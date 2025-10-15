import { createClient } from '@supabase/supabase-js'

// Public client: use ONLY public keys in the browser
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  // Intentionally throw to surface misconfiguration early during dev
  throw new Error('Missing NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY')
}

export const supabaseBrowser = createClient(supabaseUrl, supabaseAnonKey)


