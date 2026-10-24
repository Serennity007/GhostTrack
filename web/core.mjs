// Deterministic interpretation and report handling, shared by the browser and tests.
export const VERSION = '1.9.0';
export const TOOLS = {
  overview: { label: 'Domain overview', example: 'python.org', kind: 'domain' },
  dns: { label: 'DNS records', example: 'example.com', kind: 'domain' },
  domain: { label: 'Domain registration', example: 'example.com', kind: 'domain' },
  website: { label: 'Website + TLS', example: 'https://www.python.org/', kind: 'website' },
  network: { label: 'IP / ASN registration', example: 'AS15169', kind: 'network' },
  github: { label: 'GitHub public profile', example: 'octocat', kind: 'github' },
  phone: { label: 'Offline phone metadata', example: '+12025550123', kind: 'phone' },
  username: { label: 'Unverified username links', example: 'octocat', kind: 'username' },
  location: { label: 'IP database estimate', example: '8.8.8.8', kind: 'network' },
  domestic: { label: 'Chinese public profiles', example: 'https://space.bilibili.com/2', kind: 'profile' },
};
export function normalizeTarget(tool, value) {
  value = String(value ?? '').trim();
  if (!Object.hasOwn(TOOLS, tool) || !value || value.length > 4096) throw new Error('invalid_input');
  if (['domain', 'dns', 'overview'].includes(tool)) {
    let host;
    try { const u = new URL(value.includes('://') ? value : `https://${value}`); if (!['http:', 'https:'].includes(u.protocol) || u.username || u.password) throw new Error(); host = u.hostname; }
    catch { throw new Error('invalid_domain'); }
    host = host.toLowerCase().replace(/\.$/, '');
    const labels = host.split('.');
    if (host.length > 253 || labels.length < 2 || /^(local|localhost|internal|lan|home|invalid|test|\d+)$/.test(labels.at(-1)) ||
        labels.some(x => !/^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$/.test(x))) throw new Error('invalid_domain');
    return host;
  }
  if (tool === 'github') {
    if (value.startsWith('https://github.com/')) {
      const u = new URL(value);
      if (u.search || u.hash || u.username || u.password) throw new Error('invalid_github');
      value = u.pathname.replace(/^\/+|\/+$/g, '');
    }
    if (!/^[a-z\d](?:[a-z\d-]{0,37}[a-z\d])?$/i.test(value)) throw new Error('invalid_github');
    return value.toLowerCase();
  }
  if (tool === 'website') {
    const u = new URL(value.includes('://') ? value : `https://${value}`);
    if (u.protocol !== 'https:' || u.username || u.password || u.hash || (u.port && u.port !== '443')) throw new Error('https_public_only');
    return u.href;
  }
  if (tool === 'network' && /^as\d+$/i.test(value)) return value.toUpperCase();
  if (tool === 'username' && (value.length > 100 || /\s/.test(value))) throw new Error('invalid_input');
  return value;
}
export function findings(report, now = Date.parse(report.at) || Date.now()) {
  const out = [];
  const add = (id, level, source, fields, detail = {}) => out.push({ id, level, source: source.id, fields, detail, url: source.url, checkedAt: report.at });
  for (const source of report.sources ?? []) {
    const f = source.fields ?? {};
    if (['error', 'limited', 'rate_limited', 'cancelled'].includes(source.status)) {
      add(source.status === 'rate_limited' ? 'rate_limited' : 'source_unknown', 'unknown', source, [], { error: source.error ?? source.status });
      continue;
    }
    if (source.status === 'partial') add('partial_source', 'unknown', source, []);
    if (source.id === 'DNS') {
      const empty = v => v === '—' || v === '' || v == null;
      const known = k => Object.hasOwn(f, k) && !['ERROR', 'NXDOMAIN'].includes(f[k]);
      if (Object.values(f).includes('NXDOMAIN')) add('dns_nxdomain', 'warning', source, Object.keys(f).filter(k => f[k] === 'NXDOMAIN'));
      else if (known('DNS A') && known('DNS AAAA')) add(empty(f['DNS A']) && empty(f['DNS AAAA']) ? 'dns_no_address' : 'dns_address', empty(f['DNS A']) && empty(f['DNS AAAA']) ? 'warning' : 'pass', source, ['DNS A', 'DNS AAAA']);
      if (known('DNS NS')) add(empty(f['DNS NS']) ? 'dns_no_ns' : 'dns_ns', empty(f['DNS NS']) ? 'info' : 'pass', source, ['DNS NS']);
      if (known('DNS MX') && !empty(f['DNS MX']) && known('DNS TXT') && !/v=spf1/i.test(f['DNS TXT'])) add('dns_spf_review', 'info', source, ['DNS MX', 'DNS TXT']);
      if (known('DNS CAA') && empty(f['DNS CAA'])) add('dns_caa_review', 'info', source, ['DNS CAA']);
    }
    if (source.id === 'HTTPS') {
      const status = Number(f['HTTP status']);
      if (Number.isFinite(status) && status > 0) add(status >= 400 ? 'http_error' : 'http_ok', status >= 400 ? 'warning' : 'pass', source, ['HTTP status'], { status });
      const days = f['Certificate days remaining'];
      if (days !== null && days !== undefined && Number.isFinite(Number(days))) add(Number(days) <= 0 ? 'tls_expired' : Number(days) <= 14 ? 'tls_expiring' : 'tls_valid', Number(days) <= 0 ? 'critical' : Number(days) <= 14 ? 'warning' : 'pass', source, ['Certificate days remaining', 'Certificate expires'], { days: Number(days) });
      const chain = String(f['Redirect chain'] ?? '').split('\n').filter(Boolean);
      if (chain.length >= 3) add('redirect_review', 'info', source, ['Redirect chain'], { count: chain.length - 1 });
      for (const header of ['Strict-Transport-Security', 'Content-Security-Policy', 'X-Content-Type-Options', 'Referrer-Policy']) {
        if (Object.hasOwn(f, header) && (f[header] === '—' || !f[header])) add('header_review', 'info', source, [header], { header });
      }
    }
    if (source.id === 'RDAP' && f['Expires']) {
      const remaining = (Date.parse(f['Expires']) - now) / 86400000;
      if (Number.isFinite(remaining) && remaining <= 30) add('registration_expiry', remaining <= 0 ? 'warning' : 'info', source, ['Expires'], { days: Math.ceil(remaining) });
    }
    if (source.id === 'USERNAME') add('unverified_links', 'info', source, Object.keys(f));
    if (source.id === 'LOCATION' || source.id === 'PHONE') add('estimate_only', 'info', source, []);
    if (source.id === 'PROFILE') add('profile_limits', 'info', source, []);
  }
  return out;
}
const VOLATILE = new Set(['Query status', 'Query time UTC', 'Response time ms', 'Elapsed ms', 'Source URL', 'Certificate days remaining']);
function comparable(key, value, ignoreTTL) {
  let text = String(value ?? '');
  if (key.startsWith('DNS ')) {
    if (ignoreTTL) text = text.replace(/TTL=\d+/g, 'TTL=*');
    text = text.split('\n').map(x => x.trim()).filter(Boolean).sort().join('\n');
  }
  return text;
}
export function compareReports(before, after, { ignoreTTL = true } = {}) {
  if (before.tool !== after.tool || normalizeTarget(before.tool, before.target) !== normalizeTarget(after.tool, after.target) ||
      (before.platform ?? 'Auto') !== (after.platform ?? 'Auto') || (before.region ?? 'CN') !== (after.region ?? 'CN')) throw new Error('different_targets');
  const changes = [], skipped = [];
  const ids = new Set([...(before.sources ?? []).map(s => s.id), ...(after.sources ?? []).map(s => s.id)]);
  for (const id of ids) {
    const a = before.sources.find(s => s.id === id), b = after.sources.find(s => s.id === id);
    if (!a || !b || a.status !== 'ok' || b.status !== 'ok') { skipped.push(id); continue; }
    const keys = new Set([...Object.keys(a.fields), ...Object.keys(b.fields)]);
    for (const key of keys) {
      if (VOLATILE.has(key)) continue;
      if (comparable(key, a.fields[key], ignoreTTL) === comparable(key, b.fields[key], ignoreTTL)) continue;
      changes.push({ source: id, field: key, kind: !Object.hasOwn(a.fields, key) ? 'added' : !Object.hasOwn(b.fields, key) ? 'removed' : 'changed', before: a.fields[key] ?? null, after: b.fields[key] ?? null });
    }
  }
  return { target: after.target, before: before.at, after: after.at, changes, skipped };
}
export function explain(key) {
  if (key.startsWith('DNS ')) return ({ A: 'dns_a', AAAA: 'dns_aaaa', CNAME: 'dns_cname', MX: 'dns_mx', NS: 'dns_ns_explain', TXT: 'dns_txt', SOA: 'dns_soa', CAA: 'dns_caa' })[key.slice(4)] ?? 'field_public';
  if (/Certificate|TLS/.test(key)) return 'certificate_explain';
  if (/HTTP status/.test(key)) return 'http_explain';
  if (/CIDR|address|Address|Network|ASN/.test(key)) return 'network_explain';
  if (/Expires|Registered|Updated|Registrar/.test(key)) return 'registration_explain';
  if (/Source URL/.test(key)) return 'source_explain';
  if (/Strict-|Policy|Options/.test(key)) return 'header_explain';
  return 'field_public';
}
export function parseBatch(text) {
  const lines = String(text).replace(/^\uFEFF/, '').split(/\r?\n/).map(x => x.trim()).filter(Boolean);
  if (lines.length > 50) throw new Error('batch_limit');
  return [...new Set(lines.map(x => normalizeTarget('overview', x)))];
}
function maskText(value, options, targets) {
  let text = String(value);
  if (options.parameters) text = text.replace(/https?:\/\/[^\s<>"']+/g, raw => {
    try { const u = new URL(raw); if (u.search) u.search = '?redacted'; u.hash = ''; return u.href; } catch { return raw; }
  });
  if (options.target) for (const target of targets.filter(Boolean).sort((a, b) => b.length - a.length)) text = text.replace(new RegExp(target.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'), '[TARGET]');
  if (options.ip) text = text.replace(/\bip6:([a-f\d:.]+)/gi, (raw, address) => {
    try { new URL(`https://[${address}]/`); return 'ip6:[IP]'; } catch { return raw; }
  }).replace(/(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])/g, '[IP]').replace(/(?<![\w:])(?:[a-f\d]{0,4}:){2,}[a-f\d:.]*(?![\w:])/gi, raw => {
    if (!raw.includes('::') && (raw.match(/:/g) ?? []).length < 3) return raw;
    try { new URL(`https://[${raw}]/`); return '[IP]'; } catch { return raw; }
  });
  if (options.phone) text = text.replace(/\+\d[\d ()-]{6,}\d|(?<!\w)(?:1[3-9]\d{9}|(?:\(\d{3}\)|\d{3})[ -]\d{3}[ -]\d{4})(?!\w)/g, '[NUMBER]');
  return text;
}
export function redactReport(report, options = {}) {
  if (Array.isArray(report)) return report.map(item => redactReport(item, options));
  const cloned = JSON.parse(JSON.stringify(report));
  const targets = [report.target];
  try { const u = new URL(report.target.includes('://') ? report.target : `https://${report.target}`); targets.push(u.hostname); u.search = ''; u.hash = ''; targets.push(u.href); } catch {}
  function visit(value, key = '') {
    if (['at', 'checkedAt', 'id'].includes(key)) return value;
    if (typeof value === 'string') {
      if ((options.ip && /^(IP|Connected address|Start address|End address|CIDR)$/.test(key)) || (options.phone && /phone|E\.164|International format|National format/i.test(key))) return '[REDACTED]';
      return maskText(value, options, targets);
    }
    if (Array.isArray(value)) return value.map(v => visit(v));
    if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([k, v]) => [maskText(k, options, targets), visit(v, k)]));
    return value;
  }
  const result = visit(cloned);
  result.redaction = { ...options, notice: 'Review before sharing; automatic redaction cannot recognize all personal data.' };
  return result;
}
export const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
function rows(report) {
  if (Array.isArray(report)) return report.flatMap((r, i) => rows(r).map(row => [String(i + 1), ...row]));
  if (report.changes) return [['Target', report.target], ['Before UTC', report.before], ['After UTC', report.after], ...report.changes.map(c => [c.source, c.field, c.kind, c.before, c.after]), ['Skipped sources', report.skipped.join(', ')]];
  return [['Tool', report.tool], ['Target', report.target], ['Query time UTC', report.at],
    ...(report.analysis?.notice ? [['Interpretation limits', report.analysis.notice]] : []),
    ...(report.analysis?.observations ?? []).map(item => ['Observation', item.level, item.source, item.explanation, (item.fields ?? []).join(', ')]),
    ...(report.sources ?? []).flatMap(s => [[s.id, 'Status', s.status], [s.id, 'Source URL', s.url ?? ''], ...Object.entries(s.fields ?? {}).map(([k, v]) => [s.id, k, v]), ...(s.error ? [[s.id, 'Error', s.error]] : [])]), ...(report.redaction ? [['Redaction', JSON.stringify(report.redaction)]] : [])];
}
export function exportContent(report, format) {
  if (format === 'json') return { type: 'application/json', content: JSON.stringify(report, null, 2) };
  const data = rows(report);
  if (format === 'csv') {
    const cell = v => { const s = String(v ?? ''); return '"' + (/^[\s\uFEFF]*[=+\-@]/.test(s) ? "'" + s : s).replace(/"/g, '""') + '"'; };
    return { type: 'text/csv;charset=utf-8', content: '\uFEFF' + data.map(row => row.map(cell).join(',')).join('\r\n') };
  }
  return { type: 'text/html;charset=utf-8', content: `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>GhostTrack Atlas report</title><style>body{font:15px system-ui;background:#0b121b;color:#e3eeed;max-width:1100px;margin:40px auto;padding:20px}h1{color:#70edbd}table{border-collapse:collapse;width:100%}td{border-bottom:1px solid #2b3d4d;padding:12px;vertical-align:top;white-space:pre-wrap;overflow-wrap:anywhere}small{color:#a8bbc6}@media print{body{color:#111;background:white}}</style><h1>GhostTrack Atlas</h1><small>Observed public data · review source status and query time. Estimates and links do not verify identity.</small><table>${data.map(row => '<tr>' + row.map(cell => '<td>' + escapeHTML(cell) + '</td>').join('') + '</tr>').join('')}</table></html>` };
}
