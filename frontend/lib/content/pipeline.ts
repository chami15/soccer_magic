import { createSupabaseServer } from '@/lib/supabase'
import type { PipelineRun } from '@/lib/types'

export async function loadPipelineRuns(limit = 10): Promise<PipelineRun[]> {
  const supabase = createSupabaseServer()
  const { data, error } = await supabase
    .from('pipeline_runs')
    .select('*')
    .order('started_at', { ascending: false })
    .limit(limit)

  if (error) {
    throw new Error(error.message)
  }

  return (data ?? []) as PipelineRun[]
}
