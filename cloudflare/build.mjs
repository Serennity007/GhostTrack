import { mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { bundleWorker } from '../web/bundle_worker.mjs';

const folder = dirname(fileURLToPath(import.meta.url));
await mkdir(folder, { recursive: true });
await writeFile(join(folder, 'worker.mjs'), await bundleWorker(), 'utf8');
console.log('Built Cloudflare Worker: cloudflare/worker.mjs');
