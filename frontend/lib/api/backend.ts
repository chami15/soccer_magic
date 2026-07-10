import type {
  HeadToHead,
  MatchDetail,
  PlayersResponse,
  PowerRanking,
  SelectionMatchSummary,
  SelectionStats,
  UpcomingMatch,
  TicketAnalysis,
} from './types'

const DEFAULT_API_URL = 'http://localhost:8000'

function getApiBaseUrl() {
  return process.env.NEXT_PUBLIC_API_URL || DEFAULT_API_URL
}

function buildUrl(pathname: string) {
  return new URL(pathname, getApiBaseUrl())
}

async function readErrorMessage(response: Response) {
  const raw = await response.text()
  return raw || response.statusText || `Request failed with ${response.status}`
}

export async function fetchBackendJson<T>(pathname: string, init?: RequestInit): Promise<T> {
  const response = await fetch(buildUrl(pathname), {
    ...init,
    headers: {
      Accept: 'application/json',
      ...(init?.headers ?? {}),
    },
    cache: 'no-store',
  })

  if (!response.ok) {
    throw new Error(await readErrorMessage(response))
  }

  return (await response.json()) as T
}

export async function loadSelectionStats(selectionId: number) {
  return fetchBackendJson<SelectionStats>(`/api/selecoes/${selectionId}/estatisticas`)
}

export async function loadSelectionMatches(selectionId: number) {
  const response = await fetchBackendJson<{ selecao_id: number; total: number; partidas: SelectionMatchSummary[] }>(
    `/api/partidas/selecao/${selectionId}`
  )
  return response
}

export async function loadUpcomingMatches(limit = 20) {
  const suffix = limit ? `?limit=${limit}` : ''
  return fetchBackendJson<{ total: number; partidas: UpcomingMatch[] }>(`/api/calendario/proximas${suffix}`)
}

export async function loadMatchDetails(matchId: number) {
  return fetchBackendJson<MatchDetail>(`/api/partidas/${matchId}`)
}

export async function loadPowerRanking(selectionId: number) {
  return fetchBackendJson<PowerRanking>(`/api/power-ranking/${selectionId}`)
}

export async function loadPlayers(selectionId: number) {
  return fetchBackendJson<PlayersResponse>(`/api/jogadores/selecao/${selectionId}`)
}

export async function loadHeadToHead(selectionAId: number, selectionBId: number) {
  return fetchBackendJson<HeadToHead>(`/api/h2h/${selectionAId}/${selectionBId}`)
}

export async function loadTicketAnalysis(matchId: number) {
  return fetchBackendJson<TicketAnalysis>(`/api/agente/analise/${matchId}`)
}
