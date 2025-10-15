-- Anonymous: by default, deny everything. Service role bypasses RLS automatically.

-- Service role style permissive policies are not required, but if you want explicit
-- policies for non-bypass roles (e.g., "authenticated"), define them here.

-- EXPLICIT authenticated read (optional):
-- create policy authenticated_read_sources on public.sources for select to authenticated using (true);
-- create policy authenticated_read_pages   on public.pages   for select to authenticated using (true);
-- create policy authenticated_read_items   on public.items   for select to authenticated using (true);
-- create policy authenticated_read_media   on public.media   for select to authenticated using (true);

-- EXPLICIT authenticated insert (optional):
-- create policy authenticated_insert_pages on public.pages for insert to authenticated with check (true);
-- create policy authenticated_insert_items on public.items for insert to authenticated with check (true);
-- create policy authenticated_insert_media on public.media for insert to authenticated with check (true);


