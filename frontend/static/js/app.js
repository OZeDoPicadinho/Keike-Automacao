async function fetchJSON(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || 'Erro');
  }
  return response.json();
}

window.renderDashboard = async function () {
  const cards = document.getElementById('dashboard-cards');
  const events = document.getElementById('events-list');
  const cabins = await fetchJSON('/api/cabins');
  const eventList = await fetchJSON('/api/events');
  cards.innerHTML = cabins.map(c => `
    <div class="card">
      <h3>${c.name}</h3>
      <p>${c.address}</p>
      <strong>${c.status}</strong>
    </div>
  `).join('');
  events.innerHTML = '<h4>ÚLTIMOS EVENTOS</h4>' + eventList.map(e => `
    <div class="event">
      <strong>${e.title}</strong>
      <p>${e.description}</p>
    </div>
  `).join('');
}

window.renderCabins = async function () {
  const grid = document.getElementById('cabins-grid');
  const cabins = await fetchJSON('/api/cabins');
  grid.innerHTML = cabins.map(c => `
    <div class="card">
      <h3>${c.name}</h3>
      <p>${c.address}</p>
      <small>Facial: ${c.terminal_facial || 'Não vinculado'}</small><br/>
      <small>LPR: ${c.lpr_terminal || 'Não vinculado'}</small>
    </div>
  `).join('');
}

window.createCabin = async function () {
  const payload = {
    name: document.getElementById('cabin-name').value,
    address: document.getElementById('cabin-address').value,
    photo_url: document.getElementById('cabin-photo').value,
    terminal_facial: document.getElementById('cabin-facial').value,
    lpr_terminal: document.getElementById('cabin-lpr').value,
    status: 'Disponível'
  };
  await fetchJSON('/api/cabins', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  window.renderCabins();
}

window.renderPeople = async function () {
  const grid = document.getElementById('people-grid');
  const people = await fetchJSON('/api/people');
  grid.innerHTML = people.map(p => `
    <div class="card">
      <h3>${p.name}</h3>
      <p>${p.role}</p>
      <small>${p.email || ''}</small>
    </div>
  `).join('');
}

window.createPerson = async function () {
  const payload = {
    name: document.getElementById('person-name').value,
    role: document.getElementById('person-role').value,
    phone: document.getElementById('person-phone').value,
    email: document.getElementById('person-email').value
  };
  await fetchJSON('/api/people', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  window.renderPeople();
}

window.renderReservations = async function () {
  const grid = document.getElementById('reservations-grid');
  const cabins = await fetchJSON('/api/cabins');
  const people = await fetchJSON('/api/people');
  const reservations = await fetchJSON('/api/reservations');
  const cabinSelect = document.getElementById('reservation-cabin');
  const personSelect = document.getElementById('reservation-person');
  cabinSelect.innerHTML = cabins.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
  personSelect.innerHTML = people.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
  grid.innerHTML = reservations.map(r => `
    <div class="card">
      <h3>Código ${r.code}</h3>
      <p>Status: ${r.status}</p>
      <button onclick="window.checkIn(${r.id})">Check-in</button>
      <button onclick="window.checkOut(${r.id})">Check-out</button>
    </div>
  `).join('');
}

window.createReservation = async function () {
  const warning = document.getElementById('reservation-warning');
  warning.textContent = '';
  const payload = {
    cabin_id: parseInt(document.getElementById('reservation-cabin').value, 10),
    person_id: parseInt(document.getElementById('reservation-person').value, 10),
    start_at: document.getElementById('reservation-start').value,
    end_at: document.getElementById('reservation-end').value,
    status: 'Reservado'
  };
  try {
    await fetchJSON('/api/reservations', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    window.renderReservations();
  } catch (err) {
    warning.textContent = err.message;
  }
}

window.checkIn = async function (id) {
  await fetchJSON(`/api/reservations/${id}/checkin`, { method: 'PUT' });
  window.renderReservations();
}

window.checkOut = async function (id) {
  await fetchJSON(`/api/reservations/${id}/checkout`, { method: 'PUT' });
  window.renderReservations();
}

window.renderDevices = async function () {
  const grid = document.getElementById('devices-grid');
  const devices = await fetchJSON('/api/devices');
  grid.innerHTML = devices.map(d => `
    <div class="card">
      <h3>${d.name}</h3>
      <p>${d.kind}</p>
    </div>
  `).join('');
}

window.createDevice = async function () {
  const payload = {
    name: document.getElementById('device-name').value,
    kind: document.getElementById('device-kind').value
  };
  await fetchJSON('/api/devices', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  window.renderDevices();
}

window.renderIntegrations = async function () {
  const grid = document.getElementById('integrations-grid');
  const integrations = await fetchJSON('/api/integrations');
  grid.innerHTML = integrations.map(i => `
    <div class="card">
      <h3>${i.provider}</h3>
      <p>${i.username}</p>
    </div>
  `).join('');
}

window.createIntegration = async function () {
  const payload = {
    provider: document.getElementById('integration-provider').value,
    username: document.getElementById('integration-username').value,
    password: document.getElementById('integration-password').value
  };
  await fetchJSON('/api/integrations', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  window.renderIntegrations();
}

window.renderUsers = async function () {
  const grid = document.getElementById('users-grid');
  const users = await fetchJSON('/api/users');
  grid.innerHTML = users.map(u => `
    <div class="card">
      <h3>${u.name}</h3>
      <p>${u.role}</p>
    </div>
  `).join('');
}

window.createUser = async function () {
  const payload = {
    name: document.getElementById('user-name').value,
    email: document.getElementById('user-email').value,
    phone: document.getElementById('user-phone').value,
    username: document.getElementById('user-username').value,
    password: document.getElementById('user-password').value,
    role: document.getElementById('user-role').value,
    is_super_admin: false
  };
  await fetchJSON('/api/users', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  window.renderUsers();
}
