-- Farabi IT Center admin RPCs.
-- Login credentials are stored in public.demo_admin_credentials.
-- The Node server authenticates the admin session and also passes these
-- credentials to the protected RPCs before reading/updating applications.

create or replace function public.demo_admin_login(p_email text, p_password text)
returns boolean
language sql
security definer
set search_path = public, extensions
as $$
  select exists (
    select 1
    from public.demo_admin_credentials
    where lower(email) = lower(trim(p_email))
      and password_hash = crypt(p_password, password_hash)
  );
$$;

create or replace function public.demo_admin_get_applications(p_email text, p_password text)
returns setof public.applications
language plpgsql
security definer
set search_path = public, extensions
as $$
begin
  if not public.demo_admin_login(p_email, p_password) then
    raise exception 'Invalid admin credentials';
  end if;
  return query
    select * from public.applications order by created_at desc;
end;
$$;

create or replace function public.demo_admin_update_status(
  p_email text,
  p_password text,
  p_id uuid,
  p_status text
)
returns boolean
language plpgsql
security definer
set search_path = public, extensions
as $$
begin
  if not public.demo_admin_login(p_email, p_password) then
    raise exception 'Invalid admin credentials';
  end if;
  if p_status not in ('pending','approved','rejected') then
    raise exception 'Invalid status';
  end if;
  update public.applications
     set status = p_status
   where id = p_id;
  return found;
end;
$$;

grant execute on function public.demo_admin_login(text,text) to anon;
grant execute on function public.demo_admin_get_applications(text,text) to anon;
grant execute on function public.demo_admin_update_status(text,text,uuid,text) to anon;

-- Refresh PostgREST after changing RPC signatures.
notify pgrst, 'reload schema';
