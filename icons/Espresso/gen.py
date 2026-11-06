#!/usr/bin/env python3
# lucide svgs to gtk symbolic icons. gtk fills symbolic paths so strokes become outlines
# usage: gen.py <lucide-static/icons dir>   needs picosvg
import pathlib
import re
import subprocess
import sys

MAP = {
    'window-close': 'x', 'window-maximize': 'square', 'window-minimize': 'minus', 'window-restore': 'copy',
    'pan-down': 'chevron-down', 'pan-up': 'chevron-up', 'pan-end': 'chevron-right', 'pan-start': 'chevron-left',
    'open-menu': 'menu', 'view-more': 'ellipsis-vertical', 'view-more-horizontal': 'ellipsis',
    'go-previous': 'arrow-left', 'go-next': 'arrow-right', 'go-up': 'arrow-up', 'go-down': 'arrow-down',
    'go-home': 'house', 'user-home': 'house', 'edit-find': 'search', 'system-search': 'search',
    'edit-clear': 'x', 'process-stop': 'x', 'edit-delete': 'trash-2', 'user-trash': 'trash-2',
    'edit-copy': 'copy', 'edit-paste': 'clipboard-paste', 'edit-cut': 'scissors', 'edit-undo': 'undo-2',
    'edit-redo': 'redo-2', 'document-edit': 'pencil', 'list-add': 'plus', 'list-remove': 'minus',
    'object-select': 'check', 'emblem-ok': 'check', 'emblem-default': 'check',
    'document-open': 'folder-open', 'document-save': 'save', 'document-new': 'file-plus',
    'document-properties': 'sliders-horizontal', 'folder-new': 'folder-plus',
    'system-file-manager': 'folder', 'user-desktop': 'monitor', 'video-display': 'monitor',
    'drive-harddisk': 'hard-drive', 'drive-removable-media': 'usb', 'media-optical': 'disc',
    'applications-other': 'layout-grid',
    'view-app-grid': 'layout-grid', 'view-grid': 'layout-grid', 'view-list': 'list', 'view-dual': 'columns-2',
    'view-refresh': 'refresh-cw', 'view-sidebar': 'panel-left', 'starred': 'star', 'non-starred': 'star',
    'bookmark-new': 'bookmark', 'mail-unread': 'mail', 'mail-send': 'send',
    'dialog-password': 'key-round', 'dialog-information': 'info', 'help-about': 'info',
    'dialog-warning': 'triangle-alert', 'dialog-error': 'circle-alert', 'help-browser': 'circle-help',
    'preferences-system': 'settings', 'emblem-system': 'settings',
    'preferences-system-notifications': 'bell', 'notifications-disabled': 'bell-off',
    'preferences-desktop-appearance': 'palette', 'preferences-desktop-wallpaper': 'image',
    'preferences-desktop-keyboard-shortcuts': 'keyboard', 'input-keyboard': 'keyboard',
    'input-mouse': 'mouse', 'font-x-generic': 'type', 'display-brightness': 'sun',
    'weather-clear': 'sun', 'weather-clear-night': 'moon', 'night-light': 'moon',
    'dark-mode': 'contrast', 'obwl-dark-style': 'contrast', 'camera-photo': 'camera',
    'selection-mode': 'scissors', 'system-lock-screen': 'lock', 'changes-prevent': 'lock',
    'changes-allow': 'lock-open', 'system-log-out': 'log-out', 'system-reboot': 'rotate-ccw',
    'system-restart': 'rotate-ccw', 'system-shutdown': 'power', 'system-run': 'play',
    'utilities-terminal': 'square-terminal', 'power-profile-balanced': 'gauge',
    'power-profile-power-saver': 'leaf', 'power-profile-performance': 'zap',
    'media-playback-start': 'play', 'media-playback-pause': 'pause', 'media-playback-stop': 'square',
    'media-skip-backward': 'skip-back', 'media-skip-forward': 'skip-forward',
    'audio-volume-high': 'volume-2', 'audio-volume-medium': 'volume-1', 'audio-volume-low': 'volume',
    'audio-volume-muted': 'volume-x', 'audio-input-microphone': 'mic',
    'microphone-sensitivity-high': 'mic', 'microphone-sensitivity-muted': 'mic-off',
    'bluetooth': 'bluetooth', 'bluetooth-active': 'bluetooth', 'bluetooth-disabled': 'bluetooth-off',
    'network-wireless': 'wifi', 'network-wireless-signal-excellent': 'wifi',
    'network-wireless-signal-good': 'wifi-high', 'network-wireless-signal-ok': 'wifi-high',
    'network-wireless-signal-weak': 'wifi-low', 'network-wireless-signal-none': 'wifi-zero',
    'network-wireless-offline': 'wifi-off', 'network-offline': 'wifi-off',
    'network-wireless-encrypted': 'lock', 'network-wired': 'ethernet-port',
    'battery-full': 'battery-full', 'battery-good': 'battery-medium', 'battery-low': 'battery-low',
    'battery-caution': 'battery-warning', 'battery-empty': 'battery',
    'battery-full-charging': 'battery-charging', 'battery-good-charging': 'battery-charging',
    'battery-low-charging': 'battery-charging', 'battery-caution-charging': 'battery-charging',
    'battery-empty-charging': 'battery-charging', 'battery-full-charged': 'battery-full',
    'zoom-in': 'zoom-in', 'zoom-out': 'zoom-out',
}

