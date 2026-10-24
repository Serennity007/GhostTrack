import test from 'node:test';
import assert from 'node:assert/strict';
import { cloudLookup, handle } from './cloud.mjs';
const signal = () => new AbortController().signal;
test('hosted mode reports TLS limits explicitly and preserves real independent source data', async () => {
  const old = globalThis.fetch;
  const requested = [];
  globalThis.fetch = async input => {
    const url = String(input); requested.push(url);
    if (url.includes('data.iana.org')) return Response.json({ services: [[['com'], ['https://rdap.verisign.com/com/v1/']]] });
    if (url.includes('rdap.org')) return Response.json({ ldhName: 'EXAMPLE.COM', nameservers: [{ ldhName: 'NS.EXAMPLE.COM' }], events: [{ eventAction: 'expiration', eventDate: '2030-01-01T00:00:00Z' }] });
    if (url.includes('dns.google')) return Response.json({ Status: 0, Answer: [{ name: 'example.com.', TTL: 300, data: '8.8.8.8' }] });
    throw new Error('Unexpected destination');
  };
  try {
    const data = await cloudLookup({ tool: 'overview', target: 'example.com', id: 'test' }, signal());
    assert.equal(data.sources.find(s => s.id === 'DNS').status, 'ok');
    assert.equal(data.sources.find(s => s.id === 'RDAP').fields.Expires, '2030-01-01T00:00:00Z');
    assert.equal(data.sources.find(s => s.id === 'HTTPS').status, 'limited');
    assert(!requested.some(url => new URL(url).hostname === 'example.com'));
  } finally { globalThis.fetch = old; }
});
test('arbitrary RDAP redirects are not followed and source failure is retained', async () => {
  const old = globalThis.fetch; const requested = [];
  globalThis.fetch = async input => { requested.push(String(input)); return new Response(null, { status: 302, headers: { Location: 'https://127.0.0.1/private' } }); };
  try {
    const data = await cloudLookup({ tool: 'network', target: '8.8.8.8', id: 'redirect-test' }, signal());
    assert.equal(data.sources[0].status, 'error');
    assert.equal(data.sources[0].error, 'source_redirect_blocked');
    assert.equal(requested.length, 1);
    assert(!JSON.stringify(data).includes('/private'));
  } finally { globalThis.fetch = old; }
});
test('private and documentation IP ranges are rejected without contacting a provider', async () => {
  const old = globalThis.fetch; globalThis.fetch = () => { throw new Error('MUST NOT CONTACT NETWORK'); };
  try {
    for (const target of ['127.0.0.1', '10.0.0.1', '169.254.169.254', '192.168.1.1', '203.0.113.3', '::1', '2001:db8::1']) {
      const data = await cloudLookup({ tool: 'network', target, id: 'private-test' }, signal());
      assert.equal(data.sources[0].error, 'public_address_only', target);
    }
  } finally { globalThis.fetch = old; }
});
test('API rejects cross-origin and oversized bodies, serves exact assets only', async () => {
  const origin = 'https://atlas.example';
  const cross = new Request(origin + '/api/query', { method: 'POST', headers: { Origin: 'https://evil.example', 'Content-Type': 'application/json' }, body: '{}' });
  assert.equal((await handle(cross, {})).status, 403);
  const large = new Request(origin + '/api/query', { method: 'POST', headers: { Origin: origin, 'Content-Type': 'application/json' }, body: ' '.repeat(9000) });
  assert.equal((await handle(large, {})).status, 400);
  assert.equal((await handle(new Request(origin + '/secrets'), {})).status, 404);
  const response = await handle(new Request(origin + '/'), { '/': { body: '<h1>Atlas</h1>', type: 'text/html' } });
  assert.equal(response.status, 200);
  assert.match(response.headers.get('Content-Security-Policy'), /object-src 'none'/);
});
test('metadata advertises only supported tools; username links never query profiles', async () => {
  const meta = await (await handle(new Request('https://atlas.example/api/meta'), {})).json();
  assert(!meta.tools.includes('website') && !meta.tools.includes('phone'));
  const old = globalThis.fetch; globalThis.fetch = () => { throw new Error('No profile verification permitted'); };
  try {
    const result = await cloudLookup({ tool: 'username', target: 'octocat', id: 'generated' }, signal());
    assert.equal(result.sources[0].fields.GitHub, 'https://github.com/octocat');
    assert.match(result.sources[0].fields.Note, /unverified/);
  } finally { globalThis.fetch = old; }
});
