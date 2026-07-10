import { NextResponse } from 'next/server'
import { fetchBackendJson } from '@/lib/api/backend'

interface Params {
  params: { partidaId: string }
}

export async function GET(_request: Request, { params }: Params) {
  const partidaId = Number(params.partidaId)

  if (Number.isNaN(partidaId)) {
    return NextResponse.json({ error: 'partidaId invalido' }, { status: 400 })
  }

  try {
    const payload = await fetchBackendJson(`/api/agente/analise/${partidaId}`)
    return NextResponse.json(payload)
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Erro ao consultar analise'
    return NextResponse.json({ error: message }, { status: 500 })
  }
}
