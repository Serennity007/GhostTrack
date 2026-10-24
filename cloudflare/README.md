# Deploy Atlas to your Cloudflare account

This publishes the same hosted Atlas adapter directly to Cloudflare Workers, with a `workers.dev` URL. No database, API key, or application secret is needed at runtime. Your Cloudflare account authorization is required to create the Worker.

From the repository root, with Node.js installed:

```powershell
node cloudflare/build.mjs
npx --yes wrangler@4.152.0 deploy --config cloudflare/wrangler.jsonc --dry-run
npx --yes wrangler@4.152.0 login --scopes account:read user:read workers:write
npx --yes wrangler@4.152.0 deploy --config cloudflare/wrangler.jsonc
```

Complete login and authorization yourself in Cloudflare's browser page. Do not paste API tokens into an issue, chat, or configuration file. Wrangler manages its local credentials outside the checkout. If several accounts are returned, choose the intended account before publishing. If `ghosttrack-atlas` already exists in that account, verify it is this project before updating it, or change `name` in the config.

The requested application permissions are `account:read`, `user:read`, and `workers:write`. Wrangler also automatically adds `offline_access` so it can refresh its local login. Review that additional scope on Cloudflare's authorization page; do not approve it if you do not want persistent CLI login.

Use the exact URL returned by a successful deployment, not a guessed account subdomain. Verify anonymous page access, `/api/meta`, a real DNS/RDAP query, and report export before replacing existing links. Browser-local favorites and snapshots do not transfer automatically between the Sites URL and the new Workers origin.

The hosted capability limits remain unchanged: pinned arbitrary-target HTTPS/TLS, offline phone metadata, and Chinese public profiles use the local Python engine. See [the Atlas guide](../docs/atlas.md).

Reference: [Cloudflare Wrangler commands](https://developers.cloudflare.com/workers/wrangler/commands/).
