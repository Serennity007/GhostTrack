// One self-contained, dependency-free bundle for both Sites and direct Workers.
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

export async function bundleWorker() {
  const source = fileURLToPath(new URL('.', import.meta.url));
  const files = { '/': ['index.html', 'text/html; charset=utf-8'], '/style.css': ['style.css', 'text/css; charset=utf-8'],
    '/app.mjs': ['app.mjs', 'text/javascript; charset=utf-8'], '/core.mjs': ['core.mjs', 'text/javascript; charset=utf-8'], '/lang.mjs': ['lang.mjs', 'text/javascript; charset=utf-8'] };
  const assets = {};
  for (const [path, [file, type]] of Object.entries(files)) assets[path] = { body: await readFile(join(source, file), 'utf8'), type };
  const core = await readFile(join(source, 'core.mjs'), 'utf8');
  const adapter = (await readFile(join(source, 'cloud.mjs'), 'utf8')).replace(/^import[^\n]+\n/, '');
  return core + '\n' + adapter + '\nconst ASSETS = ' + JSON.stringify(assets) + ';\nexport default { async fetch(request, env, ctx) { return handle(request, ASSETS); } };\n';
}
