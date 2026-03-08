#!/usr/bin/env python3
"""HyprSettings — A modern GTK4/Libadwaita settings app for Hyprland.

Styled to match gnome-control-center using native Libadwaita theming.
"""

import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gdk, Gio

# Section builders — each returns an Adw.PreferencesPage
from sections.wifi import build_wifi_page
from sections.bluetooth import build_bluetooth_page
from sections.display import build_display_page
from sections.audio import build_audio_page
from sections.sysinfo import build_sysinfo_page
from sections.monitor import build_monitor_page
from sections.power import build_power_page
from sections.appearance import build_appearance_page

# ---------------------------------------------------------------------------
# Minimal CSS — just subtle sidebar polish, rest is native Libadwaita
# ---------------------------------------------------------------------------
APP_CSS = """
.sidebar-listbox row {
    margin: 2px 6px;
    border-radius: 10px;
    padding: 6px 10px;
    transition: background-color 200ms ease;
}
.sidebar-listbox row:selected {
    background-color: alpha(@accent_color, 0.18);
}
.sidebar-listbox row image {
    margin-right: 10px;
}

.section-title {
    font-size: 22px;
    font-weight: 800;
}

preferencespage > scrolledwindow > viewport > clamp > box {
    margin-top: 8px;
}

/* Gauge labels for System Monitor */
.gauge-value {
    font-size: 16px;
    font-weight: 700;
    color: @accent_color;
    font-variant-numeric: tabular-nums;
}
.gauge-value-warn {
    font-size: 16px;
    font-weight: 700;
    color: @warning_color;
    font-variant-numeric: tabular-nums;
}
.gauge-value-crit {
    font-size: 16px;
    font-weight: 700;
    color: @error_color;
    font-variant-numeric: tabular-nums;
}

/* Power section labels */
.accent-label {
    color: @accent_color;
    font-weight: 600;
}
.warning-label {
    color: @warning_color;
    font-weight: 600;
}
.error-label {
    color: @error_color;
    font-weight: 600;
}
.success-label {
    color: @success_color;
    font-weight: 600;
}
"""

# ---------------------------------------------------------------------------
# Section registry
# ---------------------------------------------------------------------------
SECTIONS = [
    ("Wi-Fi",        "network-wireless-symbolic",            build_wifi_page),
    ("Bluetooth",    "bluetooth-symbolic",                    build_bluetooth_page),
    ("Appearance",   "preferences-desktop-wallpaper-symbolic", build_appearance_page),
    ("Display",      "display-brightness-symbolic",           build_display_page),
    ("Audio",        "audio-volume-high-symbolic",            build_audio_page),
    ("System Monitor", "utilities-system-monitor-symbolic",     build_monitor_page),
    ("Power",        "system-shutdown-symbolic",              build_power_page),
    ("System",       "computer-symbolic",                     build_sysinfo_page),
]


class HyprSettingsWindow(Adw.ApplicationWindow):
    """Main settings window with NavigationSplitView."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title("Settings")
        self.set_default_size(960, 680)

        # --- Content stack (right pane) ----------------------------------
        self.content_stack = Gtk.Stack(
            transition_type=Gtk.StackTransitionType.CROSSFADE,
            transition_duration=200,
        )

        # Build each section page and add to stack
        self._pages = {}
        for title, _icon, builder in SECTIONS:
            page = builder(self)
            self.content_stack.add_named(page, title)
            self._pages[title] = page

        # --- Sidebar (left pane) -----------------------------------------
        self.sidebar_listbox = Gtk.ListBox(
            selection_mode=Gtk.SelectionMode.SINGLE,
            css_classes=["navigation-sidebar", "sidebar-listbox"],
        )
        self.sidebar_listbox.connect("row-selected", self._on_sidebar_row_selected)

        for idx, (title, icon, _builder) in enumerate(SECTIONS):
            row = Adw.ActionRow(title=title, activatable=True)
            row.add_prefix(Gtk.Image.new_from_icon_name(icon))
            row._section_name = title
            self.sidebar_listbox.append(row)

        sidebar_scroll = Gtk.ScrolledWindow(
            hscrollbar_policy=Gtk.PolicyType.NEVER,
            vexpand=True,
            child=self.sidebar_listbox,
        )

        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Sidebar header
        sidebar_hdr = Adw.HeaderBar(
            title_widget=Gtk.Label(label="Settings", css_classes=["title"]),
        )
        sidebar_box.append(sidebar_hdr)
        sidebar_box.append(sidebar_scroll)

        sidebar_page = Adw.NavigationPage(
            title="Settings",
            child=sidebar_box,
        )

        # --- Content pane wrapper ----------------------------------------
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.content_header = Adw.HeaderBar(
            show_title=True,
        )
        content_box.append(self.content_header)
        content_box.append(self.content_stack)

        content_page = Adw.NavigationPage(
            title="Wi-Fi",           # initial
            child=content_box,
        )

        self.content_nav_page = content_page

        # --- NavigationSplitView -----------------------------------------
        split = Adw.NavigationSplitView(
            sidebar=sidebar_page,
            content=content_page,
            min_sidebar_width=230,
            max_sidebar_width=290,
        )

        self.set_content(split)

        # Select first row
        first_row = self.sidebar_listbox.get_row_at_index(0)
        if first_row:
            self.sidebar_listbox.select_row(first_row)

    def select_section_by_keyword(self, keyword):
        keyword = keyword.lower()
        mapping = {
            "wifi": "Wi-Fi",
            "blutut": "Bluetooth",
            "bluetooth": "Bluetooth",
            "display": "Display",
            "audio": "Audio",
            "monitor": "System Monitor",
            "system monitor": "System Monitor",
            "power": "Power",
            "system": "System",
            "appearance": "Appearance",
            "personalizzazione": "Appearance",
        }
        target_name = mapping.get(keyword, keyword)
        idx = 0
        while True:
            row = self.sidebar_listbox.get_row_at_index(idx)
            if not row:
                break
            if row._section_name.lower() == target_name.lower():
                self.sidebar_listbox.select_row(row)
                break
            idx += 1

    # ----- callbacks -------------------------------------------------------

    def _on_sidebar_row_selected(self, listbox, row):
        if row is None:
            return
        name = row._section_name
        self.content_stack.set_visible_child_name(name)
        self.content_nav_page.set_title(name)


class HyprSettingsApp(Adw.Application):
    """Application singleton."""

    def __init__(self):
        super().__init__(
            application_id="com.hyprland.settings",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE | Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self._initial_section = None

    def do_command_line(self, command_line):
        args = command_line.get_arguments()
        if len(args) > 1:
            self._initial_section = args[1]
        self.activate()
        return 0

    def do_startup(self):
        Adw.Application.do_startup(self)

        # Respect system dark/light mode via Adw.StyleManager (no override)

        # Load minimal CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_string(APP_CSS)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = HyprSettingsWindow(application=self)
            
        if self._initial_section:
            win.select_section_by_keyword(self._initial_section)
            self._initial_section = None
            
        win.present()


def main():
    app = HyprSettingsApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
