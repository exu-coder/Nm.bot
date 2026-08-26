import http from 'node:http';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createClient } from '@supabase/supabase-js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PORT = Number(process.env.PORT || 3000);
const ADMIN_EMAIL = String(process.env.ADMIN_EMAIL || '').trim().toLowerCase();
const ADMIN_PASSWORD = String(process.env.ADMIN_PASSWORD || '');
const SUPABASE_URL = String(process.env.SUPABASE_URL || '');
const SUPABASE_SERVICE_ROLE_KEY = String(process.env.SUPABASE_SERVICE_ROLE_KEY || '');
const SESSION_TTL = 8 * 60 * 60 * 1000;

if (!ADMIN_EMAIL || !ADMIN_PASSWORD || !SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  console.error('Missing ADMIN_EMAIL, ADMIN_PASSWORD, SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY');
  process.exit(1);
}
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, { auth: { persistSession:false, autoRefreshToken:false } });
const sessionSecret = crypto.createHash('sha256').update(`${ADMIN_EMAIL}:${ADMIN_PASSWORD}`).digest();

function sign(value) { return crypto.createHmac('sha256', sessionSecret).update(value).digest('base64url'); }
function makeSession() { const value = `${Date.now()}`; return `${value}.${sign(value)}`; }
function validSession(req) {
  const cookie = req.headers.cookie || '';
  const match = cookie.match(/(?:^|; )farabi_admin=([^;]+)/);
  if (!match) return false;
  const [ts, sig] = decodeURIComponent(match[1]).split('.');
  if (!ts || !sig || Date.now() - Number(ts) > SESSION_TTL) return false;
  const expected = sign(ts);
  return crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expected));
}
function json(res, status, body, headers={}) {
  res.writeHead(status, {'Content-Type':'application/json; charset=utf-8', 'Cache-Control':'no-store', ...headers});
  res.end(JSON.stringify(body));
}
function readJson(req) { return new Promise((resolve,reject)=>{ let data=''; req.on('data', c=>{data+=c; if(data.length>1e6) req.destroy();}); req.on('end',()=>{try{resolve(data?JSON.parse(data):{});}catch(e){reject(e);}}); req.on('error',reject); }); }
function requireAdmin(req,res) { if (!validSession(req)) { json(res,401,{error:'Unauthorized'}); return false; } return true; }

async function api(req,res,url) {
  if (url.pathname === '/api/login' && req.method === 'POST') {
    try {
      const body = await readJson(req);
      const email = String(body.email || '').trim().toLowerCase();
      const password = String(body.password || '');
      const ok = email === ADMIN_EMAIL && password === ADMIN_PASSWORD;
      if (!ok) return json(res,401,{error:'Invalid login credentials.'});
      return json(res,200,{ok:true,email:ADMIN_EMAIL},{'Set-Cookie':`farabi_admin=${encodeURIComponent(makeSession())}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=${SESSION_TTL/1000}`});
    } catch { return json(res,400,{error:'Invalid request.'}); }
  }
  if (url.pathname === '/api/logout' && req.method === 'POST') return json(res,200,{ok:true},{'Set-Cookie':'farabi_admin=; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=0'});
  if (url.pathname === '/api/applications' && req.method === 'GET') {
    if (!requireAdmin(req,res)) return;
    const {data,error}=await supabase.from('applications').select('*').order('created_at',{ascending:false});
    if(error) return json(res,500,{error:error.message});
    return json(res,200,{data});
  }
  const match=url.pathname.match(/^\/api\/applications\/([^/]+)$/);
  if (match && req.method === 'PATCH') {
    if (!requireAdmin(req,res)) return;
    let body; try { body=await readJson(req); } catch { return json(res,400,{error:'Invalid request.'}); }
    const status=String(body.status||'');
    if(!['pending','approved','rejected'].includes(status)) return json(res,400,{error:'Invalid status.'});
    const {data,error}=await supabase.from('applications').update({status}).eq('id',match[1]).select('id,status').maybeSingle();
    if(error) return json(res,500,{error:error.message});
    if(!data) return json(res,404,{error:'Application not found.'});
    return json(res,200,{data});
  }
  return json(res,404,{error:'Not found'});
}

const server=http.createServer(async(req,res)=>{
  const url=new URL(req.url,`http://${req.headers.host||'localhost'}`);
  if(url.pathname.startsWith('/api/')) return api(req,res,url).catch(e=>{console.error(e); if(!res.headersSent) json(res,500,{error:'Server error'});});
  let pathname=decodeURIComponent(url.pathname);
  if(pathname==='/'||pathname==='') pathname='/index.html';
  const file=path.resolve(__dirname,'dist',`.${pathname}`);
  if(!file.startsWith(path.resolve(__dirname,'dist'))) return res.writeHead(403).end();
  fs.readFile(file,(err,data)=>{ if(err) return fs.readFile(path.join(__dirname,'dist','index.html'),(e,d)=>{if(e) return res.writeHead(404).end(); res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});res.end(d);}); const ext=path.extname(file); const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml'}; res.writeHead(200,{'Content-Type':types[ext]||'application/octet-stream'});res.end(data); });
});
server.listen(PORT,'0.0.0.0',()=>console.log(`Farabi admin listening on ${PORT}`));
