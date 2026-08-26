import { createClient } from '@supabase/supabase-js';

const supabase = createClient(import.meta.env.VITE_SUPABASE_URL, import.meta.env.VITE_SUPABASE_ANON_KEY);
const ADMIN_EMAIL = atob(import.meta.env.VITE_ADMIN_EMAIL_B64 || '');
const ADMIN_PASSWORD = atob(import.meta.env.VITE_ADMIN_PASSWORD_B64 || '');
const $ = id => document.getElementById(id);
let applications = [];
let loggedIn = false;
let refreshTimer = null;
let busy = false;

const checkLogin = (email, password) => email.trim().toLowerCase() === ADMIN_EMAIL.trim().toLowerCase() && password === ADMIN_PASSWORD;

$('loginForm').addEventListener('submit', async e => {
  e.preventDefault();
  if (busy) return;
  busy = true;
  const button = e.submitter || $('loginForm').querySelector('button[type="submit"]');
  if (button) button.disabled = true;
  $('loginError').textContent = 'Checking credentials…';
  try {
    if (!checkLogin($('email').value, $('password').value)) {
      $('loginError').textContent = 'Invalid login credentials.';
      return;
    }
    loggedIn = true;
    $('password').value = '';
    $('loginError').textContent = '';
    $('loginView').hidden = true;
    $('appView').hidden = false;
    $('userEmail').textContent = ADMIN_EMAIL;
    await loadApplications();
    startAutoRefresh();
  } finally {
    busy = false;
    if (button) button.disabled = false;
  }
});

$('logout').addEventListener('click', () => {
  loggedIn = false;
  clearInterval(refreshTimer);
  applications = [];
  $('appView').hidden = true;
  $('loginView').hidden = false;
  $('email').value = '';
  $('password').value = '';
  updateStats();
  render();
});
$('refresh').addEventListener('click', () => loadApplications(true));
$('search').addEventListener('input', render);
$('statusFilter').addEventListener('change', render);
$('closeDialog').addEventListener('click', () => $('detailDialog').close());
document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible' && loggedIn) loadApplications(); });

async function loadApplications(manual = false) {
  if (!loggedIn) return;
  $('loading').style.display = 'block';
  if (manual) $('refresh').disabled = true;
  try {
    const { data, error } = await supabase.rpc('demo_admin_get_applications', {
      p_email: ADMIN_EMAIL,
      p_password: ADMIN_PASSWORD
    });
    if (error) throw error;
    applications = data || [];
    updateStats();
    render();
    $('updated').textContent = 'Live · ' + new Date().toLocaleTimeString();
  } catch (error) {
    console.error(error);
    toast(error?.message || 'Could not load applications.');
  } finally {
    $('loading').style.display = 'none';
    if (manual) $('refresh').disabled = false;
  }
}

function startAutoRefresh() {
  clearInterval(refreshTimer);
  refreshTimer = setInterval(() => { if (document.visibilityState === 'visible') loadApplications(); }, 10000);
}
function normalizeStatus(status) { return !status || status === 'new' ? 'pending' : status; }
function updateStats() {
  $('total').textContent = applications.length;
  $('pending').textContent = applications.filter(a => normalizeStatus(a.status) === 'pending').length;
  $('approved').textContent = applications.filter(a => normalizeStatus(a.status) === 'approved').length;
  $('rejected').textContent = applications.filter(a => normalizeStatus(a.status) === 'rejected').length;
}
function filtered() {
  const q = $('search').value.toLowerCase().trim();
  const s = $('statusFilter').value;
  return applications.filter(a => {
    const hay = [a.full_name,a.name,a.phone,a.email,a.course,a.message].filter(Boolean).join(' ').toLowerCase();
    return (!q || hay.includes(q)) && (s === 'all' || normalizeStatus(a.status) === s);
  });
}
function render() {
  const rows = $('rows'); rows.innerHTML = '';
  const list = filtered(); $('empty').hidden = list.length !== 0;
  for (const a of list) {
    const tr = document.createElement('tr'); const status = normalizeStatus(a.status);
    tr.innerHTML = `<td><div class="name">${esc(a.full_name||a.name||'Unknown')}</div><div class="sub">ID ${esc(String(a.id||'').slice(0,8))}</div></td><td>${esc(a.phone||'—')}<div class="sub">${esc(a.email||'')}</div></td><td>${esc(a.course||'—')}</td><td><span class="badge ${esc(status)}">${esc(status)}</span></td><td>${formatDate(a.created_at)}</td><td><div class="actions"><button class="ghost small view">View</button><button class="ghost small approve">✓</button><button class="ghost small reject">×</button></div></td>`;
    tr.querySelector('.view').onclick = () => showDetail(a);
    tr.querySelector('.approve').onclick = () => setStatus(a,'approved');
    tr.querySelector('.reject').onclick = () => setStatus(a,'rejected');
    rows.appendChild(tr);
  }
}
async function setStatus(a,status) {
  if (!loggedIn) return;
  try {
    const { data, error } = await supabase.rpc('demo_admin_update_status', {
      p_email: ADMIN_EMAIL,
      p_password: ADMIN_PASSWORD,
      p_id: a.id,
      p_status: status
    });
    if (error) throw error;
    if (data !== true) throw new Error('Application was not updated.');
    a.status = status; updateStats(); render(); toast(`Marked ${status}`);
  } catch (error) { console.error(error); toast(error?.message || 'Could not update status.'); }
}
function showDetail(a) {
  $('detailName').textContent = a.full_name || a.name || 'Application';
  $('detailBody').innerHTML = `<div class="detail-grid"><div class="detail-item"><b>PHONE</b><span>${esc(a.phone||'—')}</span></div><div class="detail-item"><b>EMAIL</b><span>${esc(a.email||'—')}</span></div><div class="detail-item"><b>COURSE</b><span>${esc(a.course||'—')}</span></div><div class="detail-item"><b>STATUS</b><span>${esc(normalizeStatus(a.status))}</span></div><div class="detail-item"><b>SUBMITTED</b><span>${formatDate(a.created_at)}</span></div><div class="detail-item message"><b>MESSAGE</b><span>${esc(a.message||'No message')}</span></div></div><div class="status-actions"><button class="primary" id="dApprove">Approve</button><button class="ghost" id="dReject">Reject</button></div>`;
  $('dApprove').onclick = async () => { await setStatus(a,'approved'); $('detailDialog').close(); };
  $('dReject').onclick = async () => { await setStatus(a,'rejected'); $('detailDialog').close(); };
  $('detailDialog').showModal();
}
function formatDate(v) { if (!v) return '—'; const d=new Date(v); return d.toLocaleDateString(undefined,{year:'numeric',month:'short',day:'numeric'})+' '+d.toLocaleTimeString(undefined,{hour:'2-digit',minute:'2-digit'}); }
function esc(v) { return String(v).replace(/[&<>\'\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','\"':'&quot;'}[c])); }
let toastTimer;
function toast(msg) { $('toast').textContent=msg; $('toast').classList.add('show'); clearTimeout(toastTimer); toastTimer=setTimeout(()=>$('toast').classList.remove('show'),3000); }
updateStats(); render();
