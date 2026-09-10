requireAuth(['staff', 'admin']);

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('logout-btn').addEventListener('click', logout);
  document.getElementById('user-info').innerText = `${getUserName()}\nStaff`;
  
  // Navigation
  document.querySelectorAll('.sidebar-nav a[data-target]').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      document.querySelectorAll('.sidebar-nav a').forEach(a => a.classList.remove('active'));
      document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
      link.classList.add('active');
      document.getElementById(link.getAttribute('data-target')).classList.add('active');
      
      if(link.getAttribute('data-target') === 'queue-sec') loadQueue();
      if(link.getAttribute('data-target') === 'resources-sec') loadResources();
    });
  });

  setupModal('res-modal', 'add-res-btn');
  document.getElementById('add-res-btn').addEventListener('click', () => {
    document.getElementById('res-modal-title').innerText = 'Add Resource';
    document.getElementById('res-form').reset();
    document.getElementById('res-id').value = '';
  });

  document.getElementById('queue-filter').addEventListener('change', loadQueue);
  document.getElementById('res-form').addEventListener('submit', saveResource);

  loadQueue();
});

async function loadQueue() {
  const tbody = document.querySelector('#queue-table tbody');
  tbody.innerHTML = '<tr><td colspan="6" class="text-center"><div class="spinner"></div></td></tr>';
  const status = document.getElementById('queue-filter').value;
  
  try {
    let data = await api.get('/bookings');
    if (status) data = data.filter(b => b.status === status);
    
    if (data.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="text-center">No bookings found.</td></tr>';
      return;
    }
    
    tbody.innerHTML = data.map(b => `
      <tr>
        <td>${b.student_name} <br><small class="muted">${b.student_reg_no}</small></td>
        <td>${b.resource_name} ${b.is_hackathon ? '<span class="badge badge-premium">Hackathon</span>' : ''}</td>
        <td>${formatDate(b.start_date)}${b.start_date !== b.end_date ? ' - ' + formatDate(b.end_date) : ''}</td>
        <td>${b.start_slot} - ${b.end_slot}</td>
        <td>${badgeHtml(b.status)}</td>
        <td>
          ${b.status === 'pending' ? `
            <button class="btn btn-success btn-outline" style="padding:0.25rem 0.5rem;font-size:0.75rem;" onclick="updateBooking('${b.id}', 'approved')">Approve</button>
            <button class="btn btn-danger btn-outline" style="padding:0.25rem 0.5rem;font-size:0.75rem;" onclick="updateBooking('${b.id}', 'rejected')">Reject</button>
          ` : ''}
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" class="alert alert-error">Error: ${err.message}</td></tr>`;
  }
}

async function updateBooking(id, status) {
  try {
    await api.patch(`/bookings/${id}/status`, { status });
    loadQueue();
  } catch (err) {
    showAlert('queue-alert', err.message);
  }
}

async function loadResources() {
  const tbody = document.querySelector('#res-table tbody');
  tbody.innerHTML = '<tr><td colspan="6" class="text-center"><div class="spinner"></div></td></tr>';
  try {
    const data = await api.get('/resources');
    const std = data.filter(r => r.tier === 'standard');
    
    if (std.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="text-center">No resources found.</td></tr>';
      return;
    }
    
    tbody.innerHTML = std.map(r => `
      <tr>
        <td>${r.name}</td>
        <td>${r.type}</td>
        <td>${r.location}</td>
        <td>${r.capacity}</td>
        <td>
          <label class="switch">
            <input type="checkbox" ${r.is_available ? 'checked' : ''} onchange="toggleAvailable('${r.id}', this.checked)">
            <span class="slider"></span>
          </label>
          ${r.is_available ? 'Yes' : 'No'}
        </td>
        <td>
          <button class="btn btn-primary btn-outline" style="padding:0.25rem 0.5rem;font-size:0.75rem;" onclick='editResource(${JSON.stringify(r)})'>Edit</button>
          <button class="btn btn-danger btn-outline" style="padding:0.25rem 0.5rem;font-size:0.75rem;" onclick="deleteResource('${r.id}')">Del</button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" class="alert alert-error">Error: ${err.message}</td></tr>`;
  }
}

function editResource(r) {
  document.getElementById('res-modal-title').innerText = 'Edit Resource';
  document.getElementById('res-id').value = r.id;
  document.getElementById('res-name').value = r.name;
  document.getElementById('res-type').value = r.type;
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
    location: document.getElementById('res-location').value,
    capacity: parseInt(document.getElementById('res-capacity').value),
    is_available: document.getElementById('res-available').checked,
    tier: 'standard'
  };
  
  try {
    if (id) {
      await api.put(`/resources/${id}`, body);
    } else {
      await api.post('/resources', body);
    }
    document.getElementById('res-modal').classList.remove('active');
    loadResources();
  } catch (err) {
    showAlert('res-alert', err.message);
  } finally {
    btn.disabled = false;
  }
}

async function deleteResource(id) {
  if(!confirm('Are you sure you want to delete this resource?')) return;
  try {
    await api.delete(`/resources/${id}`);
    loadResources();
  } catch (err) {
    showAlert('res-alert', err.message);
  }
}

async function toggleAvailable(id, status) {
  try {
    await api.patch(`/resources/${id}/availability`, { is_available: status });
    loadResources();
  } catch(err) {
    showAlert('res-alert', err.message);
    loadResources();
  }
}
