import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_SERVICE_KEY", "")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL e SUPABASE_SERVICE_KEY devem estar definidos em backend/pipeline/.env")
        _client = create_client(url, key)
    return _client


def save_team(team_row: dict) -> None:
    get_client().table("teams").upsert(team_row, on_conflict="id").execute()


def save_team_stats(stats_row: dict) -> None:
    get_client().table("team_stats").upsert(stats_row, on_conflict="team_id").execute()


def save_match_log(match_rows: list[dict]) -> None:
    if not match_rows:
        return
    for row in match_rows:
        get_client().table("match_log").upsert(row, on_conflict="match_id").execute()


def get_current_window(team_id: int) -> list[int] | None:
    try:
        result = (
            get_client()
            .table("team_stats")
            .select("games_window")
            .eq("team_id", team_id)
            .maybe_single()
            .execute()
        )
        if result and result.data:
            return result.data.get("games_window")
    except Exception:
        pass
    return None


def save_pipeline_run(run: dict) -> None:
    get_client().table("pipeline_runs").insert(run).execute()
    logger.info("Pipeline run salvo: %s", run)
