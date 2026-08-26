-- Farabi IT Center: optional data-only RPCs for the demo admin UI.
-- The login credentials are NOT stored in Supabase.
-- IMPORTANT: a client-side Vite demo login is not real authentication.

create or replace function public.demo_admin_get_applications()
returns setof public.applications
language sql
security definer
set search_path = public
as $$
  select * from public.applications order by created_at desc;
$$;

create or replace function public.demo_admin_update_status(p_id uuid, p_status text)
returns boolean
language plpgsql
security definer
set search_path = public
as $$
begin
  if p_status not in ('pending','approved','rejected') then
    raise exception 'Invalid status';
  end if;
  update public.applications set status = p_status where id = p_id;
  return found;
end;
$$;

grant execute on function public.demo_admin_get_applications() to anon;
grant execute on function public.demo_admin_update_status(uuid,text) to anon;
