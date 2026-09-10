requireAuth(['student']);

let allResources = [];
let currentAvailResource = null;
let selectedSlots = [];

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('logout-btn').addEventListener('click', logout);
  document.getElementById('user-info').innerText = `${getUserName()}\nStudent`;
  
  // Navigation
  document.querySelectorAll('.sidebar-nav a[data-target]').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      document.querySelectorAll('.sidebar-nav a').forEach(a => a.classList.remove('active'));
      document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
      link.classList.add('active');
      const target = document.getElementById(link.getAttribute('data-target'));
      target.classList.add('active');
      
      if(link.getAttribute('data-target') === 'bookings-sec') loadMyBookings();
      if(link.getAttribute('data-target') === 'browse-sec') loadResources();
    });
  });

  // Populate slot dropdowns
  const stSlot = document.getElementById('nb-start-slot');
  const enSlot = document.getElementById('nb-end-slot');
  TIME_SLOTS.forEach(t => {
    stSlot.insertAdjacentHTML('beforeend', `<option value="${t}">${t}</option>`);
    enSlot.insertAdjacentHTML('beforeend', `<option value="${t}">${t}</option>`);
  });

  setupModal('avail-modal');

  // Load Initial Data
  loadResources();
  
  // Filters
  document.getElementById('filter-type').addEventListener('change', renderResources);
  document.getElementById('filter-tier').addEventListener('change', renderResources);
  
  // Availability Modal Handlers
  document.getElementById('avail-date').addEventListener('change', checkAvailability);
  
  // New Booking Handlers
  const hackToggle = document.getElementById('nb-hackathon');
  const endDateInput = document.getElementById('nb-end-date');
  const startDateInput = document.getElementById('nb-start-date');
  
  hackToggle.addEventListener('change', (e) => {
    document.getElementById('nb-event-group').style.display = e.target.checked ? 'block' : 'none';
    if(!e.target.checked) endDateInput.value = startDateInput.value;
  });
  
  startDateInput.addEventListener('change', () => {
    if(!hackToggle.checked) endDateInput.value = startDateInput.value;
  });
  
  const today = new Date().toISOString().split('T')[0];
  startDateInput.min = today;
  endDateInput.min = today;
  document.getElementById('avail-date').min = today;
  
  document.getElementById('new-booking-form').addEventListener('submit', submitBooking);
});

async function loadResources() {
  try {
    allResources = await api.get('/resources');
    renderResources();
    
    // populate dropdown
    const resSelect = document.getElementById('nb-resource');
    resSelect.innerHTML = '<option value="">Select Resource...</option>';
    allResources.filter(r => r.is_available).forEach(r => {
      resSelect.insertAdjacentHTML('beforeend', `<option value="${r.id}">${r.name} (${r.type})</option>`);
    });
  } catch (err) {
    document.getElementById('resource-grid').innerHTML = `<p class="alert alert-error">Failed to load resources: ${err.message}</p>`;
  }
}

