import { VERSION, TOOLS, normalizeTarget, findings, compareReports, explain, parseBatch, redactReport, exportContent, escapeHTML as e } from './core.mjs';
import { LANGUAGES, translate, toolLabel, fieldLabel } from './lang.mjs';

const STORE = 'ghosttrack.atlas.v1';
const $ = selector => document.querySelector(selector);
const initialSaved = { language: 'zh', snapshots: [], favorites: [] };
function validReport(value) {
  if (!value || value.schema !== 1 || !Object.hasOwn(TOOLS, value.tool) || typeof value.target !== 'string' || value.target.length > 4096 ||
      !Number.isFinite(Date.parse(value.at)) || !Array.isArray(value.sources) || !value.sources.length || value.sources.length > 12) return false;
  if (typeof value.id !== 'string' || !/^[a-z\d-]{1,80}$/i.test(value.id) || !Number.isFinite(value.elapsedMs) || value.elapsedMs < 0) return false;
  if (value.region !== undefined && (typeof value.region !== 'string' || !/^[A-Z]{2}$/.test(value.region))) return false;
  if (value.platform !== undefined && (typeof value.platform !== 'string' || value.platform.length > 40)) return false;
  const ids = new Set();
  for (const source of value.sources) {
    if (!/^[A-Z_]{1,20}$/.test(source.id) || ids.has(source.id) || !['ok', 'partial', 'error', 'limited', 'rate_limited', 'cancelled'].includes(source.status) ||
        !source.fields || Array.isArray(source.fields) || typeof source.fields !== 'object' || Object.keys(source.fields).length > 150) return false;
    ids.add(source.id);
    if (Object.entries(source.fields).some(([k, v]) => k.length > 200 || !['string', 'number', 'boolean'].includes(typeof v) && v !== null || String(v).length > 20000)) return false;
    if (source.url !== undefined && (typeof source.url !== 'string' || source.url.length > 4096)) return false;
  }
  try { return JSON.stringify(value).length <= 500000; } catch { return false; }
}
let saved;
try {
  const raw = localStorage.getItem(STORE);
  const data = raw && raw.length <= 2000000 ? JSON.parse(raw) : null;
  saved = data ? { language: Object.hasOwn(LANGUAGES, data.language) ? data.language : 'zh',
    snapshots: Array.isArray(data.snapshots) ? data.snapshots.slice(0, 50).filter(validReport) : [],
    favorites: Array.isArray(data.favorites) ? data.favorites.slice(0, 50).filter(x => x && Object.hasOwn(TOOLS, x.tool) && typeof x.target === 'string' && x.target.length <= 4096 && typeof x.id === 'string' && /^[a-z\d-]{1,80}$/i.test(x.id)) : [] } : { ...initialSaved };
} catch { saved = { ...initialSaved }; }
const state = { language: saved.language, saved, route: 'research', tool: 'overview', target: '', region: 'CN', platform: 'Auto',
  meta: null, report: null, tab: 'observations', filter: '', message: 'ready', busy: false, active: null,
  queue: [], queueRunning: false, paused: false, stopQueue: false, batchText: '', comparison: null, updates: null, updateBusy: false };
