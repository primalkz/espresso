// refresh tokens/tokens.json from a frappe-ui checkout
// usage: node tokens/sync-upstream.mjs [path-to-frappe-ui]
import fs from 'node:fs'
import path from 'node:path'
import { execFileSync } from 'node:child_process'
import { pathToFileURL } from 'node:url'

const root = process.argv[2] || path.join(process.env.HOME, 'src/frappe-ui')
const load = async (p) => (await import(pathToFileURL(path.join(root, p)).href)).default

const [colors, effects, radius, typography] = await Promise.all([
  load('tailwind/tokens/colors.js'),
  load('tailwind/tokens/effects.js'),
  load('tailwind/tokens/radius.js'),
  load('tailwind/tokens/typography.js'),
])

let commit = 'unknown'
try {
  commit = execFileSync('git', ['-C', root, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).trim()
} catch {}

const out = { provenance: { repo: 'frappe/frappe-ui', commit, synced: new Date().toISOString().slice(0, 10) },
  colors, effects, radius, typography }
const here = path.dirname(new URL(import.meta.url).pathname)
fs.writeFileSync(path.join(here, 'tokens.json'), JSON.stringify(out, null, 2) + '\n')
console.log(`wrote tokens.json from ${commit}`)