# symbolic twins for sidebar places but no file types since gtk4 picks any -symbolic twin in this theme over adwaitas full color one
PLAIN = {
    'folder-documents': 'folder-open', 'folder-download': 'folder-down', 'folder-music': 'folder-heart',
    'folder-pictures': 'folder-search', 'folder-videos': 'folder-kanban', 'folder-templates': 'folder-cog',
    'folder-publicshare': 'folder-symlink', 'folder-remote': 'folder-git', 'user-home': 'house',
    'user-desktop': 'monitor', 'user-trash': 'trash-2', 'user-trash-full': 'trash-2', 'computer': 'laptop',
    'drive-harddisk': 'hard-drive', 'drive-removable-media': 'usb', 'media-removable': 'usb',
    'drive-optical': 'disc', 'network-workgroup': 'network', 'network-server': 'server',
    'document-open-recent': 'clock', }

# thunar asks for these plain and adwaitas dark glyphs vanish on a dark sidebar. mid gray holds 3:1 in both modes
SIDEBAR = {
    'computer': 'laptop', 'user-home': 'house', 'document-open-recent': 'clock',
    'drive-harddisk': 'hard-drive', 'drive-harddisk-usb': 'hard-drive', 'drive-harddisk-system': 'hard-drive',
    'drive-removable-media': 'usb', 'drive-removable-media-usb': 'usb', 'media-removable': 'usb',
    'drive-optical': 'disc', 'media-optical': 'disc', 'network-workgroup': 'network', 'network-server': 'server',
}
GRAY = '#8a8a8a'

src = pathlib.Path(sys.argv[1])
out = pathlib.Path(__file__).resolve().parent / 'scalable' / 'symbolic'
out.mkdir(parents=True, exist_ok=True)
missing = sorted({lu for lu in [*MAP.values(), *PLAIN.values(), *SIDEBAR.values()] if not (src / f'{lu}.svg').exists()})
assert not missing, f'not in lucide: {missing}'

cache = {}


def flat(lu, color, width):
    key = (lu, color, width)
    if key not in cache:
        svg = (src / f'{lu}.svg').read_text()
        svg = svg.replace('stroke-width="2"', f'stroke-width="{width}"').replace('currentColor', color)
        res = subprocess.run(['picosvg', '/dev/stdin'], input=svg, capture_output=True, text=True, check=True).stdout
        cache[key] = re.sub(r'\s*class="[^"]*"|\s*<defs/>', '', res)
    return cache[key]


for name, lu in MAP.items():
    (out / f'{name}-symbolic.svg').write_text(flat(lu, '#000', 2))
for name, lu in PLAIN.items():
    (out / f'{name}-symbolic.svg').write_text(flat(lu, '#000', 2))
for name, lu in SIDEBAR.items():
    (out / f'{name}.svg').write_text(flat(lu, GRAY, 2))
print(f'{len(MAP) + len(PLAIN) + len(SIDEBAR)} icons from {len(cache)} renders')
