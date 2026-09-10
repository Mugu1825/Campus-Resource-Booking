requireAuth(['admin']);

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('logout-btn').addEventListener('click', logout);
  document.getElementById('user-info').innerText = `${getUserName()}\nAdmin`;
  
  // Navigation
  document.querySelectorAll('.sidebar-nav a[data-target]').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      document.querySelectorAll('.sidebar-nav a').forEach(a => a.classList.remove('active'));
      document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
      link.classList.add('active');
      document.getElementById(link.getAttribute('data-target')).classList.add('active');
      
      const t = link.getAttribute('data-target');
      if(t === 'overview-sec') loadStats();
      if(t === 'approvals-sec') loadStaffApprovals();
      if(t === 'bookings-sec') loadAllBookings();
      if(t === 'resources-sec') loadResources();
      if(t === 'users-sec') loadUsers();
    });
  });

  setupModal('res-modal', 'add-res-btn');
  document.getElementById('add-res-btn').addEventListener('click', () => {
    document.getElementById('res-modal-title').innerText = 'Add Resource';
    document.getElementById('res-form').reset();
    document.getElementById('res-id').value = '';
  });

  setupModal('role-modal');

  document.getElementById('res-form').addEventListener('submit', saveResource);
  document.getElementById('role-form').addEventListener('submit', updateRole);
  document.getElementById('bk-filter-status').addEventListener('change', loadAllBookings);

  loadStats();
});

async function loadStats() {
  const container = document.getElementById('admin-stats');
  try {
    const stats = await api.get('/admin/stats');
    container.innerHTML = `
      <div class="stat-card">
        <div class="muted">Total Resources</div>
        <div class="stat-value">${stats.total_resources || 0}</div>
      </div>
      <div class="stat-card">
        <div class="muted">Active Bookings</div>
        <div class="stat-value">${stats.active_bookings || 0}</div>
      </div>
      <div class="stat-card">
        <div class="muted">Pending Staff</div>
        <div class="stat-value">${stats.pending_staff || 0}</div>
      </div>
      <div class="stat-card">
        <div class="muted">Total Users</div>
        <div class="stat-value">${stats.total_users || 0}</div>
      </div>
    `;
  } catch(err) {
    container.innerHTML = `<p class="alert alert-error">Error loading stats</p>`;
  }
}

async function loadStaffApprovals() {
  const tbody = document.querySelector('#app-table tbody');
  tbody.innerHTML = '<tr><td colspan="5" class="text-center"><div class="spinner"></div></td></tr>';
  try {
    const data = await api.get('/admin/pending-staff');
    if (data.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="text-center">No pending approvals</td></tr>';
      return;
    }
    
    tbody.innerHTML = data.map(u => `
      <tr>
        <td>${u.name}</td>
        <td>${u.email}</td>
        <td>${u.department}</td>
        <td>${formatDate(u.created_at)}</td>
        <td>
          <button class="btn btn-success btn-outline" style="padding:0.25rem 0.5rem;font-size:0.75rem;" onclick="approveStaff('${u.id}')">Approve</button>
          <button class="btn btn-danger btn-outline" style="padding:0.25rem 0.5rem;font-size:0.75rem;" onclick="rejectStaff('${u.id}')">Reject</button>
        </td>
      </tr>
    `).join('');
  } catch(err) {
    tbody.innerHTML = `<tr><td colspan="5" class="alert alert-error">${err.message}</td></tr>`;
  }
}

async function approveStaff(id) {
  try { await api.patch(`/admin/staff/${id}/approve`); loadStaffApprovals(); loadStats(); } 
  catch(err) { showAlert('app-alert', err.message); }
}
async function rejectStaff(id) {
  if(!confirm('Reject this staff registration?')) return;
  try { await api.patch(`/admin/staff/${id}/reject`); loadStaffApprovals(); } 
  catch(err) { showAlert('app-alert', err.message); }
}

async function loadAllBookings() {
  const tbody = document.querySelector('#bk-table tbody');
  tbody.innerHTML = '<tr><td colspan="7" class="text-center"><div class="spinner"></div></td></tr>';
  const status = document.getElementById('bk-filter-status').value;
  
  try {
    let data = await api.get('/admin/bookings');
    if (status) data = data.filter(b => b.status === status);
    
    if (data.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center">No bookings found</td></tr>';
      return;
    }
    
    tbody.innerHTML = data.map(b => `
      <tr>
        <td>${b.student_name}</td>
        <td>${b.resource_name}</td>
        <td>${tierBadgeHtml(b.resource_tier)} ${b.is_hackathon ? '<span class="badge badge-premium">Hack</span>' : ''}</td>
        <td>${formatDate(b.start_date)}</td>
        <td>${b.start_slot}</td>
        <td>${badgeHtml(b.status)}</td>
        <td>
          ${b.status === 'pending' ? `
            <button class="btn btn-success btn-outline" style="padding:0.25rem 0.5rem;font-size:0.75rem;" onclick="updateBookingStatus('${b.id}', 'approved')">Approve</button>
            <button class="btn btn-danger btn-outline" style="padding:0.25rem 0.5rem;font-size:0.75rem;" onclick="updateBookingStatus('${b.id}', 'rejected')">Reject</button>
          ` : ''}
        </td>
      </tr>
    `).join('');
  } catch(err) {
    tbody.innerHTML = `<tr><td colspan="7" class="alert alert-error">${err.message}</td></tr>`;
  }
}

