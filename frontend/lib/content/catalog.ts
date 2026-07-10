import { fetchBackendJson } from '@/lib/api/backend'
import type { TeamWithStats } from '@/lib/types'

interface SelectionCatalogEntry {
  id: number
  nome: string
  continente: string | null
  grupo: string | null
  ranking_fifa: number | null
}

function catalogEntryToTeam(entry: SelectionCatalogEntry): TeamWithStats {
  return {
    id: entry.id,
    name: entry.nome,
    country: entry.continente,
    group_name: entry.grupo,
    flag_url: null,
    updated_at: null,
    team_stats: null,
  }
}

export async function loadSelectionCatalog(): Promise<TeamWithStats[]> {
  const response = await fetchBackendJson<{ total: number; selecoes: SelectionCatalogEntry[] }>(
    '/api/selecoes'
  )
  return response.selecoes.map(catalogEntryToTeam)
}
