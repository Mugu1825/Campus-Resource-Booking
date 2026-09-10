// Auto-detect API base:
// When served via Docker (port 3000) or Render production, Nginx reverse-proxies '/api'
// When running standalone 'python3 -m http.server 8080' during local dev, routes to port 5000
const API_BASE = (window.location.hostname === 'localhost' && window.location.port === '8080')
  ? 'http://localhost:5000/api'
  : '/api';

function getToken() { return localStorage.getItem('crbs_token'); }
function getRole() { return localStorage.getItem('crbs_role'); }
function getUserId() { return localStorage.getItem('crbs_user_id'); }
function getUserName() { return localStorage.getItem('crbs_name'); }

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  
  try {
    const res = await fetch(API_BASE + path, { ...options, headers });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw { status: res.status, message: data.error || data.message || 'Request failed' };
    
    // Auto-unwrap lists if backend nested them under a top-level collection key
    if (data && typeof data === 'object' && !Array.isArray(data)) {
      if (Array.isArray(data.resources)) return data.resources;
      if (Array.isArray(data.bookings)) return data.bookings;
      if (Array.isArray(data.users)) return data.users;
    }
    return data;
  } catch (err) {
    if (err.status) throw err;
    throw { status: 0, message: 'Network error or server unreachable' };
  }
}

// Convenience wrappers
const api = {
  get: (path) => apiFetch(path),
  post: (path, body) => apiFetch(path, { method: 'POST', body: JSON.stringify(body) }),
  put: (path, body) => apiFetch(path, { method: 'PUT', body: JSON.stringify(body) }),
  patch: (path, body) => apiFetch(path, { method: 'PATCH', body: body ? JSON.stringify(body) : undefined }),
  delete: (path) => apiFetch(path, { method: 'DELETE' }),
};

function logout() {
  ['crbs_token','crbs_role','crbs_user_id','crbs_name','crbs_dept'].forEach(k => localStorage.removeItem(k));
  window.location.href = 'login.html';
}

function requireAuth(allowedRoles) {
  const token = getToken();
  const role = getRole();
  if (!token || !role) { window.location.href = 'login.html'; return false; }
  if (allowedRoles && !allowedRoles.includes(role)) {
    alert('Access denied');
    window.location.href = 'login.html';
    return false;
  }
  return true;
}

function showAlert(containerId, message, type = 'error') {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
  setTimeout(() => { el.innerHTML = ''; }, 4000);
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('en-IN', {day:'2-digit',month:'short',year:'numeric'});
}

function badgeHtml(status) {
  if (!status) return '';
  return `<span class="badge badge-${status.toLowerCase()}">${status.charAt(0).toUpperCase()+status.slice(1)}</span>`;
}

function tierBadgeHtml(tier) {
  if (!tier) return '';
  return `<span class="badge badge-${tier.toLowerCase()}">${tier.charAt(0).toUpperCase()+tier.slice(1)}</span>`;
}

const TIME_SLOTS = [
  "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00"
];

function setupModal(modalId, btnId = null, closeBtnClass = 'modal-close') {
  const modal = document.getElementById(modalId);
  if (!modal) return;
  
  if (btnId) {
    const btn = document.getElementById(btnId);
    if (btn) btn.addEventListener('click', () => modal.classList.add('active'));
  }
  
  const closeBtns = modal.querySelectorAll('.' + closeBtnClass);
  closeBtns.forEach(btn => btn.addEventListener('click', () => modal.classList.remove('active')));
  
  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.classList.remove('active');
  });
}
