import { normalizeTarget, VERSION } from './core.mjs';

const KINDS = ['overview', 'dns', 'domain', 'network', 'github', 'username', 'location'];
const calls = new Map(), running = new Map();
let bootstrapCache;
class SourceError extends Error { constructor(code) { super(code); this.code = code; } }
function publicIP(value) {
  if (/^(?:\d{1,3}\.){3}\d{1,3}$/.test(value)) {
    const p = value.split('.').map(Number);
    if (p.some(n => n > 255) || value.split('.').some(n => n.length > 1 && n.startsWith('0'))) return false;
    const [a, b, c] = p;
    return !(a === 0 || a === 10 || a === 127 || a >= 224 || (a === 100 && b >= 64 && b <= 127) ||
      (a === 169 && b === 254) || (a === 172 && b >= 16 && b <= 31) ||
      (a === 192 && (b === 0 || b === 168 || (b === 88 && c === 99))) ||
      (a === 198 && (b === 18 || b === 19 || (b === 51 && c === 100))) || (a === 203 && b === 0 && c === 113));
  }
  try {
    const host = new URL(`https://[${value}]/`).hostname.slice(1, -1);
    return /^[23]/.test(host) && !/^(2001:(?:db8|0|2|10|20):|2002:)/i.test(host);
  } catch { return false; }
}
async function jsonURL(url, signal, allowedHosts, redirects = 0) {
  const u = new URL(url);
  if (u.protocol !== 'https:' || u.port || u.username || u.password || !allowedHosts.has(u.hostname)) throw new SourceError('source_redirect_blocked');
  const response = await fetch(u, { signal: AbortSignal.any([signal, AbortSignal.timeout(12000)]), redirect: 'manual', headers: { Accept: 'application/json', 'User-Agent': 'GhostTrack-Atlas/1.9 public-resource-research' } });
  if ([301, 302, 303, 307, 308].includes(response.status)) {
    await response.body?.cancel();
    if (redirects >= 3 || !response.headers.get('Location')) throw new SourceError('redirect_limit');
    return jsonURL(new URL(response.headers.get('Location'), u).href, signal, allowedHosts, redirects + 1);
  }
  if (!response.ok) { await response.body?.cancel(); throw new SourceError(response.status === 429 || response.status === 403 ? 'public_rate_limit' : response.status === 404 ? 'public_not_found' : 'source_unavailable'); }
  const reader = response.body?.getReader();
  if (!reader) throw new SourceError('source_unavailable');
  let length = 0; const parts = [];
  try {
    for (;;) {
      const chunk = await reader.read();
      if (chunk.done) break;
      length += chunk.value.length;
      if (length > 1048576) throw new SourceError('source_too_large');
      parts.push(chunk.value);
    }
  } finally { await reader.cancel().catch(() => {}); }
  const bytes = new Uint8Array(length); let offset = 0;
  for (const part of parts) { bytes.set(part, offset); offset += part.length; }
  try { return { data: JSON.parse(new TextDecoder().decode(bytes)), url: response.url || u.href }; }
  catch { throw new SourceError('invalid_source_response'); }
}
async function registration(target, network, signal) {
  let resource = 'domain', name = target;
  let hosts;
  if (network) {
    if (/^AS\d+$/i.test(target)) {
      const number = Number(target.slice(2));
      if (!Number.isInteger(number) || number <= 0 || number > 4294967295) throw new SourceError('invalid_asn');
      resource = 'autnum'; name = String(number);
    } else {
      if (!publicIP(target)) throw new SourceError('public_address_only');
      resource = 'ip';
    }
    hosts = new Set(['rdap.org', 'rdap.arin.net', 'rdap.db.ripe.net', 'rdap.apnic.net', 'rdap.afrinic.net', 'rdap.lacnic.net']);
  } else {
    if (!bootstrapCache || bootstrapCache.expires < Date.now()) {
      const { data } = await jsonURL('https://data.iana.org/rdap/dns.json', signal, new Set(['data.iana.org']));
      if (!Array.isArray(data.services)) throw new SourceError('invalid_source_response');
      bootstrapCache = { services: data.services, expires: Date.now() + 1800000 };
    }
    const tld = target.split('.').at(-1);
    const urls = bootstrapCache.services.find(entry => entry[0]?.includes(tld))?.[1] ?? [];
    // Hostnames come only from IANA's official bootstrap, never the user's URL.
    hosts = new Set(['rdap.org', ...urls.flatMap(value => {
      try { const u = new URL(value); return u.protocol === 'https:' && !u.port && !u.username && !u.password && /\.[a-z]+$/i.test(u.hostname) ? [u.hostname] : []; } catch { return []; }
    })]);
    if (hosts.size < 2) throw new SourceError('source_unavailable');
  }
  const { data, url } = await jsonURL(`https://rdap.org/${resource}/${encodeURIComponent(name)}`, signal, hosts);
  const fields = { 'Source URL': url, 'Registration status': (data.status ?? []).join(', ') || '—' };
  if (network) {
    Object.assign(fields, { 'Network name': data.name ?? null, 'Network handle': data.handle ?? null, 'Registration country code': data.country ?? null });
    if (resource === 'ip') Object.assign(fields, { IP: name, 'Start address': data.startAddress ?? null, 'End address': data.endAddress ?? null, 'IP version': data.ipVersion ?? null });
    else Object.assign(fields, { ASN: `AS${name}`, 'Start ASN': data.startAutnum, 'End ASN': data.endAutnum });
  } else {
    Object.assign(fields, { Domain: data.ldhName ?? target, Nameservers: (data.nameservers ?? []).slice(0, 20).map(x => x.ldhName).filter(Boolean).join('\n') || '—', 'DNSSEC delegation signed': data.secureDNS?.delegationSigned ?? null });
    const entity = (data.entities ?? []).find(x => x.roles?.includes('registrar'));
    const fn = entity?.vcardArray?.[1]?.find(x => x[0] === 'fn');
    if (fn && typeof fn[3] === 'string') fields.Registrar = fn[3];
  }
  for (const item of data.events ?? []) {
    const key = { registration: 'Registered', expiration: 'Expires', 'last changed': 'Updated' }[item.eventAction];
    if (key) fields[key] = item.eventDate;
  }
  return { fields, url };
}
async function dns(target, signal) {
  const fields = { Domain: target }, errors = [];
  // Two waves keep external concurrency bounded even for 8 record types.
  const types = ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SOA', 'CAA'];
  for (let i = 0; i < types.length; i += 4) await Promise.all(types.slice(i, i + 4).map(async type => {
    try {
      const { data } = await jsonURL(`https://dns.google/resolve?name=${encodeURIComponent(target)}&type=${type}`, signal, new Set(['dns.google']));
      if (![0, 3].includes(data.Status)) { fields[`DNS ${type}`] = 'ERROR'; errors.push(type); return; }
      const raw = data.Answer ?? [];
      const text = raw.slice(0, 20).map(r => `${r.name ?? ''}  TTL=${r.TTL ?? ''}  ${r.data ?? ''}`).join('\n');
      fields[`DNS ${type}`] = text ? text.slice(0, 6000) + (text.length > 6000 || raw.length > 20 ? '\n… [TRUNCATED]' : '') : data.Status === 3 ? 'NXDOMAIN' : '—';
    } catch (error) {
      if (signal.aborted) throw error;
      fields[`DNS ${type}`] = 'ERROR'; errors.push(type);
    }
  }));
  if (errors.length) fields['Failed record types'] = errors.join(', ');
  return { fields, status: errors.length === 8 ? 'error' : errors.length ? 'partial' : 'ok', error: errors.length === 8 ? 'source_unavailable' : undefined, url: `https://dns.google/query?name=${encodeURIComponent(target)}` };
}
async function github(target, signal) {
  const hosts = new Set(['api.github.com']);
  const { data, url } = await jsonURL(`https://api.github.com/users/${target}`, signal, hosts);
  const fields = { 'Source URL': url, 'Profile URL': `https://github.com/${target}`, Username: data.login, 'Display name': data.name, Bio: data.bio, 'Account type': data.type, 'Public repositories': data.public_repos, Followers: data.followers, Following: data.following, Registered: data.created_at, Updated: data.updated_at };
  let status = 'ok';
  try {
    const { data: repos } = await jsonURL(`https://api.github.com/users/${target}/repos?sort=updated&per_page=5`, signal, hosts);
    fields['Recent public repositories'] = repos.slice(0, 5).map(r => `${r.full_name} | ${r.language ?? '—'} | stars=${r.stargazers_count}\n${r.html_url}`).join('\n') || '—';
  } catch (error) { if (signal.aborted) throw error; status = 'partial'; }
  return { fields, url, status };
}
async function source(id, operation, signal) {
  const started = Date.now();
  try { return { id, status: 'ok', ...(await operation()), elapsedMs: Date.now() - started }; }
  catch (error) { return { id, status: signal.aborted ? 'cancelled' : error.code === 'public_rate_limit' ? 'rate_limited' : 'error', error: signal.aborted ? 'cancelled' : error.code ?? 'source_unavailable', fields: {}, elapsedMs: Date.now() - started }; }
}
export async function cloudLookup(payload, signal) {
  const tool = payload.tool;
  if (!KINDS.includes(tool)) throw new SourceError('local_only');
  const target = normalizeTarget(tool, payload.target), started = Date.now();
  let sources;
  if (tool === 'overview') sources = await Promise.all([
    source('RDAP', () => registration(target, false, signal), signal), source('DNS', () => dns(target, signal), signal),
    Promise.resolve({ id: 'HTTPS', status: 'limited', error: 'local_tls_required', fields: {} }),
  ]);
  else if (tool === 'dns') sources = [await source('DNS', () => dns(target, signal), signal)];
  else if (tool === 'domain' || tool === 'network') sources = [await source(tool === 'network' ? 'NETWORK' : 'RDAP', () => registration(target, tool === 'network', signal), signal)];
  else if (tool === 'github') sources = [await source('GITHUB', () => github(target, signal), signal)];
  else if (tool === 'location') sources = [await source('LOCATION', async () => {
    if (!publicIP(target)) throw new SourceError('public_address_only');
    const { data, url } = await jsonURL(`https://ipwho.is/${encodeURIComponent(target)}`, signal, new Set(['ipwho.is']));
    if (!data.success) throw new SourceError('source_unavailable');
    return { url, fields: { IP: data.ip, Country: data.country, Region: data.region, City: data.city, ISP: data.connection?.isp, Organization: data.connection?.org, ASN: data.connection?.asn, Timezone: data.timezone?.id, Note: 'Database estimate; not a live device location.' } };
  }, signal)];
  else sources = [{ id: 'USERNAME', status: 'ok', fields: { GitHub: `https://github.com/${encodeURIComponent(target)}`, Instagram: `https://www.instagram.com/${encodeURIComponent(target)}/`, X: `https://x.com/${encodeURIComponent(target)}`, Note: 'Generated links; account existence and ownership are unverified.' } }];
  return { schema: 1, version: VERSION, id: payload.id, tool, target, region: 'CN', platform: 'Auto', at: new Date().toISOString(), elapsedMs: Date.now() - started, runtime: 'hosted', sources };
}
async function updates(signal) {
  const { data } = await jsonURL('https://api.github.com/repos/Serennity007/GhostTrack/releases?per_page=30', signal, new Set(['api.github.com']));
  const releases = [];
  for (const platform of ['windows', 'android']) {
    const valid = data.filter(r => !r.draft && !r.prerelease && new RegExp(`^${platform}-v\\d+\\.\\d+\\.\\d+$`).test(r.tag_name));
    valid.sort((a, b) => { const x = a.tag_name.split('-v')[1].split('.').map(Number), y = b.tag_name.split('-v')[1].split('.').map(Number); return y[0] - x[0] || y[1] - x[1] || y[2] - x[2]; });
    if (valid[0] && valid[0].html_url?.startsWith('https://github.com/Serennity007/GhostTrack/releases/tag/')) releases.push({ platform, version: valid[0].tag_name.split('-v')[1], url: valid[0].html_url });
  }
  return { current: VERSION, releases, checkedAt: new Date().toISOString() };
}
function response(data, status = 200, type = 'application/json; charset=utf-8') {
  return new Response(typeof data === 'string' ? data : JSON.stringify(data), { status, headers: { 'Content-Type': type, 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer', 'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'self'", ...(status === 429 ? { 'Retry-After': '5' } : {}) } });
}
export async function handle(request, assets) {
  const u = new URL(request.url), path = u.pathname;
  if (request.method === 'GET' && path === '/api/meta') return response({ version: VERSION, runtime: 'hosted', tools: KINDS, token: '', website: false, limits: { batch: 50, requestsPerMinute: 60 } });
  if (request.method === 'GET' && Object.hasOwn(assets, path)) return response(assets[path].body, 200, assets[path].type);
  if (request.method !== 'POST' || !['/api/query', '/api/updates', '/api/cancel'].includes(path)) return response({ error: 'not_found' }, 404);
  if (request.headers.get('Origin') !== u.origin) return response({ error: 'invalid_origin' }, 403);
  if (request.headers.get('Content-Type')?.split(';')[0] !== 'application/json') return response({ error: 'json_required' }, 415);
  if (Number(request.headers.get('Content-Length') ?? 0) > 8192) return response({ error: 'invalid_input' }, 413);
  let payload;
  try {
    const reader = request.body?.getReader(); if (!reader) throw new Error();
    const chunks = []; let size = 0;
    try { for (;;) { const r = await reader.read(); if (r.done) break; size += r.value.length; if (size > 8192) throw new Error(); chunks.push(r.value); } }
    finally { await reader.cancel().catch(() => {}); }
    const buffer = new Uint8Array(size); let offset = 0; for (const chunk of chunks) { buffer.set(chunk, offset); offset += chunk.length; }
    payload = JSON.parse(new TextDecoder().decode(buffer));
    if (!payload || typeof payload !== 'object' || Array.isArray(payload) || typeof payload.id !== 'string' || !/^[a-z\d-]{1,80}$/i.test(payload.id)) throw new Error();
  } catch { return response({ error: 'invalid_input' }, 400); }
  const client = request.headers.get('oai-authenticated-user-id') ?? request.headers.get('CF-Connecting-IP') ?? 'anonymous';
  const key = `${client}:${payload.id}`;
  if (path === '/api/cancel') { const job = running.get(key); job?.abort(); return response({ cancelled: !!job }); }
  const now = Date.now();
  for (const [id, entry] of calls) if (now - entry.start > 60000) calls.delete(id);
  const bucket = calls.get(client) ?? { start: now, count: 0 };
  if (calls.size >= 1000 || bucket.count >= 60 || running.size >= 4 || running.has(key)) return response({ error: 'rate_limited' }, 429);
  bucket.count++; calls.set(client, bucket);
  const controller = new AbortController(); running.set(key, controller);
  const deadline = setTimeout(() => controller.abort(), 40000);
  try {
    return response(path === '/api/updates' ? await updates(controller.signal) : await cloudLookup(payload, controller.signal));
  } catch (error) { return response({ error: error.code ?? 'invalid_input' }, path === '/api/updates' ? 502 : 400); }
  finally { clearTimeout(deadline); running.delete(key); }
}
