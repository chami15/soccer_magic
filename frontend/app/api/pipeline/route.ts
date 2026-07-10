import { NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'
import path from 'path'

const execAsync = promisify(exec)

export async function POST() {
  try {
    const backendDir = path.join(process.cwd(), '..', 'backend')
    const { stdout, stderr } = await execAsync('python pipeline_diario.py', {
      cwd: backendDir,
      env: { ...process.env },
      timeout: 600_000, // 10 min
    })
    return NextResponse.json({ success: true, log: stdout + (stderr ? `\nSTDERR:\n${stderr}` : '') })
  } catch (error: any) {
    return NextResponse.json(
      { success: false, error: error?.message ?? String(error) },
      { status: 500 }
    )
  }
}
