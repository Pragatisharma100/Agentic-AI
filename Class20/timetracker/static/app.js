const state = { entries: [], projects: [], activeView: 'dashboard' };
const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];

function escapeHtml(value) { const div = document.createElement('div'); div.textContent = value ?? ''; return div.innerHTML; }
function formatHours(hours) { return `${Number(hours || 0).toLocaleString(undefined, { maximumFractionDigits: 2 })}h`; }
function formatDate(date) { return new Date(`${date}T12:00:00`).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }); }
function showToast(message, error = false) { const toast = $('#toast'); toast.textContent = message; toast.className = `toast show${error ? ' error' : ''}`; setTimeout(() => toast.className = 'toast', 2800); }

function switchView(view) {
  state.activeView = view;
  $$('.nav-item').forEach(item => item.classList.toggle('active', item.dataset.view === view));
  $$('.view').forEach(section => section.classList.toggle('active', section.id === `view-${view}`));
  $('#pageTitle').textContent = { dashboard: 'Overview', entries: 'Time entries', summary: 'Projects', log: 'Log time' }[view];
  if (view === 'summary') renderProjectCards();
}
$$('[data-view]').forEach(button => button.addEventListener('click', () => switchView(button.dataset.view)));

async function api(path, options) { const response = await fetch(path, options); if (!response.ok) throw new Error('Request failed'); return response.json(); }

function renderStats() {
  const total = state.entries.reduce((sum, entry) => sum + Number(entry.hours), 0);
  const today = new Date(); const start = new Date(today); start.setDate(today.getDate() - ((today.getDay() + 6) % 7));
  const weekHours = state.entries.filter(entry => new Date(`${entry.entry_date}T12:00:00`) >= start).reduce((sum, entry) => sum + Number(entry.hours), 0);
  $('#totalHours').textContent = formatHours(total); $('#weekHours').textContent = formatHours(weekHours);
  $('#entryCount').textContent = `${state.entries.length} ${state.entries.length === 1 ? 'entry' : 'entries'}`;
  $('#projectCount').textContent = state.projects.length;
  $('#memberCount').textContent = new Set(state.entries.map(entry => entry.employee_name)).size;
  $('#breakdownTotal').textContent = formatHours(total);
  $('#todayLabel').textContent = new Date().toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' });
}

function renderBars() {
  const totals = {}; state.entries.forEach(entry => { totals[entry.project] = (totals[entry.project] || 0) + Number(entry.hours); });
  const sorted = Object.entries(totals).sort((a, b) => b[1] - a[1]).slice(0, 5); const max = sorted[0]?.[1] || 1;
  $('#projectBars').innerHTML = sorted.length ? sorted.map(([project, hours], index) => `<div class="bar-row"><div class="bar-label"><span>${escapeHtml(project)}</span><strong>${formatHours(hours)}</strong></div><div class="bar-track"><span style="width:${hours / max * 100}%;--bar-index:${index}"></span></div></div>`).join('') : '<div class="empty-state">Log your first entry to see the breakdown.</div>';
}

function renderRecent() {
  const recent = [...state.entries].sort((a, b) => b.entry_date.localeCompare(a.entry_date)).slice(0, 5);
  $('#recentEntries').innerHTML = recent.length ? recent.map(entry => `<div class="activity-row"><span class="avatar">${escapeHtml(entry.employee_name.charAt(0).toUpperCase())}</span><div><strong>${escapeHtml(entry.employee_name)}</strong><span>${escapeHtml(entry.project)} · ${formatDate(entry.entry_date)}</span></div><b>${formatHours(entry.hours)}</b></div>`).join('') : '<div class="empty-state">No entries yet.</div>';
}

function filteredEntries() {
  const search = $('#searchInput').value.toLowerCase(); const person = $('#employeeFilter').value; const project = $('#projectFilter').value; const date = $('#dateFilter').value;
  return state.entries.filter(entry => (!search || `${entry.employee_name} ${entry.project} ${entry.description}`.toLowerCase().includes(search)) && (!person || entry.employee_name === person) && (!project || entry.project === project) && (!date || entry.entry_date >= date)).sort((a, b) => b.entry_date.localeCompare(a.entry_date));
}
function renderTable() {
  const entries = filteredEntries(); $('#emptyState').hidden = entries.length > 0;
  $('#entriesTable tbody').innerHTML = entries.map(entry => `<tr><td>${formatDate(entry.entry_date)}</td><td><span class="person-cell"><span class="mini-avatar">${escapeHtml(entry.employee_name.charAt(0))}</span>${escapeHtml(entry.employee_name)}</span></td><td><span class="project-pill">${escapeHtml(entry.project)}</span></td><td class="hours-cell">${formatHours(entry.hours)}</td><td class="description-cell">${escapeHtml(entry.description || '—')}</td><td><button class="delete-button" data-entry-id="${entry.id}" title="Delete this time entry" aria-label="Delete ${escapeHtml(entry.project)} entry">⌫</button></td></tr>`).join('');
}

