// tokens.json -> gtk _tokens-light.css / _tokens-dark.css
// raw ramps stay unprefixed by mode so semantic aliases can cross reference
// usage: node tokens/gen-css.mjs
import fs from 'node:fs'
import path from 'node:path'

const here = path.dirname(new URL(import.meta.url).pathname)
const data = JSON.parse(fs.readFileSync(path.join(here, 'tokens.json'), 'utf8'))
const { colors, effects } = data


function srgb(v) {
  v = Math.max(0, Math.min(1, v))
  return v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(v, 1 / 2.4) - 0.055
}

function oklchToCss(value) {
  const m = value.match(/oklch\(\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)(?:\s*\/\s*([\d.]+))?\)/)
  if (!m) return value
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
  const rgb = [r, g, bb].map((v) => Math.round(srgb(v) * 255))
  const alpha = m[4] === undefined ? 1 : Number(m[4])
  if (alpha >= 1) return '#' + rgb.map((v) => v.toString(16).padStart(2, '0')).join('')
  return `rgba(${rgb[0]}, ${rgb[1]}, ${rgb[2]}, ${alpha})`
}

function resolveAliases(css) {
  const defs = new Map()
  for (const m of css.matchAll(/@define-color\s+(\w+)\s+([^;]+);/g)) defs.set(m[1], m[2].trim())
  const resolve = (name, seen = new Set()) => {
    const value = defs.get(name)
    if (!value || !value.startsWith('@') || seen.has(name)) return value || `@${name}`
    seen.add(name)
    return resolve(value.slice(1), seen)
  }
  return css.replace(/@define-color\s+(\w+)\s+@(\w+);/g,
    (_full, name) => `@define-color ${name} ${resolve(name)};`)
}

function hexToGtk3(css) {
  return css.replace(/#([0-9a-fA-F]{8})\b/g, (_m, h) => {
    const [r, g, b, a] = [0, 2, 4, 6].map((i) => parseInt(h.slice(i, i + 2), 16))
    return `rgba(${r}, ${g}, ${b}, ${(a / 255).toFixed(3)})`
  })
}

function toGtk3(css) {
  return hexToGtk3(css.replace(/oklch\([^)]+\)/g, oklchToCss))
}

const name = (s) => String(s).replace(/-/g, '_')
const raw = (mode, family, step) => colors[mode][family][step]
const resolve = (ref) => {
  const [mode, family, step] = ref.split('/')
  if (mode === 'neutral') return colors.neutral[family]
  if (mode === 'overlay') return colors.overlay[family][step]
  return colors[mode][family][step]
}

function rampLines(mode) {
  const out = []
  for (const [family, steps] of Object.entries(colors[mode])) {
    for (const [step, value] of Object.entries(steps))
      out.push(`@define-color es_${mode === 'lightMode' ? 'light' : 'dark'}_${name(family)}_${step} ${value};`)
  }
  return out
}

function semanticLines(mode) {
  const out = []
  const vars = colors.themedVariables[mode]
  for (const [group, entries] of Object.entries(vars)) {
    for (const [key, ref] of Object.entries(entries)) {
      const token = `es_${name(group)}_${name(key)}`
      out.push(`@define-color ${token} ${resolve(ref)};  /* ${ref} */`)
    }
  }
  return out
}

