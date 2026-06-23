"""
Soccer Magic — Sofascore Collector (SPECv2)
Estratégia: httpx tenta primeiro; Playwright como fallback navegando na página real
e interceptando as respostas que o próprio site faz (Cloudflare não bloqueia JS nativo).
NOTA: www.sofascore.com/api/v1 funciona; api.sofascore.com retorna 403.
"""
import atexit
import logging
import time

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://www.sofascore.com/api/v1"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Referer": "https://www.sofascore.com/",
    "Origin": "https://www.sofascore.com",
}

WC_TOURNAMENT_ID = 16

# Season ID do Mundial 2026 (confirmado via DevTools: /unique-tournament/16/season/58210/)
WC_2026_SEASON_ID = 58210

RATE_LIMIT_SLEEP = 1.5


# ─── Browser session singleton ────────────────────────────────────────────────
# Playwright é caro de iniciar; mantemos um cache de respostas ao longo do run.

_playwright_cache: dict[str, dict] = {}
_playwright_page = None
_playwright_browser = None
_playwright_instance = None


def _start_playwright_session():
    """Inicia sessão Playwright navegando na Copa 2026 para aquecer os cookies."""
    global _playwright_page, _playwright_browser, _playwright_instance

    from playwright.sync_api import sync_playwright
    try:
        from playwright_stealth import Stealth
        _stealth = Stealth()
    except Exception:
        _stealth = None

    logger.info("Iniciando sessão Playwright (Cloudflare bypass)...")
    _playwright_instance = sync_playwright().start()
    _playwright_browser = _playwright_instance.chromium.launch(headless=True)
    ctx = _playwright_browser.new_context(
        user_agent=HEADERS["User-Agent"],
        locale="pt-BR",
        timezone_id="America/Sao_Paulo",
    )
    _playwright_page = ctx.new_page()
    if _stealth:
        try:
            _stealth.apply_stealth_sync(_playwright_page)
        except Exception:
            pass

    # Interceptar TODAS as respostas da API e armazenar em cache
    def on_response(resp):
        if "sofascore.com/api/v1" in resp.url and resp.status == 200:
            try:
                body = resp.json()
                path = resp.url.split("/api/v1", 1)[-1].split("?")[0]
                _playwright_cache[path] = body
            except Exception:
                pass

    _playwright_page.on("response", on_response)

    # Navegar na página principal do torneio — dispara as principais chamadas de API
    # Usar domcontentloaded (mais rápido); networkidle pode travar indefinidamente em SPAs
    copa_url = f"https://www.sofascore.com/tournament/football/world/fifa-world-cup/{WC_TOURNAMENT_ID}"
    logger.info("Navegando em: %s", copa_url)
    try:
        _playwright_page.goto(copa_url, wait_until="domcontentloaded", timeout=40000)
    except Exception as nav_err:
        logger.warning("Navegacao Copa timeout/erro (%s) — tentando continuar", nav_err)
    _playwright_page.wait_for_timeout(8000)  # aguardar chamadas XHR do SPA
    logger.info("Sessao pronta. %d endpoints em cache.", len(_playwright_cache))


def _close_playwright_session():
    global _playwright_page, _playwright_browser, _playwright_instance
    try:
        if _playwright_browser:
            _playwright_browser.close()
        if _playwright_instance:
            _playwright_instance.stop()
    except Exception:
        pass
    _playwright_page = None
    _playwright_browser = None
    _playwright_instance = None


atexit.register(_close_playwright_session)


_FETCH_JS = """
async (url) => {
    try {
        const resp = await fetch(url, {
            credentials: 'include',
            headers: { 'Accept': 'application/json, text/plain, */*' }
        });
        if (!resp.ok) return { _error: resp.status };
        return resp.json();
    } catch(e) {
        return { _error: String(e) };
    }
}
"""


