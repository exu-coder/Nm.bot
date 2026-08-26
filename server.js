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
const SUPABASE_ANON_KEY = String(process.env.SUPABASE_ANON_KEY || '');

if (!ADMIN_EMAIL || !ADMIN_PASSWORD || !SUPABASE_URL || !SUPABASE_ANON_KEY) {
  console.error('Missing ADMIN_EMAIL, ADMIN_PASSWORD, SUPABASE_URL or SUPABASE_ANON_KEY');
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: { persistSession:false, autoRefreshToken:false }
});

function json(res,status,body,headers={}) {
  res.writeHead(status,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store',...headers});
  res.end(JSON.stringify(body));
}
function readJson(req) {
  return new Promise((resolve,reject)=>{
    let data='';
    req.on('data',c=>{data+=c;if(data.length>1e6) req.destroy();});
    req.on('end',()=>{try{resolve(data?JSON.parse(data):{});}catch(e){reject(e);}});
    req.on('error',reject);
  });
}

async function api(req,res,url) {
  if(url.pathname==='/api/applications'&&req.method==='GET'){
    const {data,error}=await supabase.rpc('demo_admin_get_applications',{p_email:ADMIN_EMAIL,p_password:ADMIN_PASSWORD});
    if(error)return json(res,500,{error:error.message});
    return json(res,200,{data:data||[]});
  }

  const match=url.pathname.match(/^\/api\/applications\/([^/]+)$/);
  if(match&&req.method==='PATCH'){
    let body;
    try{body=await readJson(req);}catch{return json(res,400,{error:'Invalid request.'});}
    const status=String(body.status||'');
    if(!['pending','approved','rejected'].includes(status))return json(res,400,{error:'Invalid status.'});
    const {data,error}=await supabase.rpc('demo_admin_update_status',{p_email:ADMIN_EMAIL,p_password:ADMIN_PASSWORD,p_id:match[1],p_status:status});
    if(error)return json(res,500,{error:error.message});
    if(data!==true)return json(res,400,{error:'Application was not updated.'});
    return json(res,200,{data:true});
  }

  return json(res,404,{error:'Not found'});
}

const server=http.createServer(async(req,res)=>{
  const url=new URL(req.url,`http://${req.headers.host||'localhost'}`);
  if(url.pathname.startsWith('/api/'))return api(req,res,url).catch(e=>{console.error(e);if(!res.headersSent)json(res,500,{error:'Server error'});});
  let pathname=decodeURIComponent(url.pathname);
  if(pathname==='/'||pathname==='')pathname='/index.html';
  const dist=path.resolve(__dirname,'dist');
  const file=path.resolve(dist,`.${pathname}`);
  if(!file.startsWith(dist))return res.writeHead(403).end();
  fs.readFile(file,(err,data)=>{
    if(err)return fs.readFile(path.join(dist,'index.html'),(e,d)=>{
      if(e)return res.writeHead(404).end();
      res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});res.end(d);
    });
    const ext=path.extname(file);
    const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml'};
    res.writeHead(200,{'Content-Type':types[ext]||'application/octet-stream'});res.end(data);
  });
});
server.listen(PORT,'0.0.0.0',()=>console.log(`Farabi admin listening on ${PORT}`));