function gtkAliases(mode) {
  const a = (n) => `@es_${n}`
  const lines = [
    ['theme_bg_color', 'surface_base'],
    ['theme_fg_color', 'ink_gray_8'],
    ['theme_base_color', 'surface_base'],
    ['theme_text_color', 'ink_gray_8'],
    ['theme_selected_bg_color', 'accent'],
    ['theme_selected_fg_color', 'accent_fg'],
    ['theme_unfocused_bg_color', 'surface_base'],
    ['theme_unfocused_fg_color', 'ink_gray_6'],
    ['theme_unfocused_text_color', 'ink_gray_6'],
    ['theme_unfocused_base_color', 'surface_base'],
    ['theme_unfocused_selected_bg_color', 'accent'],
    ['theme_unfocused_selected_fg_color', 'accent_fg'],
    ['borders', 'outline_gray_1'],
    ['unfocused_borders', 'outline_gray_1'],
    ['insensitive_bg_color', 'surface_gray_1'],
    ['insensitive_fg_color', 'ink_gray_3'],
    ['insensitive_base_color', 'surface_base'],
    ['unfocused_insensitive_color', 'ink_gray_3'],
    ['accent_color', 'accent'],
    ['success_color', 'success'],
    ['warning_color', 'warning'],
    ['error_color', 'error'],
    ['content_view_bg', 'surface_base'],
    ['text_view_bg', 'surface_base'],
    ['window_bg_color', 'surface_base'],
    ['window_fg_color', 'ink_gray_8'],
    ['view_bg_color', 'surface_base'],
    ['view_fg_color', 'ink_gray_8'],
    ['headerbar_bg_color', 'surface_base'],
    ['headerbar_fg_color', 'ink_gray_8'],
    ['headerbar_border_color', 'outline_gray_1'],
    ['headerbar_backdrop_color', 'surface_base'],
    ['headerbar_shade_color', 'outline_gray_1'],
    ['card_bg_color', 'surface_elevation_1'],
    ['card_fg_color', 'ink_gray_8'],
    ['card_shade_color', 'outline_gray_1'],
    ['popover_bg_color', 'surface_elevation_1'],
    ['popover_fg_color', 'ink_gray_8'],
    ['popover_shade_color', 'outline_gray_1'],
    ['dialog_bg_color', 'surface_base'],
    ['dialog_fg_color', 'ink_gray_8'],
    ['accent_bg_color', 'accent'],
    ['accent_fg_color', 'accent_fg'],
    ['destructive_bg_color', 'destructive'],
    ['destructive_fg_color', 'accent_fg'],
    ['destructive_color', 'destructive'],
    ['error_bg_color', 'destructive'],
    ['error_fg_color', 'accent_fg'],
    ['success_bg_color', 'success'],
    ['success_fg_color', 'accent_fg'],
    ['warning_bg_color', 'warning'],
    ['warning_fg_color', 'accent_fg'],
    ['sidebar_bg_color', 'surface_sidebar'],
    ['sidebar_fg_color', 'ink_gray_8'],
    ['sidebar_backdrop_color', 'surface_sidebar'],
    ['sidebar_shade_color', 'outline_gray_1'],
    ['secondary_sidebar_bg_color', 'surface_base'],
    ['secondary_sidebar_fg_color', 'ink_gray_8'],
    ['secondary_sidebar_backdrop_color', 'surface_base'],
    ['secondary_sidebar_shade_color', 'outline_gray_1'],
    ['shade_color', 'outline_gray_1'],
    ['scrollbar_outline_color', 'outline_gray_1'],
    ['thumbnail_bg_color', 'surface_gray_2'],
    ['thumbnail_fg_color', 'ink_gray_8'],
  ]
  return lines.map(([alias, token]) => `@define-color ${alias} ${a(token)};`)
}

function extra(mode) {
  const f = effects.focus[mode].default
  const bits = f.trim().split(/\s+/)
  const width = bits[3]
  const color = bits.slice(4).join(' ')
  const dark = mode === 'dark'
  return [
    `/* focus ring ${width} ${color} */`,
    `@define-color es_focus ${color};`,
    `@define-color es_accent ${'@es_surface_blue_6'};`,
    `@define-color es_accent_hover @es_surface_blue_7;`,
    `@define-color es_accent_active @es_surface_blue_8;`,
    `@define-color es_accent_fg @es_ink_base;`,
    `@define-color es_destructive @es_surface_red_7;`,
    `@define-color es_destructive_fg ${dark ? '@es_surface_red_9' : '@es_ink_base'};`,
    `@define-color es_destructive_hover @es_surface_red_8;`,
    `@define-color es_success @es_surface_green_7;`,
    `@define-color es_warning @es_surface_amber_6;`,
    `@define-color es_error @es_surface_red_7;`,
    `@define-color es_focus_ring ${color};`,
    `/* focus width ${width}; dark ${dark} */`,
  ]
}

function emit(mode) {
  const lines = [
    `/* generated from tokens.json (frappe-ui ${data.provenance.commit.slice(0, 7)}) by tokens/gen-css.mjs do not edit */`,
    '',
    '/* raw ramps */',
    ...rampLines('lightMode'),
    ...rampLines('darkMode'),
    '',
    '/* semantic */',
    ...semanticLines(mode),
    '',
    '/* espresso aliases */',
    ...extra(mode),
    '',
    '/* gtk and libadwaita names */',
    ...gtkAliases(mode),
    '',
  ]
  return lines.join('\n')
}

fs.writeFileSync(path.join(here, '..', 'gtk-4.0', '_tokens-light.css'), emit('light'))
fs.writeFileSync(path.join(here, '..', 'gtk-4.0', '_tokens-dark.css'), emit('dark'))
fs.mkdirSync(path.join(here, '..', 'gtk-3.0'), { recursive: true })
fs.writeFileSync(path.join(here, '..', 'gtk-3.0', '_tokens-light.css'), toGtk3(resolveAliases(emit('light'))))
fs.writeFileSync(path.join(here, '..', 'gtk-3.0', '_tokens-dark.css'), toGtk3(resolveAliases(emit('dark'))))
console.log('wrote gtk4 and gtk3 token maps')
