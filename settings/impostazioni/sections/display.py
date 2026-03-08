"""Display & Brightness settings section — backlight + hyprsunset."""

import os
import subprocess

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import shutil
from gi.repository import Gtk, Adw, GLib


def _find_backlight() -> str | None:
    """Return the sysfs path for the first backlight device, or None."""
    base = "/sys/class/backlight"
    if not os.path.isdir(base):
        return None
    for entry in sorted(os.listdir(base)):
        path = os.path.join(base, entry)
        if os.path.isfile(os.path.join(path, "brightness")):
            return path
    return None


def _read_int(path: str) -> int:
    try:
        with open(path) as f:
            return int(f.read().strip())
    except Exception:
        return -1


def _brightnessctl_get() -> tuple[int, int]:
    """Return (current, max) brightness via brightnessctl, or (-1,-1)."""
    try:
        out = subprocess.check_output(
            ["brightnessctl", "info", "-m"], text=True, timeout=3
        )
        # Format: device,class,current,percentage,max
        parts = out.strip().split(",")
        current = int(parts[2])
        max_val = int(parts[4])
        return current, max_val
    except Exception:
        return -1, -1


def _brightnessctl_set(percent: int):
    subprocess.Popen(
        ["brightnessctl", "set", f"{percent}%"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


class DisplaySection:
    """Manages the Display preferences page."""

    def __init__(self, win):
        self.win = win
        self.page = Adw.PreferencesPage()
        self.backlight_path = _find_backlight()
        self.max_brightness = 100

        self._night_shift_proc = None

        # --- Brightness group ---------------------------------------------
        bright_group = Adw.PreferencesGroup(title="Brightness")

        self.bright_pct_label = Gtk.Label(
            label="100%",
            css_classes=["dim-label"],
            valign=Gtk.Align.CENTER,
            width_chars=5,
        )

        self.bright_slider = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL,
            hexpand=True,
            draw_value=False,
            valign=Gtk.Align.CENTER,
        )
        self.bright_slider.set_range(1, 100)
        self.bright_slider.set_increments(1, 5)

        bright_row = Adw.ActionRow(title="Screen Brightness")
        bright_row.add_suffix(self.bright_slider)
        bright_row.add_suffix(self.bright_pct_label)
        bright_group.add(bright_row)
        self.page.add(bright_group)

        # Read current brightness
        if self.backlight_path:
            self.max_brightness = _read_int(
                os.path.join(self.backlight_path, "max_brightness")
            )
            current = _read_int(os.path.join(self.backlight_path, "brightness"))
            if self.max_brightness > 0 and current >= 0:
                pct = int(current / self.max_brightness * 100)
                self.bright_slider.set_value(max(1, pct))
        else:
            # Fallback to brightnessctl
            cur, mx = _brightnessctl_get()
            if mx > 0:
                self.max_brightness = mx
                pct = int(cur / mx * 100)
                self.bright_slider.set_value(max(1, pct))

        self._update_pct_label()
        self.bright_slider.connect("value-changed", self._on_brightness_changed)

        # --- Night Shift group --------------------------------------------
        night_group = Adw.PreferencesGroup(
            title="Night Shift",
            description="Reduce blue light by adjusting color temperature",
        )

        # Toggle
        self.night_switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        night_toggle_row = Adw.ActionRow(
            title="Night Shift",
            subtitle="Use hyprsunset to warm the display",
        )
        night_toggle_row.add_suffix(self.night_switch)
        night_toggle_row.set_activatable_widget(self.night_switch)
        night_group.add(night_toggle_row)

        # Temperature slider
        self.temp_label = Gtk.Label(
            label="4500 K",
            css_classes=["dim-label"],
            valign=Gtk.Align.CENTER,
            width_chars=7,
        )

        self.temp_slider = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL,
            hexpand=True,
            draw_value=False,
            valign=Gtk.Align.CENTER,
        )
        self.temp_slider.set_range(2500, 6500)
        self.temp_slider.set_increments(100, 500)
        self.temp_slider.set_value(4500)
        # Add marks
        self.temp_slider.add_mark(2500, Gtk.PositionType.BOTTOM, "Warm")
        self.temp_slider.add_mark(6500, Gtk.PositionType.BOTTOM, "Cool")

        temp_row = Adw.ActionRow(title="Color Temperature")
        temp_row.add_suffix(self.temp_slider)
        temp_row.add_suffix(self.temp_label)
        night_group.add(temp_row)

        self.page.add(night_group)

        self.night_switch.connect("notify::active", self._on_night_toggle)
        self.temp_slider.connect("value-changed", self._on_temp_changed)
        self.temp_slider.set_sensitive(False)

        # --- Multimonitor group -------------------------------------------
        multi_group = Adw.PreferencesGroup(
            title="Multi-Monitor",
            description="Configure screen layout and resolution",
        )

        multi_row = Adw.ActionRow(
            title="Manage Displays",
            subtitle="Open the display configuration utility",
        )
        multi_btn = Gtk.Button(
            icon_name="preferences-desktop-display-symbolic",
            valign=Gtk.Align.CENTER,
            css_classes=["circular"]
        )
        multi_btn.connect("clicked", self._on_manage_displays)
        multi_row.add_suffix(multi_btn)
        multi_row.set_activatable_widget(multi_btn)
        multi_group.add(multi_row)

        self.page.add(multi_group)

    # ---- Brightness -------------------------------------------------------

    def _update_pct_label(self):
        pct = int(self.bright_slider.get_value())
        self.bright_pct_label.set_label(f"{pct}%")

    def _on_brightness_changed(self, scale):
        self._update_pct_label()
        pct = int(scale.get_value())

        if self.backlight_path and self.max_brightness > 0:
            raw = max(1, int(pct / 100 * self.max_brightness))
            try:
                with open(
                    os.path.join(self.backlight_path, "brightness"), "w"
                ) as f:
                    f.write(str(raw))
            except PermissionError:
                # Fall back to brightnessctl
                _brightnessctl_set(pct)
        else:
            _brightnessctl_set(pct)

    # ---- Night Shift ------------------------------------------------------

    def _on_night_toggle(self, switch, _pspec):
        active = switch.get_active()
        self.temp_slider.set_sensitive(active)
        if active:
            self._apply_night_shift()
        else:
            self._kill_hyprsunset()

    def _on_temp_changed(self, scale):
        temp = int(scale.get_value())
        self.temp_label.set_label(f"{temp} K")
        if self.night_switch.get_active():
            self._apply_night_shift()

    def _apply_night_shift(self):
        self._kill_hyprsunset()
        temp = int(self.temp_slider.get_value())
        try:
            self._night_shift_proc = subprocess.Popen(
                ["hyprsunset", "-t", str(temp)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            self._show_error("hyprsunset not found. Install it to use Night Shift.")

    def _kill_hyprsunset(self):
        if self._night_shift_proc:
            try:
                self._night_shift_proc.terminate()
            except Exception:
                pass
            self._night_shift_proc = None
        # Also kill any stray instances
        subprocess.Popen(
            ["pkill", "-f", "hyprsunset"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def _show_error(self, msg):
        dialog = Adw.AlertDialog(heading="Display Error", body=msg)
        dialog.add_response("ok", "OK")
        dialog.present(self.win)

    # ---- Multimonitor -----------------------------------------------------

    def _on_manage_displays(self, button):
        if shutil.which("wdisplays"):
            cmd = ["wdisplays"]
        elif shutil.which("nwg-displays"):
            cmd = ["nwg-displays"]
        else:
            self._show_error(
                "No display management tool found.\nInstall 'wdisplays' (e.g. sudo apt install wdisplays) or 'nwg-displays'."
            )
            return

        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build_display_page(win) -> Adw.PreferencesPage:
    """Build and return the Display preferences page."""
    section = DisplaySection(win)
    return section.page
