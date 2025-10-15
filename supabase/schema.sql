-- Sources: origin of scraped content (site, feed, api)
create table if not exists public.sources (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  base_url text not null,
  type text not null check (type in ('website','feed','api')),
  created_at timestamptz not null default now(),
  unique (base_url)
);

-- Pages: specific pages we scrape
create table if not exists public.pages (
  id uuid primary key default gen_random_uuid(),
  source_id uuid not null references public.sources(id) on delete cascade,
  url text not null,
  last_scraped_at timestamptz,
  created_at timestamptz not null default now(),
  unique (url)
);

-- Items: normalized scraped items (articles/products/etc.)
create table if not exists public.items (
  id uuid primary key default gen_random_uuid(),
  page_id uuid not null references public.pages(id) on delete cascade,
  title text not null,
  slug text,
  summary text,
  content text,
  author text,
  published_at timestamptz,
  url text not null,
  hash text, -- content hash to dedupe
  created_at timestamptz not null default now(),
  unique (url)
);

-- Media: images/videos/files associated with items
create table if not exists public.media (
  id uuid primary key default gen_random_uuid(),
  item_id uuid not null references public.items(id) on delete cascade,
  type text not null check (type in ('image','video','file')),
  url text not null,
  alt text,
  created_at timestamptz not null default now()
);

-- Indexes to speed up lookups
create index if not exists idx_pages_source on public.pages(source_id);
create index if not exists idx_items_page on public.items(page_id);
create index if not exists idx_media_item on public.media(item_id);

-- RLS: enabled. Policies are defined separately in policies.sql
alter table public.sources enable row level security;
alter table public.pages enable row level security;
alter table public.items enable row level security;
alter table public.media enable row level security;

-- =============================================
-- Permission Groups (scraped) schema
-- =============================================

-- Ensure pgcrypto for gen_random_uuid (run once if missing)
create extension if not exists "pgcrypto";

-- High-level overview document (optional)
create table if not exists public.permission_overviews (
  id uuid primary key default gen_random_uuid(),
  total_count integer,
  sharable boolean,
  attributes jsonb,
  created_at timestamptz not null default now()
);

-- Master list of groups from groupList and group_details
create table if not exists public.permission_groups (
  id uuid primary key default gen_random_uuid(),
  group_id integer not null,
  group_name text,
  group_leader text,
  group_flag integer,
  group_type text,
  active_member_count integer,
  all_member_count integer,
  last_modified date,
  last_modified_utc date,
  lms_role_id text,
  shared boolean,
  show boolean,
  static_group boolean,
  sub_domain text,
  user_type text,
  version_id text,
  visibility_type text,
  attributes jsonb,        -- e.g., { GroupVO: { ... } }
  ui_state jsonb,          -- raw UIState if you want to keep the original structure
  created_at timestamptz not null default now(),
  unique (group_id)
);

-- Each includeGroups entry under UIState gets a row here
create table if not exists public.include_groups (
  id uuid primary key default gen_random_uuid(),
  permission_group_id uuid not null references public.permission_groups(id) on delete cascade,
  set_index integer not null,
  created_at timestamptz not null default now()
);

-- Each expression inside includeGroups[n].filters[m].uiBasicFilter.expressions gets a row here
create table if not exists public.include_group_filters (
  id uuid primary key default gen_random_uuid(),
  include_group_id uuid not null references public.include_groups(id) on delete cascade,
  filter_index integer not null default 0,    -- m in filters[m]
  expr_index integer not null default 0,      -- index within expressions
  field_id text,                              -- uiBasicFilter.fieldId.internal
  operator text,                              -- e.g., 'eq'
  value_display text,                         -- expressions[x].filterValues[y].display
  value_internal text,                        -- expressions[x].filterValues[y].internal
  created_at timestamptz not null default now()
);

-- Helpful indexes
create index if not exists idx_permission_groups_group_id on public.permission_groups(group_id);
create index if not exists idx_include_groups_group on public.include_groups(permission_group_id);
create index if not exists idx_include_group_filters_include on public.include_group_filters(include_group_id);
create index if not exists idx_include_group_filters_field on public.include_group_filters(field_id);

-- Enable RLS; keep policies managed in policies.sql
alter table public.permission_overviews enable row level security;
alter table public.permission_groups enable row level security;
alter table public.include_groups enable row level security;
alter table public.include_group_filters enable row level security;