const t = (key, vars) => translate(key, state.language, vars);
const tl = key => toolLabel(key, state.language);
const fl = key => fieldLabel(key, state.language);
const icons = { research: '<circle cx="11" cy="11" r="7"/><path d="m16 16 5 5M11 7v8M7 11h8"/>', batch: '<path d="M4 5h16M4 12h16M4 19h16"/><circle cx="7" cy="5" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="17" cy="19" r="1"/>', compare: '<path d="M8 4v16M16 4v16M4 8l4-4 4 4M12 16l4 4 4-4"/>', history: '<path d="M3 11a9 9 0 1 1 3 7M3 4v7h7M12 7v5l3 2"/>', favorites: '<path d="m12 3 3 6 7 1-5 5 1 7-6-3-6 3 1-7-5-5 7-1Z"/>', sources: '<circle cx="12" cy="12" r="9"/><path d="m7 12 3 3 7-7"/>', settings: '<path d="M4 7h16M4 17h16"/><circle cx="8" cy="7" r="3"/><circle cx="16" cy="17" r="3"/>', updates: '<path d="M20 8a8 8 0 1 0 0 8M20 3v5h-5M12 8v5l3 2"/>' };
const icon = key => `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">${icons[key] ?? icons.research}</svg>`;
const date = value => Number.isFinite(Date.parse(value)) ? new Date(value).toISOString().replace('T', ' ').slice(0, 19) + ' UTC' : '—';
const badge = status => `<span class="chip ${e(status)}">${e(t(status))}</span>`;
function safeURL(value) {
  try { const u = new URL(value); return u.protocol === 'https:' && !u.username && !u.password ? u.href : null; } catch { return null; }
}
const sourceLink = source => safeURL(source.url) ? `<a href="${e(safeURL(source.url))}" target="_blank" rel="noopener noreferrer">${e(t('source'))} ↗</a>` : '';
function toast(key, raw = false) {
  $('#toast').textContent = raw ? key : t(key);
  $('#toast').classList.add('visible');
  clearTimeout(toast.timer); toast.timer = setTimeout(() => $('#toast').classList.remove('visible'), 3800);
}
function persist(next) {
  try {
    const text = JSON.stringify(next);
    if (text.length > 1900000) throw new Error();
    localStorage.setItem(STORE, text); state.saved = next; return true;
  } catch { toast('storage_full'); return false; }
}
const button = (action, label, cls = '', extra = '') => `<button type="button" class="${cls}" data-action="${action}" ${extra}>${e(t(label))}</button>`;
function empty(title = 'empty_results', hint = 'empty_hint') {
  return `<div class="empty"><svg viewBox="0 0 160 110" fill="none" aria-hidden="true"><path d="M5 20h150M5 45h150M5 70h150M5 95h150M30 10v90M55 10v90M80 10v90M105 10v90M130 10v90" stroke="#203c4e"/><circle cx="80" cy="55" r="31" stroke="currentColor"/><circle cx="80" cy="55" r="17" stroke="currentColor"/><path d="m80 55 35-29" stroke="#70efbd" stroke-width="2"/><circle cx="80" cy="55" r="3" fill="#70efbd"/><path d="M8 30V12h18M134 12h18v18M8 80v18h18M134 98h18V80" stroke="#547b89"/></svg><h2>${e(t(title))}</h2><p class="note">${e(t(hint))}</p></div>`;
}
function readForm() {
  if ($('#tool')) state.tool = $('#tool').value;
  if ($('#target')) state.target = $('#target').value;
  if ($('#region')) state.region = $('#region').value.toUpperCase();
  if ($('#platform')) state.platform = $('#platform').value;
  if ($('#batch-text')) state.batchText = $('#batch-text').value;
}
function render() {
  document.documentElement.lang = { zh: 'zh-CN', en: 'en', ja: 'ja', es: 'es' }[state.language];
  document.title = `GhostTrack Atlas · ${t(state.route)}`;
  const nav = ['research', 'batch', 'compare', 'favorites', 'history', 'sources', 'settings', 'updates'];
  $('#app').innerHTML = `<div class="shell"><aside class="sidebar"><div class="brand"><span class="brand-mark">G</span><div><strong>GHOSTTRACK</strong><small>ATLAS / ${VERSION}</small></div></div><div class="nav-label">WORKSPACE</div><nav class="nav" aria-label="${e(t('workspace'))}">${nav.map(key => `<button type="button" data-view="${key}" class="${state.route === key ? 'active' : ''}" ${state.route === key ? 'aria-current="page"' : ''}>${icon(key)}<span>${e(t(key))}</span></button>`).join('')}</nav><div class="sidebar-bottom"><div class="sidebar-foot">${e(t('public_only'))}<br>${e(t('attribution'))}<a href="https://github.com/Serennity007/GhostTrack" target="_blank" rel="noopener noreferrer">${e(t('docs'))} ↗</a></div></div></aside><div class="topbar"><div class="breadcrumb"><span>GhostTrack Atlas</span><span>/</span><b>${e(t(state.route))}</b></div><div class="top-actions"><span class="runtime">${e(state.meta ? t(state.meta.runtime) : 'CONNECTING')}</span><select id="language" aria-label="Language">${Object.entries(LANGUAGES).map(([key, name]) => `<option value="${key}" ${key === state.language ? 'selected' : ''}>${name}</option>`).join('')}</select></div></div><main id="main" class="content" tabindex="-1"><header class="hero"><div><div class="kicker">${e(t('workspace'))}</div><h1>${e(state.route === 'research' ? t('headline') : t(state.route))}</h1><p class="subline">${e(state.route === 'research' ? t('subline') : t('public_only'))}</p></div><svg class="orbit" viewBox="0 0 130 90" fill="none" aria-hidden="true"><path d="M5 45h120M65 5v80" stroke="#254052"/><circle cx="65" cy="45" r="35" stroke="#315469"/><circle cx="65" cy="45" r="23" stroke="#497881"/><circle cx="65" cy="45" r="10" stroke="#497881"/><path d="m65 45 34-28" stroke="#70efbd" stroke-width="2"/><circle cx="65" cy="45" r="3" fill="#70efbd"/><path d="M65 10a35 35 0 0 1 35 35" stroke="#70efbd" stroke-width="2"/></svg></header><div id="page">${page()}</div></main></div>`;
  if (state.route === 'research') renderResults();
  if (state.route === 'batch') renderQueue();
}
function page() {
  if (state.route === 'research') return researchPage();
  if (state.route === 'batch') return batchPage();
  if (state.route === 'compare') return comparePage();
  if (state.route === 'history') return historyPage();
  if (state.route === 'favorites') return favoritesPage();
  if (state.route === 'settings') return privacyPage();
  if (state.route === 'sources') return sourcesPage();
  return updatesPage();
}
function metrics() {
  const report = state.report, count = report?.sources.reduce((n, s) => n + Object.keys(s.fields).length, 0) ?? 0;
  return `<div class="metrics"><div class="metric"><span class="number">${report ? report.sources.filter(s => s.status === 'ok').length + '/' + report.sources.length : '—'}</span><span>${e(t('source'))}</span></div><div class="metric"><span class="number">${count.toString().padStart(2, '0')}</span><span>${e(t('fields'))}</span></div><div class="metric"><span class="number">${report ? (report.elapsedMs / 1000).toFixed(1) : '0.0'}s</span><span>${e(t('elapsed'))}</span></div></div>`;
}
function researchPage() {
  return `${metrics()}<div class="workspace-grid"><section class="panel query-panel"><header class="panel-heading"><span class="kicker">01 / ${e(t('target'))}</span></header><div class="panel-body"><div><label for="tool">${e(t('tool'))}</label><select id="tool">${Object.keys(TOOLS).map(key => `<option value="${key}" ${key === state.tool ? 'selected' : ''} ${state.meta && !state.meta.tools.includes(key) ? 'disabled' : ''}>${e(tl(key))}${state.meta && !state.meta.tools.includes(key) ? ' · ' + e(t('available_local')) : ''}</option>`).join('')}</select></div><div><label for="target">${e(t('target'))}</label><input id="target" type="text" autocomplete="off" spellcheck="false" value="${e(state.target)}" placeholder="${e(TOOLS[state.tool].example)}" maxlength="4096"></div>${state.tool === 'phone' ? `<div><label for="region">${e(t('region'))}</label><input id="region" value="${e(state.region)}" maxlength="2"></div>` : ''}${state.tool === 'domestic' ? `<div><label for="platform">${e(t('platform'))}</label><select id="platform">${['Auto', 'Douyin', 'Xiaohongshu', 'Kuaishou', 'Bilibili', 'Weibo', 'Zhihu', 'Douban'].map(p => `<option ${state.platform === p ? 'selected' : ''}>${p}</option>`).join('')}</select></div>` : ''}<div class="button-row">${button('example', 'example', 'small ghost')}${button('favorite', 'favorite', 'small ghost')}</div><div class="button-row query-actions">${button('query', 'query', 'primary', state.busy || state.queueRunning || !state.meta ? 'disabled' : '')}${button('cancel', 'cancel', '', state.busy ? '' : 'disabled')}</div><p id="query-message" class="query-status" role="status">${e(t(state.message))}</p><div class="form-note note">${e(t('source_note'))}${state.meta?.runtime === 'hosted' ? `<div class="runtime-note">${e(t('scope_note'))}</div>` : ''}</div></div></section><section class="panel results-panel"><header class="panel-heading"><span class="kicker">02 / ${e(t('interpretation'))}</span>${state.report ? button('retry', 'retry', 'small ghost') : ''}</header>${state.report ? `<div class="result-status"><code>${e(state.report.target)}</code><span>${e(date(state.report.at))}</span></div><div class="toolbar"><input id="filter" value="${e(state.filter)}" placeholder="${e(t('filter'))}" aria-label="${e(t('filter'))}">${button('copy-all', 'copy_all', 'small')}${button('save', 'save', 'small')}${button('export', 'export', 'small')}</div><div class="tabs" role="tablist"><button role="tab" aria-selected="${state.tab === 'observations'}" data-tab="observations" class="${state.tab === 'observations' ? 'active' : ''}">${e(t('observations'))}</button><button role="tab" aria-selected="${state.tab === 'fields'}" data-tab="fields" class="${state.tab === 'fields' ? 'active' : ''}">${e(t('fields'))}</button></div>` : ''}<div id="result-content"></div></section></div>`;
}
function renderResults() {
  const target = $('#result-content'); if (!target) return;
  const report = state.report;
  if (!report) { target.innerHTML = empty(); return; }
  if (state.tab === 'observations') {
    const items = findings(report);
    const list = items.filter(f => !state.filter || `${t(f.id, f.detail)} ${f.source}`.toLowerCase().includes(state.filter.toLowerCase()));
    target.innerHTML = `<div class="panel-body"><div class="chips">${report.sources.map(s => `<span class="chip ${e(s.status)}">${e(s.id)} / ${e(t(s.status))}</span>`).join('')}</div><div class="finding-list report-note">${list.length ? list.map((f, i) => `<article class="finding ${f.level}"><div class="finding-top">${badge(f.level)}<span class="mono tiny muted">${e(f.source)}</span></div><p>${e(t(f.id, f.detail))}</p>${f.detail.error ? `<p class="note">${e(errorText(f.detail.error))}</p>` : ''}<button type="button" class="small ghost" data-action="evidence" data-index="${items.indexOf(f)}">${e(t('evidence'))} →</button></article>`).join('') : `<p class="note">${e(t(state.filter ? 'no_matches' : 'no_findings'))}</p>`}</div><p class="note report-note">${e(t('health_note'))}</p></div>`;
    return;
  }
  let total = 0;
  const groups = report.sources.map((s, sourceIndex) => {
    const entries = Object.entries(s.fields);
    const filtered = entries.filter(([key, value]) => !state.filter || `${key} ${fl(key)} ${value}`.toLowerCase().includes(state.filter.toLowerCase()));
    total += filtered.length;
    return `<section class="source-group" data-source="${e(s.id)}"><div class="source-title"><strong class="mono">${e(s.id)}</strong>${badge(s.status)}<span class="note">${Number.isFinite(s.elapsedMs) ? (s.elapsedMs / 1000).toFixed(1) + 's' : ''}</span>${sourceLink(s)}</div>${s.error ? `<p class="note">${e(errorText(s.error))}</p>` : ''}${filtered.map(([key, value]) => `<details class="field"><summary><strong>${e(fl(key))}</strong><button class="field-copy" type="button" data-action="copy-field" data-source="${sourceIndex}" data-field="${entries.findIndex(([k]) => k === key)}">${e(t('copy'))}</button></summary><pre class="field-value">${e(value === null ? '—' : value)}</pre><p class="explanation">${e(t(explain(key)))}</p></details>`).join('')}${!entries.length ? `<p class="note">${e(t('evidence_empty'))}</p>` : ''}</section>`;
  });
  target.innerHTML = `<div class="panel-body">${state.filter && !total ? `<p class="note">${e(t('no_matches'))}</p>` : groups.join('')}</div>`;
}
function batchPage() {
  return `<p class="section-intro">${e(t('batch_note'))}</p><div class="two-columns"><section class="panel"><header class="panel-heading"><h2>${e(t('batch'))}</h2><span class="chip">MAX 50</span></header><div class="panel-body"><div class="file-actions">${button('import-domains', 'import_domains', 'small ghost')}</div><textarea class="batch-text" id="batch-text" aria-label="${e(t('batch'))}" placeholder="python.org&#10;example.com">${e(state.batchText)}</textarea><div class="button-row query-actions">${button('start-batch', 'start_batch', 'primary', state.queueRunning || state.busy || !state.meta ? 'disabled' : '')}${state.queueRunning ? button('pause-batch', state.paused ? 'resume' : 'pause') + button('stop-batch', 'cancel') : button('retry-batch', 'retry_failed', '', !state.queue.some(x => ['error', 'partial', 'cancelled'].includes(x.status)) ? 'disabled' : '')}</div><p class="note">${e(t('snapshot_note'))}</p></div></section><section class="panel"><header class="panel-heading"><h2>${e(t('status'))}</h2>${button('export-batch', 'batch_export', 'small', !state.queue.some(x => x.report) ? 'disabled' : '')}</header><div id="queue-content"></div></section></div>`;
}
function renderQueue() {
  if (!$('#queue-content')) return;
  const exportButton = document.querySelector('[data-action="export-batch"]');
  if (exportButton) exportButton.disabled = !state.queue.some(item => item.report);
  const done = state.queue.filter(x => !['queued', 'running'].includes(x.status)).length;
  $('#queue-content').innerHTML = `<div class="panel-body"><p class="mono muted">${done} / ${state.queue.length} ${state.paused ? '· ' + e(t('paused')) : ''}</p><progress max="${state.queue.length || 1}" value="${done}" aria-label="${e(t('status'))}"></progress></div>${!state.queue.length ? empty('batch', 'batch_note') : `<div class="table-scroll"><table><thead><tr><th>#</th><th>${e(t('target'))}</th><th>${e(t('status'))}</th><th></th></tr></thead><tbody>${state.queue.map((item, i) => `<tr><td class="muted mono">${String(i + 1).padStart(2, '0')}</td><td class="queue-target"><code>${e(item.target)}</code>${item.error ? `<p class="note">${e(errorText(item.error))}</p>` : ''}</td><td>${badge(item.status)}</td><td>${item.report ? button('open-queue', 'load', 'small ghost', `data-index="${i}"`) : ''}</td></tr>`).join('')}</tbody></table></div>`}`;
}
function optionsHTML(selected) { return state.saved.snapshots.map((r, i) => `<option value="${i}" ${i === selected ? 'selected' : ''}>${e(r.target)} · ${e(tl(r.tool))} · ${e(date(r.at))}</option>`).join(''); }
function comparePage() {
  const result = state.comparison;
  return `<p class="section-intro">${e(t('compare_note'))}</p><section class="panel"><div class="panel-body"><div class="select-row"><div><label for="before">${e(t('before'))}</label><select id="before">${optionsHTML(Math.min(1, state.saved.snapshots.length - 1))}</select></div><div><label for="after">${e(t('after'))}</label><select id="after">${optionsHTML(0)}</select></div></div><label class="checkbox"><input type="checkbox" id="ignore-ttl" checked>${e(t('ignore_ttl'))}</label><div class="button-row">${button('compare', 'compare_action', 'primary', state.saved.snapshots.length < 2 ? 'disabled' : '')}${result ? button('export-comparison', 'export') : ''}</div></div>${result ? `<div class="panel-heading"><code>${e(result.target)}</code><span class="chip">${result.changes.length} Δ</span></div><div class="table-scroll"><table><thead><tr><th>${e(t('source'))}</th><th>${e(t('fields'))}</th><th>${e(t('status'))}</th><th>${e(t('before'))}</th><th>${e(t('after'))}</th></tr></thead><tbody>${result.changes.map(c => `<tr><td>${e(c.source)}</td><td>${e(fl(c.field))}</td><td>${badge(c.kind)}</td><td><pre>${e(c.before ?? '—')}</pre></td><td><pre>${e(c.after ?? '—')}</pre></td></tr>`).join('')}</tbody></table></div><div class="panel-body">${!result.changes.length ? `<p>${e(t('unchanged'))}</p>` : ''}${result.skipped.length ? `<p class="note">${e(t('skipped'))}: ${e(result.skipped.join(', '))}</p>` : ''}</div>` : empty('compare', state.saved.snapshots.length < 2 ? 'no_snapshots' : 'compare_note')}</section>`;
}
function historyPage() {
  return `<p class="section-intro">${e(t('snapshot_note'))}</p><div class="view-tools">${button('import-snapshot', 'import', 'ghost')}</div><section class="panel">${state.saved.snapshots.length ? state.saved.snapshots.map((r, i) => `<article class="record-card"><div><strong>${e(r.target)}</strong><p class="note">${e(tl(r.tool))} · ${e(date(r.at))}</p></div><div class="button-row">${button('open-snapshot', 'load', 'small', `data-index="${i}"`)}${button('rerun-snapshot', 'rerun', 'small ghost', `data-index="${i}"`)}${button('export-snapshot', 'export', 'small ghost', `data-index="${i}"`)}${button('delete-snapshot', 'delete', 'small ghost danger', `data-index="${i}"`)}</div></article>`).join('') : empty('no_snapshots', 'snapshot_note')}</section>`;
}
function favoritesPage() {
  return `<p class="section-intro">${e(t('favorite_note'))}</p><section class="panel">${state.saved.favorites.length ? state.saved.favorites.map((f, i) => `<article class="record-card"><div><strong>${e(f.target)}</strong><p class="note">${e(tl(f.tool))} · ${e(f.region ?? 'CN')} / ${e(f.platform ?? 'Auto')}</p></div><div class="button-row">${button('run-favorite', 'load', 'small', `data-index="${i}"`)}${button('delete-favorite', 'delete', 'small ghost danger', `data-index="${i}"`)}</div></article>`).join('') : empty('no_favorites', 'favorite_note')}</section>`;
}
function privacyPage() {
  return `<section class="panel"><div class="panel-body"><h2>${e(t('privacy_title'))}</h2><p class="section-intro privacy-copy">${e(t('privacy_body'))}</p><ul class="privacy-list"><li><b>0</b><span>Analytics / Query database</span></li><li><b>${state.saved.snapshots.length}/50</b><span>${e(t('history'))}</span></li><li><b>${state.saved.favorites.length}/50</b><span>${e(t('favorites'))}</span></li></ul><p class="note">${e(t('snapshot_note'))}</p><p class="note report-note">${e(t('redaction_note'))}</p><div class="button-row query-actions">${button('clear-data', 'clear_data', 'danger ghost')}<a href="https://github.com/Serennity007/GhostTrack/blob/main/docs/PRIVACY.md" target="_blank" rel="noopener noreferrer">${e(t('docs'))} ↗</a></div></div></section>`;
}
function sourcesPage() {
  return `<p class="section-intro">${e(t('sources_note'))}</p><section class="panel">${state.report ? `<header class="panel-heading"><code>${e(state.report.target)}</code>${button('retry', 'retry', 'small')}</header>${state.report.sources.map(s => `<div class="record-card"><div><strong>${e(s.id)}</strong><p class="note">${e(date(state.report.at))} · ${s.elapsedMs ?? '—'} ms</p>${s.error ? `<p class="note">${e(errorText(s.error))}</p>` : ''}${sourceLink(s)}</div>${badge(s.status)}</div>`).join('')}` : empty('never_checked', 'sources_note')}</section>`;
}
function updatesPage() {
  const data = state.updates;
  return `<p class="section-intro">${e(t('updates_note'))}</p><section class="panel"><div class="panel-body"><span class="kicker">GHOSTTRACK / ATLAS</span><h2 class="section-intro">${e(t('current_version'))} · <span class="mono">${e(state.meta?.version ?? VERSION)}</span></h2>${button('check-updates', 'check_updates', 'primary', state.updateBusy ? 'disabled' : '')}${data?.checkedAt ? `<p class="note report-note">${e(t('checked_at'))}: ${e(date(data.checkedAt))}</p>` : ''}${data?.error ? `<p class="note report-note">${e(errorText(data.error))}</p>` : ''}</div>${data?.releases?.map(r => `<div class="record-card"><div><strong>${e(r.platform)} / ${e(r.version)}</strong>${r.platform === 'windows' && newer(r.version, state.meta?.version ?? VERSION) ? `<p class="note">${e(t('new_version'))}</p>` : ''}</div>${safeURL(r.url) ? `<a href="${e(safeURL(r.url))}" target="_blank" rel="noopener noreferrer">${e(t('release_page'))} ↗</a>` : ''}</div>`).join('') ?? ''}${data?.releases?.length === 0 ? `<div class="panel-body note">${e(t('no_releases'))}</div>` : ''}</section>`;
}
function newer(a, b) { const x = a.split('.').map(Number), y = b.split('.').map(Number); for (let i = 0; i < 3; i++) { if (x[i] !== y[i]) return x[i] > y[i]; } return false; }
function errorText(key) { const text = t(key); return text === key ? t('source_unavailable') : text; }
async function api(path, payload, signal) {
  let response;
  try { response = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-GhostTrack-Token': state.meta?.token ?? '' }, body: JSON.stringify(payload), signal }); }
  catch (error) { if (error.name === 'AbortError') throw error; throw new Error('network_error'); }
  let data;
  try { data = await response.json(); } catch { throw new Error('network_error'); }
  if (!response.ok) { const error = new Error(data.error ?? 'source_unavailable'); error.retry = Math.min(60, Math.max(1, Number(response.headers.get('Retry-After')) || 5)); error.status = response.status; throw error; }
  return data;
}
function configFrom(item) { state.tool = item.tool; state.target = item.target; state.region = item.region ?? 'CN'; state.platform = item.platform ?? 'Auto'; }
function cancelActive() {
  if (state.active) {
    const active = state.active; state.active = null; active.controller.abort();
    api('/api/cancel', { id: active.id }).catch(() => {});
  }
}
async function lookup(config, retryLimit = 0) {
  const id = crypto.randomUUID(), controller = new AbortController();
  const active = { id, controller }; state.active = active;
  try {
    for (let tries = 0; ; tries++) {
      try {
        const report = await api('/api/query', { ...config, id }, controller.signal);
        if (!validReport(report)) throw new Error('invalid_snapshot');
        if (state.active !== active) throw new DOMException('Cancelled', 'AbortError');
        return report;
      } catch (error) {
        if (error.status !== 429 || tries >= retryLimit) throw error;
        await delay(error.retry * 1000, controller.signal);
      }
    }
  } finally { if (state.active === active) state.active = null; }
}
function delay(ms, signal) {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) return reject(new DOMException('Cancelled', 'AbortError'));
    const timer = setTimeout(() => { signal?.removeEventListener('abort', abort); resolve(); }, ms);
    const abort = () => { clearTimeout(timer); reject(new DOMException('Cancelled', 'AbortError')); };
    signal?.addEventListener('abort', abort, { once: true });
  });
}
async function runQuery(item) {
  if (state.busy || state.queueRunning) return toast('busy');
  if (!state.meta) return toast('network_error');
  readForm(); if (item) configFrom(item);
  if (!state.meta.tools.includes(state.tool)) return toast('local_only');
  let target;
  try { target = normalizeTarget(state.tool, state.target); } catch (error) { return toast(error.message); }
  state.target = target; state.message = 'running'; state.busy = true; render();
  try { state.report = await lookup({ tool: state.tool, target, region: state.region, platform: state.platform }); state.filter = ''; state.message = 'completed'; }
  catch (error) { state.message = error.name === 'AbortError' ? 'cancelled' : 'failed'; if (error.name !== 'AbortError') toast(errorText(error.message), true); }
  finally { state.busy = false; render(); }
}
async function runQueue(retry = false) {
  if (state.busy || state.queueRunning) return toast('busy');
  readForm();
  if (!retry) {
    try { const targets = parseBatch(state.batchText); if (!targets.length) throw new Error('invalid_domain'); state.queue = targets.map(target => ({ target, status: 'queued' })); }
    catch (error) { return toast(error.message); }
  } else state.queue = state.queue.map(item => ['partial', 'error', 'cancelled'].includes(item.status) ? { target: item.target, status: 'queued' } : item);
  state.queueRunning = true; state.paused = false; state.stopQueue = false; render();
  try {
    for (const item of state.queue) {
      if (item.status !== 'queued') continue;
      while (state.paused && !state.stopQueue) await delay(150);
      if (state.stopQueue) break;
      item.status = 'running'; renderQueue();
      try {
        item.report = await lookup({ tool: 'overview', target: item.target, region: 'CN', platform: 'Auto' }, 2);
        const usable = item.report.sources.filter(s => s.status !== 'limited');
        item.status = usable.every(s => s.status === 'ok') ? 'ok' : usable.some(s => ['ok', 'partial'].includes(s.status)) ? 'partial' : 'error';
      } catch (error) { item.status = error.name === 'AbortError' ? 'cancelled' : 'error'; item.error = error.name === 'AbortError' ? 'cancelled' : error.message; }
      renderQueue();
      if (!state.stopQueue) await delay(1250);
    }
  } finally {
    if (state.stopQueue) for (const item of state.queue) if (item.status === 'queued') item.status = 'cancelled';
    state.queueRunning = false; state.paused = false; render();
  }
}
async function copy(value) {
  try { await navigator.clipboard.writeText(String(value)); toast('copied'); }
  catch { toast('copy_failed'); }
}
function saveSnapshot(report) {
  if (!report || !validReport(report)) return toast('invalid_snapshot');
  const snapshots = [structuredClone(report), ...state.saved.snapshots.filter(r => r.id !== report.id)].slice(0, 50);
  if (persist({ ...state.saved, snapshots })) { toast('saved'); render(); }
}
let exportData;
function reportWithAnalysis(value) {
  if (Array.isArray(value)) return value.map(reportWithAnalysis);
  if (!value.sources) return value;
  return { ...value, analysis: { language: state.language, notice: t('health_note'),
    observations: findings(value).map(item => ({ ...item, explanation: t(item.id, item.detail) })) } };
}
function showExport(report) {
  if (!report) return;
  exportData = reportWithAnalysis(report);
  const dialog = $('#export-dialog');
  dialog.innerHTML = `<header><h2 id="export-title">${e(t('redaction'))}</h2>${button('close-export', 'close', 'small ghost')}</header><div class="dialog-body"><div class="export-layout"><div class="controls">${[['target', 'redact_target'], ['ip', 'redact_ip'], ['phone', 'redact_phone'], ['parameters', 'redact_parameters']].map(([key, label]) => `<label class="checkbox"><input type="checkbox" data-redact="${key}" checked>${e(t(label))}</label>`).join('')}<label for="export-format">${e(t('format'))}</label><select id="export-format"><option value="json">JSON</option><option value="csv">CSV · UTF-8 BOM</option><option value="html">HTML · offline</option></select><p class="note report-note">${e(t('redaction_note'))}</p><div class="query-actions">${button('download-export', 'download', 'primary')}</div></div><div><label>${e(t('preview'))} · JSON</label><pre id="export-preview" class="export-preview" tabindex="0"></pre></div></div></div>`;
  updateExportPreview(); dialog.showModal();
}
function redacted() { return redactReport(exportData, Object.fromEntries([...document.querySelectorAll('[data-redact]')].map(input => [input.dataset.redact, input.checked]))); }
function updateExportPreview() { if ($('#export-preview')) $('#export-preview').textContent = JSON.stringify(redacted(), null, 2); }
function downloadReport(report, format) {
  const data = exportContent(report, format), blob = new Blob([data.content], { type: data.type });
  const url = URL.createObjectURL(blob), anchor = document.createElement('a');
  anchor.href = url; anchor.download = `GhostTrack-Atlas-${new Date().toISOString().slice(0, 10)}.${format}`;
  document.body.append(anchor); anchor.click(); anchor.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}
