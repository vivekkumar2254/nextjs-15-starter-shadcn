import { NextRequest, NextResponse } from 'next/server'
import { supabaseServer } from '@/lib/supabase/server'

// Minimal input shape for a scraped item
type ScrapedItemInput = {
  source: { name: string; base_url: string; type: 'website' | 'feed' | 'api' }
  page: { url: string; last_scraped_at?: string | null }
  item: {
    title: string
    slug?: string | null
    summary?: string | null
    content?: string | null
    author?: string | null
    published_at?: string | null
    url: string
    hash?: string | null
  }
  media?: Array<{ type: 'image' | 'video' | 'file'; url: string; alt?: string | null }>
}

export async function POST(req: NextRequest) {
  const payload = (await req.json()) as ScrapedItemInput
  const supabase = supabaseServer

  // Upsert source
  const { data: sourceRow, error: sourceErr } = await supabase
    .from('sources')
    .upsert(
      [
        {
          name: payload.source.name,
          base_url: payload.source.base_url,
          type: payload.source.type,
        },
      ],
      { onConflict: 'base_url' }
    )
    .select('*')
    .single()

  if (sourceErr) return NextResponse.json({ error: sourceErr.message }, { status: 500 })

  // Upsert page
  const { data: pageRow, error: pageErr } = await supabase
    .from('pages')
    .upsert(
      [
        {
          source_id: sourceRow.id,
          url: payload.page.url,
          last_scraped_at: payload.page.last_scraped_at ?? null,
        },
      ],
      { onConflict: 'url' }
    )
    .select('*')
    .single()

  if (pageErr) return NextResponse.json({ error: pageErr.message }, { status: 500 })

  // Insert item (unique on URL)
  const { data: itemRow, error: itemErr } = await supabase
    .from('items')
    .upsert(
      [
        {
          page_id: pageRow.id,
          title: payload.item.title,
          slug: payload.item.slug ?? null,
          summary: payload.item.summary ?? null,
          content: payload.item.content ?? null,
          author: payload.item.author ?? null,
          published_at: payload.item.published_at ?? null,
          url: payload.item.url,
          hash: payload.item.hash ?? null,
        },
      ],
      { onConflict: 'url' }
    )
    .select('*')
    .single()

  if (itemErr) return NextResponse.json({ error: itemErr.message }, { status: 500 })

  // Insert media (no upsert; duplicates allowed per url+item)
  if (payload.media?.length) {
    const { error: mediaErr } = await supabase.from('media').insert(
      payload.media.map((m) => ({ item_id: itemRow.id, type: m.type, url: m.url, alt: m.alt ?? null }))
    )
    if (mediaErr) return NextResponse.json({ error: mediaErr.message }, { status: 500 })
  }

  return NextResponse.json({ id: itemRow.id }, { status: 201 })
}


