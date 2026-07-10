import { createSupabaseServer } from '@/lib/supabase'
import type { TeamWithStats } from '@/lib/types'
import type { Database } from '@/lib/database.types'

type TeamRow = Database['public']['Tables']['teams']['Row']

export async function loadSelectionCatalog(): Promise<TeamWithStats[]> {
  const supabase = createSupabaseServer()

  const { data, error } = await supabase
    .from('teams')
    .select('*, team_stats(*)')
    .order('group_name', { ascending: true })
    .order('name', { ascending: true })

  if (error) {
    throw new Error(error.message)
  }

  return (data ?? []) as TeamWithStats[]
}

export async function loadSelectionById(selectionId: number): Promise<TeamRow> {
  const supabase = createSupabaseServer()
  const { data, error } = await supabase
    .from('teams')
    .select('*')
    .eq('id', selectionId)
    .single()

  if (error || !data) {
    throw new Error(error?.message || `Selection ${selectionId} not found`)
  }

  return data
}