async function updateBookingStatus(id, status) {
  try { await api.patch(`/admin/bookings/${id}/status`, { status }); loadAllBookings(); } 
  catch(err) { showAlert('bk-alert', err.message); }
}

async function loadResources() {
  const tbody = document.querySelector('#res-table tbody');
  tbody.innerHTML = '<tr><td colspan="7" class="text-center"><div class="spinner"></div></td></tr>';
  try {
    const data = await api.get('/resources');
    if (data.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center">No resources</td></tr>';
      return;
    }
    tbody.innerHTML = data.map(r => `
      <tr>
        <td>${r.name}</td>
        <td>${r.type}</td>
        <td>${tierBadgeHtml(r.tier)}</td>
        <td>${r.location}</td>
        <td>${r.capacity}</td>
        <td>${r.is_available ? 'Yes' : 'No'}</td>
        <td>
          <button class="btn btn-primary btn-outline" style="padding:0.25rem 0.5rem;font-size:0.75rem;" onclick='editResource(${JSON.stringify(r)})'>Edit</button>
          <button class="btn btn-danger btn-outline" style="padding:0.25rem 0.5rem;font-size:0.75rem;" onclick="deleteResource('${r.id}')">Del</button>
        </td>
      </tr>
    `).join('');
  } catch(err) {
    tbody.innerHTML = `<tr><td colspan="7" class="alert alert-error">${err.message}</td></tr>`;
  }
}

function editResource(r) {
  document.getElementById('res-modal-title').innerText = 'Edit Resource';
  document.getElementById('res-id').value = r.id;
  document.getElementById('res-name').value = r.name;
  document.getElementById('res-type').value = r.type;
  document.getElementById('res-tier').value = r.tier;
  document.getElementById('res-location').value = r.location;
  document.getElementById('res-capacity').value = r.capacity;
  document.getElementById('res-available').checked = r.is_available;
  document.getElementById('res-modal').classList.add('active');
}

async function saveResource(e) {
  e.preventDefault();
  const id = document.getElementById('res-id').value;
  const btn = document.getElementById('res-submit-btn');
  btn.disabled = true;
  
  const body = {
    name: document.getElementById('res-name').value,
    type: document.getElementById('res-type').value,
    tier: document.getElementById('res-tier').value,
    location: document.getElementById('res-location').value,
    capacity: parseInt(document.getElementById('res-capacity').value),
    is_available: document.getElementById('res-available').checked
  };
  
  try {
    if (id) await api.put(`/admin/resources/${id}`, body);
    else await api.post('/admin/resources', body);
    
    document.getElementById('res-modal').classList.remove('active');
    loadResources();
    loadStats();
  } catch (err) {
    showAlert('res-alert', err.message);
  } finally {
    btn.disabled = false;
  }
}

async function deleteResource(id) {
  if(!confirm('Are you sure you want to delete this resource?')) return;
  try { await api.delete(`/admin/resources/${id}`); loadResources(); loadStats(); } 
  catch(err) { showAlert('res-alert', err.message); }
}

async function loadUsers() {
  const tbody = document.querySelector('#users-table tbody');
  tbody.innerHTML = '<tr><td colspan="6" class="text-center"><div class="spinner"></div></td></tr>';
  try {
    const data = await api.get('/admin/users');
    if (data.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="text-center">No users found</td></tr>';
      return;
    }
    
    tbody.innerHTML = data.map(u => `
      <tr>
        <td>${u.name}</td>
        <td>${u.email}</td>
        <td>${badgeHtml(u.role)}</td>
        <td>${u.role==='student' ? (u.reg_no || '-') : (u.department || '-')}</td>
        <td>${badgeHtml(u.status)}</td>
        <td>
          <button class="btn btn-primary btn-outline" style="padding:0.25rem 0.5rem;font-size:0.75rem;" onclick="openRoleModal('${u.id}', '${u.role}')">Change Role</button>
        </td>
      </tr>
    `).join('');
  } catch(err) {
    tbody.innerHTML = `<tr><td colspan="6" class="alert alert-error">${err.message}</td></tr>`;
  }
}

function openRoleModal(id, role) {
  document.getElementById('role-user-id').value = id;
  document.getElementById('role-select').value = role;
  document.getElementById('role-modal').classList.add('active');
}

async function updateRole(e) {
  e.preventDefault();
  const id = document.getElementById('role-user-id').value;
  const role = document.getElementById('role-select').value;
  const btn = document.getElementById('role-submit-btn');
  btn.disabled = true;
  
  try {
    await api.patch(`/admin/users/${id}/role`, { role });
    document.getElementById('role-modal').classList.remove('active');
    loadUsers();
  } catch (err) {
    showAlert('user-alert', err.message);
  } finally {
    btn.disabled = false;
  }
}