function populateFilters() {
  const employees = [...new Set(state.entries.map(entry => entry.employee_name))].sort(); const currentEmployee = $('#employeeFilter').value; const currentProject = $('#projectFilter').value;
  $('#employeeFilter').innerHTML = '<option value="">All people</option>' + employees.map(name => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`).join('');
  $('#projectFilter').innerHTML = '<option value="">All projects</option>' + state.projects.map(project => `<option value="${escapeHtml(project)}">${escapeHtml(project)}</option>`).join('');
  $('#employeeFilter').value = currentEmployee; $('#projectFilter').value = currentProject;
  $('#projectList').innerHTML = state.projects.map(project => `<option value="${escapeHtml(project)}">`).join('');
}

function renderProjectCards() {
  const totals = {}; state.entries.forEach(entry => { totals[entry.project] = (totals[entry.project] || 0) + Number(entry.hours); }); const max = Math.max(...Object.values(totals), 1);
  $('#projectCards').innerHTML = state.projects.length ? state.projects.map(project => `<button class="project-card" data-project="${escapeHtml(project)}"><span class="project-mark">${escapeHtml(project.charAt(0))}</span><span><strong>${escapeHtml(project)}</strong><small>${formatHours(totals[project] || 0)} logged</small></span><span class="card-arrow">→</span><i style="width:${(totals[project] || 0) / max * 100}%"></i></button>`).join('') : '<div class="empty-state">No projects yet.</div>';
  $$('.project-card').forEach(card => card.addEventListener('click', () => loadSummary(card.dataset.project)));
}
async function loadSummary(project) { try { const summary = await api(`/api/projects/${encodeURIComponent(project)}/summary`); $('#summaryResult').innerHTML = `<p class="eyebrow">Selected project</p><h3>${escapeHtml(summary.project)}</h3><strong class="summary-total">${formatHours(summary.total_hours)}</strong><span class="summary-caption">total logged hours</span><div class="team-list">${Object.entries(summary.by_employee).map(([name, hours]) => `<div><span>${escapeHtml(name)}</span><strong>${formatHours(hours)}</strong></div>`).join('')}</div>`; } catch { showToast('Could not load project summary', true); } }

function exportCsv() { const entries = filteredEntries(); const csv = [['Date', 'Employee', 'Project', 'Hours', 'Description'], ...entries.map(entry => [entry.entry_date, entry.employee_name, entry.project, entry.hours, entry.description])].map(row => row.map(value => `"${String(value ?? '').replaceAll('"', '""')}"`).join(',')).join('\n'); const link = document.createElement('a'); link.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' })); link.download = 'timetrack-entries.csv'; link.click(); URL.revokeObjectURL(link.href); }

async function loadData() { try { state.entries = await api('/api/entries'); state.projects = await api('/api/projects'); renderStats(); renderBars(); renderRecent(); renderTable(); populateFilters(); renderProjectCards(); } catch { showToast('Unable to connect to the time tracker', true); } }
$('#logForm').addEventListener('submit', async event => { event.preventDefault(); const body = { employee_name: $('#employeeInput').value.trim(), project: $('#projectInput').value.trim(), entry_date: $('#dateInput').value, hours: Number($('#hoursInput').value), description: $('#descInput').value.trim() }; try { await api('/api/entries', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }); $('#logForm').reset(); $('#dateInput').value = new Date().toISOString().slice(0, 10); showToast('Time entry saved'); await loadData(); switchView('entries'); } catch { showToast('Could not save this entry', true); } });
$('#entriesTable tbody').addEventListener('click', async event => { const button = event.target.closest('.delete-button'); if (!button) return; const entry = state.entries.find(item => String(item.id) === button.dataset.entryId); if (!entry || !confirm(`Delete ${entry.hours}h logged for ${entry.project}?`)) return; button.disabled = true; try { await api(`/api/entries/${button.dataset.entryId}`, { method: 'DELETE' }); showToast('Time entry deleted'); await loadData(); } catch { button.disabled = false; showToast('Could not delete this entry', true); } });
['searchInput', 'employeeFilter', 'projectFilter', 'dateFilter'].forEach(id => $(`#${id}`).addEventListener('input', renderTable));
$('#exportBtn').addEventListener('click', exportCsv); $('#entriesExportBtn').addEventListener('click', exportCsv);
$('#themeToggle').addEventListener('click', () => { const dark = document.documentElement.classList.toggle('dark'); localStorage.setItem('timetrack-theme', dark ? 'dark' : 'light'); $('#themeToggle').textContent = dark ? '☀' : '☾'; });
if (localStorage.getItem('timetrack-theme') === 'dark') { document.documentElement.classList.add('dark'); $('#themeToggle').textContent = '☀'; }
$('#dateInput').value = new Date().toISOString().slice(0, 10); loadData();