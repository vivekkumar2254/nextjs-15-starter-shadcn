-- =====================================================
-- Permission Management System Schema (Supabase/PostgreSQL)
-- Notes:
-- - Uses SERIAL and TIMESTAMP compatible with Supabase
-- - Avoids IF NOT EXISTS on CREATE POLICY (use SQL editor to run once)
-- - No RLS policies here; add in policies.sql if client reads are needed
-- =====================================================

create extension if not exists "pgcrypto";

-- User Types
create table if not exists public.user_types (
  user_type_id serial primary key,
  user_type_name varchar(100) unique not null,
  description text,
  created_at timestamp default current_timestamp
);

-- Users/Employees
create table if not exists public.users (
  user_id serial primary key,
  username varchar(100) unique not null,
  display_name varchar(255),
  employee_id varchar(50),
  user_type_id int references public.user_types(user_type_id),
  is_active boolean default true,
  created_at timestamp default current_timestamp,
  updated_at timestamp default current_timestamp
);

-- Update trigger
create or replace function public.update_updated_at_column()
returns trigger as $$
begin
  new.updated_at = current_timestamp;
  return new;
end;
$$ language plpgsql;

drop trigger if exists update_users_updated_at on public.users;
create trigger update_users_updated_at before update on public.users
for each row execute function public.update_updated_at_column();

-- Roles
create table if not exists public.permission_roles (
  role_id serial primary key,
  role_external_id varchar(50) unique,
  role_name varchar(255) not null,
  user_type_id int references public.user_types(user_type_id),
  description text,
  status varchar(100),
  is_active boolean default true,
  is_rbp_only boolean default false,
  last_modified date,
  created_at timestamp default current_timestamp,
  updated_at timestamp default current_timestamp
);

create index if not exists idx_role_name on public.permission_roles(role_name);
create index if not exists idx_status on public.permission_roles(status);
create index if not exists idx_last_modified on public.permission_roles(last_modified);

drop trigger if exists update_permission_roles_updated_at on public.permission_roles;
create trigger update_permission_roles_updated_at before update on public.permission_roles
for each row execute function public.update_updated_at_column();

-- Groups
create table if not exists public.permission_groups_rbp (
  group_id serial primary key,
  group_external_id int unique,
  group_name varchar(255) not null,
  group_leader varchar(255),
  group_type varchar(100),
  is_static boolean default false,
  is_dynamic boolean default true,
  is_rbp_only boolean default false,
  group_flag int,
  visibility_type varchar(50),
  is_shared boolean default false,
  is_freeze boolean default false,
  active_member_count int default 0,
  all_member_count int default 0,
  last_modified date,
  last_modified_utc timestamp,
  created_at timestamp default current_timestamp,
  updated_at timestamp default current_timestamp
);

create index if not exists idx_group_name on public.permission_groups_rbp(group_name);
create index if not exists idx_group_leader on public.permission_groups_rbp(group_leader);
create index if not exists idx_group_last_modified on public.permission_groups_rbp(last_modified);

drop trigger if exists update_permission_groups_updated_at on public.permission_groups_rbp;
create trigger update_permission_groups_updated_at before update on public.permission_groups_rbp
for each row execute function public.update_updated_at_column();

-- Group membership
create table if not exists public.group_memberships (
  membership_id serial primary key,
  group_id int not null references public.permission_groups_rbp(group_id) on delete cascade,
  user_id int not null references public.users(user_id) on delete cascade,
  is_active boolean default true,
  joined_date timestamp default current_timestamp,
  removed_date timestamp null,
  unique (group_id, user_id)
);

create index if not exists idx_group_active on public.group_memberships(group_id, is_active);
create index if not exists idx_user_active on public.group_memberships(user_id, is_active);

-- Role assignments
create table if not exists public.role_assignments (
  assignment_id serial primary key,
  role_id int not null references public.permission_roles(role_id) on delete cascade,
  user_id int references public.users(user_id) on delete cascade,
  group_id int references public.permission_groups_rbp(group_id) on delete cascade,
  assigned_date timestamp default current_timestamp,
  expiry_date timestamp null,
  is_active boolean default true,
  assigned_by int references public.users(user_id),
  check ((user_id is not null and group_id is null) or (user_id is null and group_id is not null))
);

create index if not exists idx_role_user on public.role_assignments(role_id, user_id);
create index if not exists idx_role_group on public.role_assignments(role_id, group_id);
create index if not exists idx_active on public.role_assignments(is_active);

-- Filter types (lookup)
create table if not exists public.filter_types (
  filter_type_id serial primary key,
  filter_type_code varchar(50) unique not null,
  filter_type_name varchar(100) not null,
  description text
);

-- Group filter criteria (flattened)
create table if not exists public.group_filter_criteria (
  filter_id serial primary key,
  group_id int not null references public.permission_groups_rbp(group_id) on delete cascade,
  filter_index int default 0,
  filter_group_index int default 0,
  field_id varchar(100) not null,
  field_display_name varchar(255),
  operator varchar(20) not null,
  filter_type varchar(50),
  is_include_filter boolean default true,
  created_at timestamp default current_timestamp
);

