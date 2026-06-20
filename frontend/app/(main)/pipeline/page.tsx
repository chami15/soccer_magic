import { createSupabaseServer } from '@/lib/supabase'
import { PipelineStatus } from '@/components/PipelineStatus'

export const revalidate = 60

export default async function PipelinePage() {
  const supabase = createSupabaseServer()
  const { data: runs } = await supabase
    .from('pipeline_runs')
    .select('*')
    .order('started_at', { ascending: false })
    .limit(10)

  return <PipelineStatus runs={runs ?? []} />
}