document.addEventListener('click', async event => {
  const buttonNode = event.target.closest('button'); if (!buttonNode || buttonNode.disabled) return;
  if (buttonNode.dataset.view) { readForm(); state.route = buttonNode.dataset.view; render(); return; }
  if (buttonNode.dataset.tab) { state.tab = buttonNode.dataset.tab; render(); return; }
  const action = buttonNode.dataset.action, index = Number(buttonNode.dataset.index);
  if (action === 'example') { readForm(); state.target = TOOLS[state.tool].example; render(); $('#target')?.focus(); }
  if (action === 'query') await runQuery();
  if (action === 'retry') await runQuery(state.report ?? undefined);
  if (action === 'cancel') { cancelActive(); state.message = 'cancelled'; }
  if (action === 'copy-all') await copy(JSON.stringify(state.report, null, 2));
  if (action === 'copy-field') { event.preventDefault(); const value = Object.entries(state.report.sources[Number(buttonNode.dataset.source)].fields)[Number(buttonNode.dataset.field)]?.[1]; await copy(value ?? '—'); }
  if (action === 'save') saveSnapshot(state.report);
  if (action === 'export') showExport(state.report);
  if (action === 'evidence') {
    const finding = findings(state.report)[index]; state.tab = 'fields'; state.filter = ''; render();
    const group = [...document.querySelectorAll('[data-source]')].find(node => node.dataset.source === finding.source);
    if (group) { group.querySelectorAll('details').forEach(node => { node.open = true; }); group.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  }
  if (action === 'favorite') {
    readForm(); let target; try { target = normalizeTarget(state.tool, state.target); } catch (error) { return toast(error.message); }
    const favorite = { id: crypto.randomUUID(), tool: state.tool, target, region: state.region, platform: state.platform };
    const favorites = [favorite, ...state.saved.favorites.filter(f => !(f.tool === favorite.tool && f.target === favorite.target && f.region === favorite.region && f.platform === favorite.platform))].slice(0, 50);
    if (persist({ ...state.saved, favorites })) toast('saved');
  }
  if (action === 'open-snapshot') { state.report = state.saved.snapshots[index]; configFrom(state.report); state.route = 'research'; state.filter = ''; render(); }
  if (action === 'rerun-snapshot') { const report = state.saved.snapshots[index]; state.route = 'research'; await runQuery(report); }
  if (action === 'export-snapshot') showExport(state.saved.snapshots[index]);
  if (action === 'delete-snapshot') { const snapshots = state.saved.snapshots.filter((_, i) => i !== index); if (persist({ ...state.saved, snapshots })) { state.comparison = null; render(); } }
  if (action === 'delete-favorite') { if (persist({ ...state.saved, favorites: state.saved.favorites.filter((_, i) => i !== index) })) render(); }
  if (action === 'run-favorite') { configFrom(state.saved.favorites[index]); state.route = 'research'; render(); $('#target')?.focus(); }
  if (action === 'compare') {
    const a = Number($('#before').value), b = Number($('#after').value);
    try { if (a === b) throw new Error('different_targets'); state.comparison = compareReports(state.saved.snapshots[a], state.saved.snapshots[b], { ignoreTTL: $('#ignore-ttl').checked }); render(); }
    catch (error) { toast(error.message); }
  }
  if (action === 'export-comparison') showExport(state.comparison);
  if (action === 'import-snapshot') $('#snapshot-file').click();
  if (action === 'import-domains') $('#batch-file').click();
  if (action === 'start-batch') await runQueue();
  if (action === 'retry-batch') await runQueue(true);
  if (action === 'pause-batch') { state.paused = !state.paused; readForm(); render(); }
  if (action === 'stop-batch') { state.stopQueue = true; state.paused = false; cancelActive(); }
  if (action === 'open-queue') { state.report = state.queue[index].report; configFrom(state.report); state.route = 'research'; state.filter = ''; render(); }
  if (action === 'export-batch') showExport(state.queue.filter(x => x.report).map(x => x.report));
  if (action === 'clear-data' && confirm(t('confirm_clear'))) {
    try { localStorage.removeItem(STORE); state.saved = { ...initialSaved, language: state.language }; state.comparison = null; toast('deleted'); render(); }
    catch { toast('storage_full'); }
  }
  if (action === 'close-export') $('#export-dialog').close();
  if (action === 'download-export') downloadReport(redacted(), $('#export-format').value);
  if (action === 'check-updates') {
    state.updateBusy = true; render();
    try { state.updates = await api('/api/updates', { id: crypto.randomUUID() }); }
    catch (error) { state.updates = { error: error.message }; }
    finally { state.updateBusy = false; render(); }
  }
});
document.addEventListener('change', event => {
  if (event.target.id === 'language') { readForm(); state.language = event.target.value; persist({ ...state.saved, language: state.language }); render(); }
  if (event.target.id === 'tool') { readForm(); state.target = ''; render(); }
  if (event.target.matches('[data-redact]')) updateExportPreview();
});
document.addEventListener('input', event => {
  if (event.target.id === 'filter') { state.filter = event.target.value; renderResults(); }
  if (event.target.id === 'batch-text') state.batchText = event.target.value;
});
document.addEventListener('keydown', event => {
  if (event.key === 'Enter' && event.target.id === 'target') { event.preventDefault(); runQuery(); }
  if (event.key === 'Escape' && state.busy && !$('#export-dialog').open) cancelActive();
});
$('#snapshot-file').addEventListener('change', async event => {
  try {
    const file = event.target.files[0]; if (!file) return;
    if (file.size > 600000) throw new Error();
    const report = JSON.parse(await file.text()); if (!validReport(report)) throw new Error();
    report.id = crypto.randomUUID(); saveSnapshot(report); toast('imported');
  } catch { toast('invalid_snapshot'); }
  finally { event.target.value = ''; }
});
$('#batch-file').addEventListener('change', async event => {
  try {
    const file = event.target.files[0]; if (!file) return;
    if (file.size > 100000) throw new Error();
    let lines = (await file.text()).replace(/^\uFEFF/, '').split(/\r?\n/).map(line => line.trim().replace(/^"([^"\r\n]*)"$/, '$1')).filter(Boolean);
    if (/^(domain|target|域名)$/i.test(lines[0])) lines.shift();
    const targets = parseBatch(lines.join('\n')); state.batchText = targets.join('\n'); render();
  } catch { toast('invalid_file'); }
  finally { event.target.value = ''; }
});
window.addEventListener('beforeunload', () => { state.stopQueue = true; state.active?.controller.abort(); });
render();
try {
  const response = await fetch('/api/meta', { cache: 'no-store' });
  if (!response.ok) throw new Error();
  const meta = await response.json();
  if (!Array.isArray(meta.tools) || !meta.version) throw new Error();
  state.meta = meta; render();
} catch { state.message = 'network_error'; render(); toast('network_error'); }