def _get_via_playwright(path: str, custom_id: str | None = None) -> dict:
    """Recupera endpoint via Playwright: cache primeiro, depois navega na página de time/evento.

    custom_id: customId Sofascore (ex: 'pUbsYUb') da partida, usado para navegação quando
    o path contém o match_id NUMÉRICO (ex: /event/{id}/statistics) — a navegação de página
    exige o customId alfanumérico, o id numérico não roteia corretamente.
    """
    global _playwright_page

    # 1. Verificar cache (populado pela navegação na página do torneio)
    if path in _playwright_cache:
        logger.debug("Cache HIT: %s", path)
        return _playwright_cache[path]

    # 2. Tentar via JS fetch dentro do browser (session cookies já ativos)
    if _playwright_page is None:
        _start_playwright_session()
        if path in _playwright_cache:
            return _playwright_cache[path]

    url = f"{BASE_URL}{path}"
    logger.info("Playwright fetch (JS context): %s", url)

    data = _playwright_page.evaluate(_FETCH_JS, url)

    if data and "_error" not in data:
        _playwright_cache[path] = data
        return data

    # 3z. goal-distributions é carregado na página de uma PARTIDA do time (seção de
    # comparação/prévia), não na página de perfil do time — confirmado via DevTools
    # (referer da chamada real era a página de um jogo do Brasil, não /team/4748).
    if "goal-distributions" in path:
        parts = path.strip("/").split("/")
        if len(parts) >= 2:
            team_id = parts[1]
            next_resp = _get_via_playwright(f"/team/{team_id}/events/next/0")
            events = next_resp.get("events", [])
            custom_id = events[0].get("customId") if events else None
            if custom_id:
                match_page = f"https://www.sofascore.com/football/match/x/{custom_id}"
                logger.info("Navegando na pagina da partida (goal-distributions): %s", match_page)
                try:
                    _playwright_page.goto(match_page, wait_until="domcontentloaded", timeout=25000)
                    _playwright_page.wait_for_timeout(6000)
                except Exception as nav_err:
                    logger.warning("Navegacao timeout/erro (%s) — continuando com cache", nav_err)
                if path in _playwright_cache:
                    return _playwright_cache[path]
                data = _playwright_page.evaluate(_FETCH_JS, url)
                if data and "_error" not in data:
                    _playwright_cache[path] = data
                    return data

    # 3. Para endpoints de time (/team/{id}/...), navegar na página do time
    if "/team/" in path:
        parts = path.strip("/").split("/")
        if len(parts) >= 2:
            team_id = parts[1]
            team_slug = _playwright_cache.get(f"__slug_{team_id}", "x")
            team_page = f"https://www.sofascore.com/team/football/{team_slug}/{team_id}"
            # statistics/overall é lazy-loaded na aba "Statistics" da página do time —
            # navegação simples na home do time não dispara esse XHR (confirmado via
            # DevTools real: URL com #tab:statistics é necessária para carregar a aba).
            if "statistics/overall" in path:
                team_page += "#tab:statistics"
            logger.info("Navegando na pagina de time: %s", team_page)
            try:
                _playwright_page.goto(team_page, wait_until="domcontentloaded", timeout=25000)
                _playwright_page.wait_for_timeout(6000)
            except Exception as nav_err:
                logger.warning("Navegacao timeout/erro (%s) — continuando com cache", nav_err)
            if path in _playwright_cache:
                return _playwright_cache[path]
            # 3a. Sessão "aquecida" pela navegação — tentar o fetch JS novamente
            data = _playwright_page.evaluate(_FETCH_JS, url)
            if data and "_error" not in data:
                _playwright_cache[path] = data
                return data

    # 3b. Para endpoints de evento (/event/{customId ou id numérico}/...), navegar na
    # página da partida. Sofascore redireciona "/football/match/{slug}/{customId}" (slug
    # é ignorado no roteamento) e dispara as mesmas chamadas de API que um usuário real
    # geraria — mas a navegação EXIGE o customId alfanumérico, não o match_id numérico
    # (ex: /event/15186856/statistics usa id numérico na API, mas a navegação para
    # /football/match/x/15186856 não roteia — precisa do customId, ex: 'pUbsYUb').
    if "/event/" in path:
        parts = path.strip("/").split("/")
        if len(parts) >= 2:
            nav_custom_id = custom_id or parts[1]
            event_page = f"https://www.sofascore.com/football/match/x/{nav_custom_id}"
            # statistics da partida também é lazy-loaded na aba "Statistics" da página do
            # evento (confirmado via DevTools real: URL real era .../match/.../{customId}
            # #id:{eventId},tab:statistics — sem o fragmento a navegação não dispara o XHR).
            if "statistics" in path and "h2h" not in path:
                event_page += "#tab:statistics"
            logger.info("Navegando na pagina do evento: %s", event_page)
            try:
                _playwright_page.goto(event_page, wait_until="domcontentloaded", timeout=25000)
                _playwright_page.wait_for_timeout(6000)
            except Exception as nav_err:
                logger.warning("Navegacao timeout/erro (%s) — continuando com cache", nav_err)
            if path in _playwright_cache:
                return _playwright_cache[path]

            # 3c. h2h/events é carregado lazy, só quando a aba "H2H" é aberta na partida —
            # a navegação simples não dispara esse XHR (confirmado via DevTools real:
            # o endpoint só aparece no Network depois do clique na aba H2H).
            if "h2h" in path:
                try:
                    _playwright_page.get_by_text("H2H", exact=True).first.click(timeout=8000)
                    _playwright_page.wait_for_timeout(5000)
                except Exception as click_err:
                    logger.warning("Nao conseguiu clicar na aba H2H (%s)", click_err)
                if path in _playwright_cache:
                    return _playwright_cache[path]

            # 3d. Sessão "aquecida" pela navegação — tentar o fetch JS novamente
            data = _playwright_page.evaluate(_FETCH_JS, url)
            if data and "_error" not in data:
                _playwright_cache[path] = data
                return data

    logger.warning("Playwright não conseguiu obter: %s (data=%s)", path, data)
    return {}


