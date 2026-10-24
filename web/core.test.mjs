import test from 'node:test';
import assert from 'node:assert/strict';
import { findings, compareReports, redactReport, exportContent, normalizeTarget, parseBatch } from './core.mjs';
const report = (sources, extra = {}) => ({ schema: 1, version: '1.9.0', id: 'sample', tool: 'overview', target: 'example.com', region: 'CN', platform: 'Auto', at: '2026-10-24T10:11:12Z', sources, ...extra });
const source = (id, fields, status = 'ok') => ({ id, status, fields, url: 'https://example.com/?token=private-value' });

test('health observations preserve unknown evidence instead of claiming a pass', () => {
  const data = report([source('HTTPS', { 'HTTP status': 200, 'Certificate days remaining': 90 }, 'error'), source('DNS', { 'DNS A': 'ERROR', 'DNS AAAA': '—' }, 'partial')]);
  const values = findings(data);
  assert(!values.some(x => x.id === 'http_ok' || x.id === 'tls_valid' || x.id === 'dns_no_address'));
  assert(values.some(x => x.level === 'unknown'));
});
test('certificate and registry expiry are based on the recorded observation', () => {
  const values = findings(report([source('HTTPS', { 'HTTP status': 503, 'Certificate days remaining': 0 }), source('RDAP', { Expires: '2026-10-30T10:11:12Z' })]));
  assert(values.some(x => x.id === 'tls_expired' && x.level === 'critical'));
  assert(values.some(x => x.id === 'http_error' && x.detail.status === 503));
  assert(values.some(x => x.id === 'registration_expiry' && x.detail.days === 6));
});
test('DNS checks distinguish NXDOMAIN, no records, and mail-specific recommendations', () => {
  const nx = findings(report([source('DNS', { 'DNS A': 'NXDOMAIN', 'DNS AAAA': 'NXDOMAIN' })]));
  assert(nx.some(x => x.id === 'dns_nxdomain'));
  assert(!nx.some(x => x.id === 'dns_no_address'));
  assert(!findings(report([source('DNS', { 'DNS MX': '—', 'DNS TXT': '—' })])).some(x => x.id === 'dns_spf_review'));
  assert(findings(report([source('DNS', { 'DNS MX': '10 mx.example.com', 'DNS TXT': 'site-verification=example' })])).some(x => x.id === 'dns_spf_review' && x.level === 'info'));
});
test('comparison ignores observation timing, TTL countdown and DNS answer order', () => {
  const a = report([source('DNS', { 'DNS A': 'example.com. TTL=300 8.8.8.8\nexample.com. TTL=300 1.1.1.1', 'Response time ms': 20 })]);
  const b = report([source('DNS', { 'DNS A': 'example.com. TTL=250 1.1.1.1\nexample.com. TTL=250 8.8.8.8', 'Response time ms': 90 })], { at: '2026-10-24T11:00:00Z' });
  assert.equal(compareReports(a, b).changes.length, 0);
  assert.equal(compareReports(a, b, { ignoreTTL: false }).changes.length, 1);
});
test('failed or partial sources never imply deletion; real changes retain both values', () => {
  const a = report([source('DNS', { 'DNS A': '8.8.8.8', 'DNS MX': '10 mx.example.com' }), source('RDAP', { Registrar: 'Example A' })]);
  const b = report([source('DNS', {}, 'error'), source('RDAP', { Registrar: 'Example B' })]);
  const diff = compareReports(a, b);
  assert.deepEqual(diff.skipped, ['DNS']);
  assert.deepEqual(diff.changes.map(x => [x.source, x.before, x.after]), [['RDAP', 'Example A', 'Example B']]);
  assert.throws(() => compareReports(a, { ...b, target: 'other.example.com' }), /different_targets/);
  assert.throws(() => compareReports(a, { ...b, region: 'US' }), /different_targets/);
});
test('redaction removes secrets before target masking and preserves original and timestamp', () => {
  const data = report([source('HTTPS', { 'Connected address': '8.8.8.8', 'IPv6': '2001:4860:4860::8888', 'SPF': 'v=spf1 ip6:2a03:b0c0:2:d0::71:1 ~all', 'Phone': '+1 (202) 555-0123', 'Note': 'example.com on 2026-10-24 at 10:11:12', 'Expires': '2026-10-30T10:11:12Z', 'Strict-Transport-Security': 'max-age=31536000' })]);
  const original = JSON.stringify(data);
  const masked = redactReport(data, { target: true, ip: true, phone: true, parameters: true });
  const text = JSON.stringify(masked);
  for (const secret of ['example.com', '8.8.8.8', '2001:4860:4860::8888', '2a03:b0c0:2:d0::71:1', '555-0123', 'private-value']) assert(!text.includes(secret), secret);
  assert.equal(masked.at, data.at);
  assert.equal(masked.id, data.id);
  assert(text.includes('max-age=31536000'));
  assert(text.includes('2026-10-24') && text.includes('10:11:12'));
  assert.equal(JSON.stringify(data), original);
  assert.equal(redactReport([data, data], { target: true })[1].target, '[TARGET]');
  assert(!JSON.stringify(redactReport(report([source('RDAP', { Domain: 'EXAMPLE.COM' })]), { target: true })).toLowerCase().includes('example.com'));
  const withShare = report([source('PROFILE', { 'Source URL': 'https://example.com/profile/123?token=secret' })], { target: 'https://example.com/profile/123?token=secret' });
  assert(!JSON.stringify(redactReport(withShare, { target: true, parameters: true })).includes('/profile/123'));
});
test('reports escape untrusted HTML, protect spreadsheet formulas and retain partial errors', () => {
  const data = report([source('GITHUB', { Bio: '<img src=x onerror=alert(1)>', Formula: ' =HYPERLINK("bad")' }, 'partial')],
    { analysis: { notice: 'Observed data only', observations: [{ source: 'GITHUB', level: 'unknown', explanation: 'Partial source: review fields', fields: ['Bio'] }] } });
  const html = exportContent(data, 'html').content;
  assert(!html.includes('<img src=x'));
  assert(html.includes('&lt;img'));
  assert(html.includes('Partial source: review fields'));
  const csv = exportContent(data, 'csv').content;
  assert(csv.startsWith('\uFEFF'));
  assert(csv.includes("' =HYPERLINK"));
  assert(csv.includes('Observed data only'));
  assert(JSON.parse(exportContent(data, 'json').content).sources[0].status === 'partial');
});
test('batch parsing normalizes IDNs and deduplicates before requests; invalid rows reject batch', () => {
  assert.deepEqual(parseBatch('PYTHON.ORG\nhttps://python.org/\nexample.com'), ['python.org', 'example.com']);
  assert.throws(() => parseBatch('python.org\nlocalhost'), /invalid_domain/);
  assert.throws(() => parseBatch(Array.from({ length: 51 }, (_, i) => `d${i}.example.com`).join('\n')), /batch_limit/);
  assert.equal(normalizeTarget('github', 'https://github.com/Octocat'), 'octocat');
  assert.throws(() => normalizeTarget('overview', 'https://user:password@example.com'), /invalid_domain/);
  assert.throws(() => normalizeTarget('website', 'http://example.com'), /https_public_only/);
});
