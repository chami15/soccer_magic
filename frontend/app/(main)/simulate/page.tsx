import { loadSelectionCatalog } from '@/lib/content/catalog'
import { CompareBoard } from '@/components/compare/CompareBoard'

export const revalidate = 300

export default async function SimulatePage() {
  const teams = await loadSelectionCatalog()

  return <CompareBoard teams={teams} />
}