def _get(client: httpx.Client, path: str, retries: int = 3, custom_id: str | None = None) -> dict:
    """GET com rate limiting, retry e fallback Playwright.

    custom_id: customId Sofascore da partida, repassado ao fallback Playwright para
    navegação quando o path usa o match_id numérico (ex: /event/{id}/statistics).
    """
    url = f"{BASE_URL}{path}"
    for attempt in range(retries):
        try:
            time.sleep(RATE_LIMIT_SLEEP)
            resp = client.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 403 and attempt == retries - 1:
                logger.warning("403 após %d tentativas — usando Playwright para %s", retries, path)
                return _get_via_playwright(path, custom_id=custom_id)
            wait = 2 ** (attempt + 1)
            logger.warning("Tentativa %d falhou (%s): aguardando %ds", attempt + 1, exc, wait)
            time.sleep(wait)
        except httpx.RequestError as exc:
            wait = 2 ** (attempt + 1)
            logger.warning("Tentativa %d falhou (%s): aguardando %ds", attempt + 1, exc, wait)
            if attempt == retries - 1:
                raise
            time.sleep(wait)
    raise RuntimeError(f"Falha após {retries} tentativas: {url}")


def get_wc_2026_season_id(client: httpx.Client) -> int:
    return WC_2026_SEASON_ID


def get_wc_teams(client: httpx.Client, season_id: int) -> list[dict]:
    """Extrai times da tabela de classificação e armazena slugs no cache."""
    import re
    resp = _get(client, f"/unique-tournament/{WC_TOURNAMENT_ID}/season/{season_id}/standings/total")
    teams_seen: dict[int, dict] = {}
    for group in resp.get("standings", []):
        for row in group.get("rows", []):
            team = row.get("team", {})
            tid = team.get("id")
            if tid and tid not in teams_seen:
                name = team.get("name", "")
                slug = team.get("slug") or re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
                # Armazenar slug no cache para uso pelo Playwright fallback
                _playwright_cache[f"__slug_{tid}"] = slug
                teams_seen[tid] = {
                    "id": tid,
                    "name": name,
                    "country": team.get("country", {}).get("name") if team.get("country") else None,
                    "flag_url": f"https://www.sofascore.com/api/v1/team/{tid}/image",
                    "group_name": None,
                }
    return list(teams_seen.values())


