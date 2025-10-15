import { NextRequest, NextResponse } from 'next/server'
import { supabaseServer } from '@/lib/supabase/server'

export async function GET(req: NextRequest) {
  const supabase = supabaseServer
  const { searchParams } = new URL(req.url)
  const q = searchParams.get('q')?.trim()
  const limit = Math.min(Number(searchParams.get('limit') ?? 50), 200)

  let query = supabase
    .from('permission_groups_rbp')
    .select('group_id, group_external_id, group_name, group_leader, active_member_count, all_member_count, last_modified')
    .order('last_modified', { ascending: false })
    .limit(limit)

  if (q) {
    // Simple ilike filter on group name or leader
    query = query.ilike('group_name', `%${q}%`)
  }

  const { data, error } = await query
  if (error) return NextResponse.json({ error: error.message }, { status: 500 })
  return NextResponse.json({ groups: data })
}


