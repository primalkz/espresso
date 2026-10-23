// tokens.json -> gtk-2.0/gtkrc (palette only)
// gtk2 has no css so this is the smallest port that still looks espresso
import fs from 'node:fs'
import path from 'node:path'

const here = path.dirname(new URL(import.meta.url).pathname)
const theme = path.join(here, '..')
const data = JSON.parse(fs.readFileSync(path.join(here, 'tokens.json'), 'utf8'))
const { colors } = data

function srgb(v) {
  v = Math.max(0, Math.min(1, v))
  return v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(v, 1 / 2.4) - 0.055
}

function oklchToHex(value) {
  const m = value.match(/oklch\(\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)(?:\s*\/\s*([\d.]+))?\)/)
  if (!m) return '#000000'
  const [L, C, H] = [Number(m[1]), Number(m[2]), Number(m[3])]
  const h = (H * Math.PI) / 180
  const a = C * Math.cos(h)
  const b = C * Math.sin(h)
  const l = Math.pow(L + 0.3963377774 * a + 0.2158037573 * b, 3)
  const mm = Math.pow(L - 0.1055613458 * a - 0.0638541728 * b, 3)
  const s = Math.pow(L - 0.0894841775 * a - 1.291485548 * b, 3)
  const r = 4.0767416621 * l - 3.3077115913 * mm + 0.2309699292 * s
  const g = -1.2684380046 * l + 2.6097574011 * mm - 0.3413193965 * s
  const bb = -0.0041960863 * l - 0.7034186147 * mm + 1.707614701 * s
  const hex = [r, g, bb].map((v) => Math.round(srgb(v) * 255).toString(16).padStart(2, '0'))
  return `#${hex.join('')}`
}

const resolve = (ref) => {
  const [mode, family, step] = ref.split('/')
  if (mode === 'neutral') return colors.neutral[family]
  if (mode === 'overlay') return colors.overlay[family][step]
  return colors[mode][family][step]
}

const light = colors.themedVariables.light
const vars = {
  bg_color: light.surface.base,
  fg_color: light.ink['gray-8'],
  base_color: light.surface.base,
  text_color: light.ink['gray-8'],
  selected_bg_color: light.surface['blue-6'],
  selected_fg_color: light.ink.base,
  tooltip_bg_color: light.ink['gray-9'],
  tooltip_fg_color: light.surface.base,
  insensitive_fg_color: light.ink['gray-3'],
  insensitive_bg_color: light.surface['gray-1'],
  link_color: light.ink['blue-link'],
}

const lines = [
  '# generated from tokens.json by tokens/gen-gtk2.mjs do not edit',
  '',
  'gtk-color-scheme = "' + Object.entries(vars)
    .map(([k, v]) => `${k}:${oklchToHex(resolve(v))}`)
    .join('\\n') + '"',
  '',
  'style "espresso-default" {',
  '  xthickness = 1',
  '  ythickness = 1',
  '  GtkButton::inner-border = { 6, 6, 4, 4 }',
  '  GtkWidget::focus-line-width = 1',
  '  GtkWidget::focus-padding = 1',
  '}',
  '',
  'class "*" style "espresso-default"',
  '',
]

fs.mkdirSync(path.join(theme, 'gtk-2.0'), { recursive: true })
fs.writeFileSync(path.join(theme, 'gtk-2.0', 'gtkrc'), lines.join('\n'))
console.log('wrote gtk-2.0/gtkrc')