def get_team_recent_matches(client: httpx.Client, team_id: int, count: int = 10) -> list[dict]:
    resp = _get(client, f"/team/{team_id}/events/last/0")
    events = resp.get("events", [])
    finished = [e for e in events if e.get("status", {}).get("type") == "finished"]
    finished.sort(key=lambda e: e.get("startTimestamp", 0), reverse=True)
    return finished[:count]


def get_match_statistics(client: httpx.Client, match_id: int, custom_id: str | None = None) -> list[dict]:
    """Retorna os grupos de estatísticas do período completo do jogo (ALL).

    A resposta real do Sofascore separa as estatísticas por período
    (ALL/1ST/2ND) — cada item de resp['statistics'] é {'period': ..., 'groups': [...]},
    não o grupo em si. Pegamos apenas o período 'ALL' (jogo completo)."""
    resp = _get(client, f"/event/{match_id}/statistics", custom_id=custom_id)
    periods = resp.get("statistics", [])
    full_match = next((p for p in periods if p.get("period") == "ALL"), None)
    return full_match.get("groups", []) if full_match else []


def get_match_incidents(client: httpx.Client, match_id: int, custom_id: str | None = None) -> list[dict]:
    resp = _get(client, f"/event/{match_id}/incidents", custom_id=custom_id)
    return resp.get("incidents", [])


def get_team_next_match(client: httpx.Client, team_id: int) -> dict | None:
    """Retorna o próximo jogo agendado de um time (espelho de get_team_recent_matches)."""
    resp = _get(client, f"/team/{team_id}/events/next/0")
    events = resp.get("events", [])
    if not events:
        return None
    events.sort(key=lambda e: e.get("startTimestamp", 0))
    return events[0]


def get_tournament_next_events(
    client: httpx.Client, tournament_id: int = WC_TOURNAMENT_ID, season_id: int = WC_2026_SEASON_ID
) -> list[dict]:
    """Retorna todos os próximos jogos do torneio numa única chamada (substitui loop por time)."""
    resp = _get(client, f"/unique-tournament/{tournament_id}/season/{season_id}/events/next/0")
    return resp.get("events", [])


def get_tournament_last_events(
    client: httpx.Client, tournament_id: int = WC_TOURNAMENT_ID, season_id: int = WC_2026_SEASON_ID
) -> list[dict]:
    """Retorna os últimos jogos encerrados do torneio numa única chamada."""
    resp = _get(client, f"/unique-tournament/{tournament_id}/season/{season_id}/events/last/0")
    return resp.get("events", [])


def get_team_goal_distributions(
    client: httpx.Client, team_id: int, tournament_id: int = WC_TOURNAMENT_ID, season_id: int = WC_2026_SEASON_ID
) -> list[dict]:
    """Retorna a distribuição de gols marcados/sofridos por intervalo de 15min (home/away/overall)."""
    resp = _get(client, f"/team/{team_id}/unique-tournament/{tournament_id}/season/{season_id}/goal-distributions")
    return resp.get("goalDistributions", [])


def get_h2h_events(client: httpx.Client, custom_id: str) -> list[dict]:
    """Retorna o histórico de confrontos diretos entre os dois times de uma partida.
    Usa o customId do evento (ex: 'VTbsYUb'), não o match_id numérico."""
    resp = _get(client, f"/event/{custom_id}/h2h/events")
    return resp.get("events", [])


def get_team_overall_statistics(
    client: httpx.Client, team_id: int, tournament_id: int = WC_TOURNAMENT_ID, season_id: int = WC_2026_SEASON_ID
) -> dict:
    """Retorna as estatísticas agregadas do time na Copa inteira (escopo: todos os jogos
    já disputados no torneio, não a janela deslizante de 5 jogos). Carregado na própria
    página de perfil do time (aba 'Statistics'), por isso usa o fallback genérico /team/."""
    resp = _get(client, f"/team/{team_id}/unique-tournament/{tournament_id}/season/{season_id}/statistics/overall")
    return resp.get("statistics", {})
