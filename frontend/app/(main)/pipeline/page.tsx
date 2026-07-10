import { loadPipelineRuns } from '@/lib/content/pipeline'
import { PipelineConsole } from '@/components/pipeline/PipelineConsole'

export const revalidate = 60

export default async function PipelinePage() {
  const result = await Promise.allSettled([loadPipelineRuns(10)])
  const runs = result[0].status === 'fulfilled' ? result[0].value : []

  return <PipelineConsole runs={runs} />
}
