#!/usr/bin/env python3
# gtk4 widget gallery for theme checks
# usage: GTK_THEME=Espresso python3 tests/gallery.py [page]
import sys

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Gsk', '4.0')
gi.require_version('Graphene', '1.0')
from gi.repository import Gdk, GLib, Graphene, Gsk, Gtk  # noqa: E402


def section(title):
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    label = Gtk.Label(label=title, xalign=0)
    label.add_css_class('title-3')
    box.append(label)
    return box


def row(*widgets):
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    for widget in widgets:
        box.append(widget)
    return box


def buttons_page():
    page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24,
                   margin_top=24, margin_bottom=24, margin_start=24, margin_end=24)

    group = section('Buttons')
    normal = Gtk.Button(label='Button')
    suggested = Gtk.Button(label='Save')
    suggested.add_css_class('suggested-action')
    destructive = Gtk.Button(label='Delete')
    destructive.add_css_class('destructive-action')
    flat = Gtk.Button(label='Flat')
    flat.add_css_class('flat')
    icon = Gtk.Button(icon_name='list-add-symbolic')
    icon.add_css_class('circular')
    disabled = Gtk.Button(label='Disabled')
    disabled.set_sensitive(False)
    group.append(row(normal, suggested, destructive, flat, icon, disabled))

    group.append(row(Gtk.Button(label='Small'), Gtk.Button(label='Wide'),
                     Gtk.MenuButton(label='Menu')))
    page.append(group)

    group = section('Entries')
    entry = Gtk.Entry(placeholder_text='Name')
    search = Gtk.SearchEntry(placeholder_text='Search')
    spin = Gtk.SpinButton.new_with_range(0, 100, 1)
    dropdown = Gtk.DropDown.new_from_strings(['Balanced', 'Performance', 'Saver'])
    group.append(row(entry, search, spin, dropdown))
    page.append(group)

    group = section('Checks')
    check = Gtk.CheckButton(label='Enable notifications')
    radio1 = Gtk.CheckButton(label='Light')
    radio2 = Gtk.CheckButton(label='Dark')
    radio2.set_group(radio1)
    switch = Gtk.Switch()
    switch_on = Gtk.Switch()
    switch_on.set_active(True)
    switch_off_disabled = Gtk.Switch()
    switch_off_disabled.set_sensitive(False)
    group.append(row(check, radio1, radio2, switch, switch_on, switch_off_disabled))
    page.append(group)

    group = section('Ranges')
    scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
    scale.set_value(62)
    scale.set_hexpand(True)
    progress = Gtk.ProgressBar(fraction=0.62)
    progress.set_hexpand(True)
    spinner = Gtk.Spinner(spinning=True)
    group.append(row(scale, progress, spinner))
    page.append(group)

    group = section('Status')
    group.append(row(Gtk.Label(label='Muted'), Gtk.Label(label='Selected'),
                     Gtk.Label(label='Error')))
    page.append(group)
    return page


def surfaces_page():
    page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20,
                   margin_top=24, margin_bottom=24, margin_start=24, margin_end=24)

    group = section('Card and list')
    frame = Gtk.Frame()
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    for text in ['Build a site', 'Invite a member', 'Read the docs']:
        box.append(Gtk.Label(label=text, xalign=0, margin_start=12, margin_end=12))
    frame.set_child(box)
    group.append(frame)

    listbox = Gtk.ListBox()
    listbox.add_css_class('boxed-list')
    for text in ['Today', 'This week', 'Later']:
        listbox.append(Gtk.Label(label=text, xalign=0, margin_start=12, margin_end=12))
    listbox.select_row(listbox.get_row_at_index(0))
    group.append(listbox)
    page.append(group)

    group = section('Notebook')
    notebook = Gtk.Notebook()
    notebook.append_page(Gtk.Label(label='First tab'), Gtk.Label(label='One'))
    notebook.append_page(Gtk.Label(label='Second tab'), Gtk.Label(label='Two'))
    group.append(notebook)
    page.append(group)

    group = section('Menu and popover')
    popover = Gtk.Popover()
    content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4,
                      margin_top=8, margin_bottom=8, margin_start=8, margin_end=8)
    for text in ['Rename', 'Duplicate', 'Delete']:
        content.append(Gtk.Button(label=text, css_classes=['flat']))
    popover.set_child(content)
    menu = Gtk.MenuButton(label='Actions')
    menu.set_popover(popover)
    PREVIEW_POPOVERS.append(popover)
    group.append(row(menu, Gtk.Button(label='Tooltip')))
    page.append(group)
    return page