function renderResources() {
  const type = document.getElementById('filter-type').value;
  const tier = document.getElementById('filter-tier').value;
  const grid = document.getElementById('resource-grid');
  
  let filtered = allResources;
  if(type) filtered = filtered.filter(r => r.type === type);
  if(tier) filtered = filtered.filter(r => r.tier === tier);
  
  if (filtered.length === 0) {
    grid.innerHTML = '<p>No resources found.</p>';
    return;
  }
  
  grid.innerHTML = filtered.map(r => `
    <div class="resource-card">
      <div class="flex justify-between items-center mb-2">
        <h3 style="margin:0">${r.name}</h3>
        ${tierBadgeHtml(r.tier)}
      </div>
      <p class="muted" style="font-size: 0.875rem;">${r.type} | Capacity: ${r.capacity}</p>
      <p class="muted mb-4" style="font-size: 0.875rem;">Location: ${r.location}</p>
      ${r.is_available 
        ? `<button class="btn btn-outline btn-block" onclick="openAvailModal('${r.id}', '${r.name.replace(/'/g, "\\'")}')">Check Availability</button>`
        : `<button class="btn btn-block" disabled>Unavailable</button>`}
    </div>
  `).join('');
}

function openAvailModal(id, name) {
  currentAvailResource = id;
  document.getElementById('avail-resource-name').innerText = name;
  document.getElementById('avail-date').value = new Date().toISOString().split('T')[0];
  document.getElementById('avail-slots').innerHTML = '';
  document.getElementById('avail-book-btn').style.display = 'none';
  selectedSlots = [];
  document.getElementById('avail-modal').classList.add('active');
  checkAvailability();
}

async function checkAvailability() {
  const date = document.getElementById('avail-date').value;
  if(!date || !currentAvailResource) return;
  
  document.getElementById('avail-loading').style.display = 'block';
  document.getElementById('avail-slots').innerHTML = '';
  selectedSlots = [];
  document.getElementById('avail-book-btn').style.display = 'none';
  
  try {
    const data = await api.get(`/resources/${currentAvailResource}/availability?date=${date}`);
    const booked = data.booked_slots || [];
    
    document.getElementById('avail-loading').style.display = 'none';
    const grid = document.getElementById('avail-slots');
    
    TIME_SLOTS.forEach((t, index) => {
      const isBooked = booked.includes(t);
      const div = document.createElement('div');
      div.className = `slot ${isBooked ? 'booked' : 'available'}`;
      div.innerText = t;
      div.dataset.index = index;
      div.dataset.time = t;
      
      if(!isBooked) {
        div.addEventListener('click', () => toggleSlotSelection(index));
      }
      grid.appendChild(div);
    });
    
  } catch (err) {
    document.getElementById('avail-loading').style.display = 'none';
    document.getElementById('avail-slots').innerHTML = `<p class="alert alert-error">Error: ${err.message}</p>`;
  }
}

function toggleSlotSelection(index) {
  const slots = document.querySelectorAll('.slot');
  
  if (selectedSlots.length === 0) {
    selectedSlots.push(index);
  } else if (selectedSlots.length === 1) {
    const start = Math.min(selectedSlots[0], index);
    const end = Math.max(selectedSlots[0], index);
    
    let canSelect = true;
    for(let i=start; i<=end; i++) {
      if(slots[i].classList.contains('booked')) canSelect = false;
    }
    
    if (canSelect) {
      selectedSlots = [];
      for(let i=start; i<=end; i++) selectedSlots.push(i);
    } else {
      selectedSlots = [index];
    }
  } else {
    selectedSlots = [index];
  }
  
  slots.forEach(s => s.classList.remove('selected'));
  selectedSlots.forEach(i => slots[i].classList.add('selected'));
  
  const btn = document.getElementById('avail-book-btn');
  if (selectedSlots.length > 0) {
    btn.style.display = 'block';
    btn.onclick = () => {
      document.getElementById('avail-modal').classList.remove('active');
      document.querySelector('[data-target="new-booking-sec"]').click();
      
      document.getElementById('nb-resource').value = currentAvailResource;
      document.getElementById('nb-start-date').value = document.getElementById('avail-date').value;
      document.getElementById('nb-end-date').value = document.getElementById('avail-date').value;
      
      selectedSlots.sort((a,b)=>a-b);
      document.getElementById('nb-start-slot').value = TIME_SLOTS[selectedSlots[0]];
      const endIdx = Math.min(selectedSlots[selectedSlots.length-1] + 1, TIME_SLOTS.length - 1);
      document.getElementById('nb-end-slot').value = TIME_SLOTS[endIdx];
    };
  } else {
    btn.style.display = 'none';
  }
}

async function loadMyBookings() {
  const tbody = document.querySelector('#my-bookings-table tbody');
  tbody.innerHTML = '<tr><td colspan="6" class="text-center"><div class="spinner"></div></td></tr>';
  
  try {
    const data = await api.get('/bookings');
    
    if (data.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="text-center">No bookings found.</td></tr>';
      return;
    }
    
    tbody.innerHTML = data.map(b => `
      <tr>
        <td>${b.resource_name}</td>
        <td>${formatDate(b.start_date)}${b.start_date !== b.end_date ? ' - ' + formatDate(b.end_date) : ''}</td>
        <td>${b.start_slot} - ${b.end_slot}</td>
        <td>${b.is_hackathon ? 'Hackathon' : 'Regular'}</td>
        <td>${badgeHtml(b.status)}</td>
        <td>
          ${b.status === 'pending' ? `<button class="btn btn-danger btn-outline" style="padding:0.25rem 0.5rem;font-size:0.75rem;" onclick="cancelBooking('${b.id}')">Cancel</button>` : ''}
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" class="alert alert-error">Error: ${err.message}</td></tr>`;
  }
}

async function cancelBooking(id) {
  if(!confirm('Are you sure you want to cancel this booking?')) return;
  try {
    await api.patch(`/bookings/${id}/cancel`);
    loadMyBookings();
  } catch (err) {
    showAlert('my-bookings-alert', err.message);
  }
}

async function submitBooking(e) {
  e.preventDefault();
  const btn = document.getElementById('nb-submit-btn');
  btn.disabled = true;
  
  const isHackathon = document.getElementById('nb-hackathon').checked;
  
  const resId = document.getElementById('nb-resource').value.trim();
  const startDate = document.getElementById('nb-start-date').value;
  const endDate = document.getElementById('nb-end-date').value || startDate;
  const eventName = isHackathon ? document.getElementById('nb-event-name').value.trim() : null;

  const body = {
    resource_id: resId,
    start_date: startDate,
    end_date: endDate,
    date_start: startDate,
    date_end: endDate,
    start_slot: document.getElementById('nb-start-slot').value,
    end_slot: document.getElementById('nb-end-slot').value,
    is_hackathon: isHackathon,
    event_name: eventName,
    hackathon_event: eventName
  };
  
  const startIdx = TIME_SLOTS.indexOf(body.start_slot);
  const endIdx = TIME_SLOTS.indexOf(body.end_slot);
  if (endIdx <= startIdx && body.start_date === body.end_date) {
    showAlert('new-booking-alert', 'End slot must be after start slot');
    btn.disabled = false;
    return;
  }
  
  if (!isHackathon) {
    if (endIdx - startIdx > 4) {
      showAlert('new-booking-alert', 'Regular bookings cannot exceed 4 slots.');
      btn.disabled = false;
      return;
    }
  }
  
  try {
    await api.post('/bookings', body);
    showAlert('new-booking-alert', 'Booking submitted successfully!', 'success');
    e.target.reset();
    document.getElementById('nb-event-group').style.display = 'none';
    setTimeout(() => {
      document.querySelector('[data-target="bookings-sec"]').click();
    }, 1500);
  } catch (err) {
    showAlert('new-booking-alert', err.message);
  } finally {
    btn.disabled = false;
  }
}
