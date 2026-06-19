"""
Soccer Magic — Sliding Window Algorithm (§7.2 SPECv2)
Isolado e 100% testável sem dependências externas.
"""
from dataclasses import dataclass

# Sofascore FIFA World Cup tournament ID (confirmar via DevTools na primeira execução)
WC_TOURNAMENT_ID = 16


@dataclass
class WindowResult:
    window: list[dict]
    data_quality: str  # 'complete' | 'partial' | 'insufficient'
    copa_count: int
    friendly_count: int


def build_window(matches_raw: list[dict], wc_tournament_id: int = WC_TOURNAMENT_ID) -> WindowResult:
    """
    Implementação exata do §7.2 do SPECv2.

    Recebe lista de eventos Sofascore com status.type == 'finished'.
    Copa (wc_tournament_id) entra primeiro; amistosos preenchem as vagas restantes até 5.
    Ordena por startTimestamp DESC dentro de cada grupo.
    """
    def _tournament_id(m: dict) -> int | None:
        return m.get("tournament", {}).get("uniqueTournament", {}).get("id")

    copa_matches = sorted(
        [m for m in matches_raw if _tournament_id(m) == wc_tournament_id],
        key=lambda m: m.get("startTimestamp", 0),
        reverse=True,
    )
    friendly_matches = sorted(
        [m for m in matches_raw if _tournament_id(m) != wc_tournament_id],
        key=lambda m: m.get("startTimestamp", 0),
        reverse=True,
    )

    window: list[dict] = []
    for match in copa_matches:
        if len(window) < 5:
            window.append(match)
    for match in friendly_matches:
        if len(window) < 5:
            window.append(match)

    n = len(window)
    if n < 3:
        data_quality = "insufficient"
    elif n < 5:
        data_quality = "partial"
    else:
        data_quality = "complete"

    copa_count = sum(1 for m in window if _tournament_id(m) == wc_tournament_id)
    friendly_count = n - copa_count

    return WindowResult(window, data_quality, copa_count, friendly_count)
