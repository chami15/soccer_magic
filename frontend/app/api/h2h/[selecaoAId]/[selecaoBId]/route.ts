import { NextResponse } from 'next/server'
import { fetchBackendJson } from '@/lib/api/backend'

interface Params {
  params: { selecaoAId: string; selecaoBId: string }
}

export async function GET(_request: Request, { params }: Params) {
  const selecaoAId = Number(params.selecaoAId)
  const selecaoBId = Number(params.selecaoBId)

  if (Number.isNaN(selecaoAId) || Number.isNaN(selecaoBId)) {
    return NextResponse.json({ error: 'Ids invalidos' }, { status: 400 })
  }

  try {
    const payload = await fetchBackendJson(`/api/h2h/${selecaoAId}/${selecaoBId}`)
    return NextResponse.json(payload)
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Erro ao consultar h2h'
    return NextResponse.json({ error: message }, { status: 500 })
  }
}