def dialogs_page():
    page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20,
                   margin_top=24, margin_bottom=24, margin_start=24, margin_end=24)

    group = section('Calendar')
    group.append(Gtk.Calendar())
    page.append(group)

    group = section('Dialogs')
    message = Gtk.Button(label='Message dialog')

    def open_message(_button):
        dialog = Gtk.MessageDialog(transient_for=page.get_root(), modal=True,
                                   buttons=Gtk.ButtonsType.OK_CANCEL,
                                   text='Apply changes?')
        dialog.set_property('secondary-text', 'This updates every open window.')
        dialog.connect('response', lambda d, _r: d.destroy())
        dialog.present()

    message.connect('clicked', open_message)

    chooser = Gtk.Button(label='File chooser')

    def open_chooser(_button):
        dialog = Gtk.FileChooserDialog(title='Open file', transient_for=page.get_root(),
                                       action=Gtk.FileChooserAction.OPEN)
        dialog.add_buttons('Cancel', Gtk.ResponseType.CANCEL, 'Open', Gtk.ResponseType.ACCEPT)
        dialog.connect('response', lambda d, _r: d.destroy())
        dialog.present()

    chooser.connect('clicked', open_chooser)
    group.append(row(message, chooser))
    page.append(group)
    return page


PREVIEW_POPOVERS = []
PAGES = [('Buttons', buttons_page), ('Surfaces', surfaces_page), ('Dialogs', dialogs_page)]


def save_shot(window, path, native=None):
    paintable = Gtk.WidgetPaintable.new(window)
    width = window.get_width() or paintable.get_intrinsic_width()
    height = window.get_height() or paintable.get_intrinsic_height()
    snapshot = Gtk.Snapshot.new()
    paintable.snapshot(snapshot, width, height)
    node = snapshot.to_node()
    renderer = Gtk.Native.get_renderer(native or window)
    rect = Graphene.Rect().init(0, 0, width, height)
    renderer.render_texture(node, rect).save_to_png(path)


def main():
    shot = None
    popover_shot = None
    popup = '--popup' in sys.argv
    for index, arg in enumerate(sys.argv[1:]):
        if arg == '--popover-shot' and index + 2 <= len(sys.argv[1:]):
            popover_shot = sys.argv[index + 2]
    page = 'Buttons'
    args = sys.argv[1:]
    for index, arg in enumerate(args):
        if arg == '--shot' and index + 1 < len(args):
            shot = args[index + 1]
        elif not arg.startswith('--') and (index == 0 or args[index - 1] != '--shot'):
            page = arg

    app = Gtk.Application(application_id='org.obwl.EspressoGallery')

    def activate(application):
        window = Gtk.ApplicationWindow(application=application,
                                       title='Espresso Gallery', default_width=980,
                                       default_height=760)
        header = Gtk.HeaderBar()
        window.set_titlebar(header)

        sidebar = Gtk.ListBox(css_classes=['navigation-sidebar'], width_request=180)
        stack = Gtk.Stack(transition_type=Gtk.StackTransitionType.CROSSFADE)
        stack.set_hexpand(True)

        for index, (name, build) in enumerate(PAGES):
            sidebar.append(Gtk.Label(label=name, xalign=0, margin_top=10, margin_bottom=10,
                                     margin_start=14, margin_end=14))
            stack.add_named(build(), name)

        def on_row(_listbox, row):
            stack.set_visible_child_name(PAGES[row.get_index()][0])

        sidebar.connect('row-selected', on_row)

        split = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        split.append(sidebar)
        split.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        split.append(stack)
        window.set_child(split)
        sidebar.select_row(sidebar.get_row_at_index(0))

        for index, (name, _build) in enumerate(PAGES):
            if name.lower() == page.lower():
                sidebar.select_row(sidebar.get_row_at_index(index))
        window.present()

        def find_popover(widget):
            child = widget.get_first_child()
            while child:
                if isinstance(child, Gtk.Popover):
                    return child
                found = find_popover(child)
                if found:
                    return found
                child = child.get_next_sibling()
            return None

        if popover_shot and PREVIEW_POPOVERS:
            PREVIEW_POPOVERS[0].popup()

        if popup or popover_shot:
            def open_popup(widget):
                child = widget.get_first_child()
                while child:
                    if isinstance(child, Gtk.MenuButton):
                        child.popup()
                        return True
                    if open_popup(child):
                        return True
                    child = child.get_next_sibling()
                return False

            open_popup(window)

        if popover_shot:
            def snap_popover():
                popover = PREVIEW_POPOVERS[0] if PREVIEW_POPOVERS else None
                content = popover.get_child() if popover else None
                if content:
                    save_shot(content, popover_shot, window)
                application.quit()
                return GLib.SOURCE_REMOVE

            GLib.timeout_add(900, snap_popover)
        elif shot:
            def snap():
                save_shot(window, shot)
                application.quit()
                return GLib.SOURCE_REMOVE

            GLib.timeout_add(600 if popup else 1500, snap)

    app.connect('activate', activate)
    return app.run(sys.argv[:1])


if __name__ == '__main__':
    raise SystemExit(main())