create index if not exists idx_group_field on public.group_filter_criteria(group_id, field_id);
create index if not exists idx_filter_type on public.group_filter_criteria(filter_type);

-- Filter values
create table if not exists public.filter_values (
  filter_value_id serial primary key,
  filter_id int not null references public.group_filter_criteria(filter_id) on delete cascade,
  display_value varchar(500),
  internal_value varchar(500),
  value_order int default 0
);

create index if not exists idx_filter_display on public.filter_values(filter_id, display_value);
create index if not exists idx_filter_internal on public.filter_values(filter_id, internal_value);

-- Permissions catalog
create table if not exists public.permissions (
  permission_id serial primary key,
  permission_code varchar(100) unique not null,
  permission_name varchar(255) not null,
  permission_category varchar(100),
  description text,
  is_active boolean default true,
  created_at timestamp default current_timestamp
);

-- Role-permission mapping
create table if not exists public.role_permissions (
  role_permission_id serial primary key,
  role_id int not null references public.permission_roles(role_id) on delete cascade,
  permission_id int not null references public.permissions(permission_id) on delete cascade,
  grant_type varchar(10) default 'ALLOW' check (grant_type in ('ALLOW','DENY')),
  created_at timestamp default current_timestamp,
  unique (role_id, permission_id)
);

create index if not exists idx_role_grant on public.role_permissions(role_id, grant_type);

-- Audit log
create table if not exists public.audit_log (
  audit_id bigserial primary key,
  entity_type varchar(20) not null check (entity_type in ('USER','ROLE','GROUP','ASSIGNMENT','PERMISSION')),
  entity_id int not null,
  action_type varchar(20) not null check (action_type in ('CREATE','UPDATE','DELETE','ACTIVATE','DEACTIVATE')),
  performed_by int references public.users(user_id),
  old_value jsonb,
  new_value jsonb,
  change_description text,
  ip_address varchar(45),
  user_agent text,
  created_at timestamp default current_timestamp
);

create index if not exists idx_entity on public.audit_log(entity_type, entity_id);
create index if not exists idx_performed_by on public.audit_log(performed_by);
create index if not exists idx_created_at on public.audit_log(created_at);
create index if not exists idx_action_type on public.audit_log(action_type);

-- HRIS fields catalog
create table if not exists public.hris_fields (
  field_id serial primary key,
  field_code varchar(100) unique not null,
  field_display_name varchar(255) not null,
  field_type varchar(50),
  field_category varchar(100),
  is_filterable boolean default true,
  is_active boolean default true,
  description text
);

-- Group attributes (flexible key/value)
create table if not exists public.group_attributes (
  attribute_id serial primary key,
  group_id int not null references public.permission_groups_rbp(group_id) on delete cascade,
  attribute_key varchar(100) not null,
  attribute_value text,
  data_type varchar(50) default 'string',
  unique (group_id, attribute_key)
);

create index if not exists idx_attribute_key on public.group_attributes(attribute_key);

-- Role attributes (flexible key/value)
create table if not exists public.role_attributes (
  attribute_id serial primary key,
  role_id int not null references public.permission_roles(role_id) on delete cascade,
  attribute_key varchar(100) not null,
  attribute_value text,
  data_type varchar(50) default 'string',
  unique (role_id, attribute_key)
);

-- Seed reference data (optional)
insert into public.user_types (user_type_name, description) values
  ('Employee','Regular employee user type'),
  ('External Onboarding User','External users in onboarding process'),
  ('Contractor','Contractor user type'),
  ('Administrator','System administrator user type')
on conflict do nothing;

insert into public.filter_types (filter_type_code, filter_type_name, description) values
  ('USERNAME','Username Filter','Filter by username'),
  ('USER_DISPLAY','User Display Name','Filter by user display name'),
  ('LEGAL_ENTITY','Legal Entity','Filter by legal entity'),
  ('CITY','City','Filter by city location'),
  ('COUNTRY','Country','Filter by country'),
  ('PAY_GROUP','Pay Group','Filter by pay group'),
  ('COMPANY','Company','Filter by company code'),
  ('BENCH_STRENGTH','Bench Strength','Filter by bench strength indicator')
on conflict do nothing;

insert into public.hris_fields (field_code, field_display_name, field_type, field_category) values
  ('std_username','Username','string','User Identity'),
  ('user','User Display Name','string','User Identity'),
  ('std_custom05','Legal Entity','string','Organization'),
  ('std_city','City','string','Location'),
  ('std_country','Country','string','Location'),
  ('hris_compInfo$pay-group','Pay Group','string','Compensation'),
  ('hris_jobInfo$company','Company','string','Organization'),
  ('std_benchStrength','Bench Strength','string','Development')
on conflict do nothing;


