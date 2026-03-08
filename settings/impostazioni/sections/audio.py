"""Audio settings section — WirePlumber / PipeWire via wpctl."""

import re
import subprocess

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib


def _run(cmd: list[str]) -> str:
    """Run a command and return stdout, or empty string on failure."""
    try:
        return subprocess.check_output(cmd, text=True, timeout=5, stderr=subprocess.DEVNULL)
    except Exception:
        return ""


def _get_volume(target: str) -> tuple[float, bool]:
    """Return (volume_fraction, muted) for a wpctl target like @DEFAULT_AUDIO_SINK@."""
    out = _run(["wpctl", "get-volume", target])
    # Example: "Volume: 0.75" or "Volume: 0.75 [MUTED]"
    m = re.search(r"Volume:\s+([\d.]+)", out)
    vol = float(m.group(1)) if m else 0.0
    muted = "[MUTED]" in out
    return vol, muted


def _set_volume(target: str, fraction: float):
    subprocess.Popen(
        ["wpctl", "set-volume", target, f"{fraction:.2f}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _toggle_mute(target: str):
    subprocess.Popen(
        ["wpctl", "set-mute", target, "toggle"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _parse_devices(section_keyword: str) -> list[tuple[str, str, bool]]:
    """Parse wpctl status and return [(id, name, is_default), ...] for sinks or sources.

    section_keyword: "Sinks:" or "Sources:"
    """
    out = _run(["wpctl", "status"])
    devices = []
    in_section = False
    in_audio = False

    for line in out.splitlines():
        stripped = line.strip()
        # Detect "Audio" top-level section
        if stripped.startswith("Audio"):
            in_audio = True
            continue
        if in_audio and stripped and not stripped[0].isspace() and not stripped.startswith("│") and not stripped.startswith("├") and not stripped.startswith("└") and not stripped.startswith("*"):
            # new top-level section
            if not stripped.startswith(section_keyword) and in_section:
                break
        if section_keyword in stripped:
            in_section = True
            continue
        if in_section:
            # Lines look like: " │  * 46. Built-in Audio Analog Stereo [vol: 0.75]"
            # or " │    47. Some Device [vol: 0.50]"
            if "─" in stripped or stripped == "│" or stripped == "":
                if devices:  # end of section
                    break
                continue
            # Extract id, name, default marker
            m = re.search(r"(\*?)\s*(\d+)\.\s+(.+?)(?:\s+\[vol:.*\])?$", stripped)
            if m:
                is_default = m.group(1) == "*"
                dev_id = m.group(2)
                dev_name = m.group(3).strip()
                devices.append((dev_id, dev_name, is_default))

    return devices


class AudioSection:
    """Manages the Audio preferences page."""

    def __init__(self, win):
        self.win = win
        self.page = Adw.PreferencesPage()
        self._updating = False  # guard against feedback loops

        # ---- Output group ------------------------------------------------
        output_group = Adw.PreferencesGroup(title="Output")

        # Volume slider
        vol, muted = _get_volume("@DEFAULT_AUDIO_SINK@")

        self.vol_slider = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL,
            hexpand=True,
            draw_value=False,
            valign=Gtk.Align.CENTER,
        )
        self.vol_slider.set_range(0, 1.5)
        self.vol_slider.set_increments(0.01, 0.05)
        self.vol_slider.set_value(vol)
        self.vol_slider.add_mark(1.0, Gtk.PositionType.BOTTOM, "100%")

        self.vol_pct = Gtk.Label(
            label=f"{int(vol * 100)}%",
            css_classes=["dim-label"],
            valign=Gtk.Align.CENTER,
            width_chars=5,
        )

        self.mute_btn = Gtk.ToggleButton(
            icon_name="audio-volume-muted-symbolic" if muted else "audio-volume-high-symbolic",
            valign=Gtk.Align.CENTER,
            css_classes=["flat"],
            active=muted,
            tooltip_text="Mute",
        )

        vol_row = Adw.ActionRow(title="Volume")
        vol_row.add_suffix(self.mute_btn)
        vol_row.add_suffix(self.vol_slider)
        vol_row.add_suffix(self.vol_pct)
        output_group.add(vol_row)

        # Output device dropdown
        self.sink_devices = _parse_devices("Sinks:")
        sink_names = [d[1] for d in self.sink_devices]
        default_idx = 0
        for i, d in enumerate(self.sink_devices):
            if d[2]:
                default_idx = i
                break

        if sink_names:
            self.sink_model = Gtk.StringList.new(sink_names)
            self.sink_dropdown = Gtk.DropDown(
                model=self.sink_model,
                valign=Gtk.Align.CENTER,
            )
            self.sink_dropdown.set_selected(default_idx)
            self.sink_dropdown.connect("notify::selected", self._on_sink_changed)

            dev_row = Adw.ActionRow(title="Output Device")
            dev_row.add_suffix(self.sink_dropdown)
            output_group.add(dev_row)

        self.page.add(output_group)

        # ---- Input group -------------------------------------------------
        input_group = Adw.PreferencesGroup(title="Input")

        # Input volume slider
        ivol, imuted = _get_volume("@DEFAULT_AUDIO_SOURCE@")

        self.input_slider = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL,
            hexpand=True,
            draw_value=False,
            valign=Gtk.Align.CENTER,
        )
        self.input_slider.set_range(0, 1.5)
        self.input_slider.set_increments(0.01, 0.05)
        self.input_slider.set_value(ivol)

        self.input_pct = Gtk.Label(
            label=f"{int(ivol * 100)}%",
            css_classes=["dim-label"],
            valign=Gtk.Align.CENTER,
            width_chars=5,
        )

        self.input_mute_btn = Gtk.ToggleButton(
            icon_name="audio-input-microphone-muted-symbolic" if imuted else "audio-input-microphone-symbolic",
            valign=Gtk.Align.CENTER,
            css_classes=["flat"],
            active=imuted,
            tooltip_text="Mute Microphone",
        )

        input_vol_row = Adw.ActionRow(title="Microphone Level")
        input_vol_row.add_suffix(self.input_mute_btn)
        input_vol_row.add_suffix(self.input_slider)
        input_vol_row.add_suffix(self.input_pct)
        input_group.add(input_vol_row)

        # Input device dropdown
        self.source_devices = _parse_devices("Sources:")
        source_names = [d[1] for d in self.source_devices]
        default_src_idx = 0
        for i, d in enumerate(self.source_devices):
            if d[2]:
                default_src_idx = i
                break

        if source_names:
            self.source_model = Gtk.StringList.new(source_names)
            self.source_dropdown = Gtk.DropDown(
                model=self.source_model,
                valign=Gtk.Align.CENTER,
            )
            self.source_dropdown.set_selected(default_src_idx)
            self.source_dropdown.connect("notify::selected", self._on_source_changed)

            src_dev_row = Adw.ActionRow(title="Input Device")
            src_dev_row.add_suffix(self.source_dropdown)
            input_group.add(src_dev_row)

        self.page.add(input_group)

        # ---- Connect signals ---------------------------------------------
        self.vol_slider.connect("value-changed", self._on_vol_changed)
        self.mute_btn.connect("toggled", self._on_mute_toggled)
        self.input_slider.connect("value-changed", self._on_input_vol_changed)
        self.input_mute_btn.connect("toggled", self._on_input_mute_toggled)

    # ---- Output callbacks -------------------------------------------------

    def _on_vol_changed(self, scale):
        val = scale.get_value()
        self.vol_pct.set_label(f"{int(val * 100)}%")
        _set_volume("@DEFAULT_AUDIO_SINK@", val)

    def _on_mute_toggled(self, btn):
        _toggle_mute("@DEFAULT_AUDIO_SINK@")
        if btn.get_active():
            btn.set_icon_name("audio-volume-muted-symbolic")
        else:
            btn.set_icon_name("audio-volume-high-symbolic")

    def _on_sink_changed(self, dropdown, _pspec):
        idx = dropdown.get_selected()
        if idx < len(self.sink_devices):
            dev_id = self.sink_devices[idx][0]
            subprocess.Popen(
                ["wpctl", "set-default", dev_id],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    # ---- Input callbacks --------------------------------------------------

    def _on_input_vol_changed(self, scale):
        val = scale.get_value()
        self.input_pct.set_label(f"{int(val * 100)}%")
        _set_volume("@DEFAULT_AUDIO_SOURCE@", val)

    def _on_input_mute_toggled(self, btn):
        _toggle_mute("@DEFAULT_AUDIO_SOURCE@")
        if btn.get_active():
            btn.set_icon_name("audio-input-microphone-muted-symbolic")
        else:
            btn.set_icon_name("audio-input-microphone-symbolic")

    def _on_source_changed(self, dropdown, _pspec):
        idx = dropdown.get_selected()
        if idx < len(self.source_devices):
            dev_id = self.source_devices[idx][0]
            subprocess.Popen(
                ["wpctl", "set-default", dev_id],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )


def build_audio_page(win) -> Adw.PreferencesPage:
    """Build and return the Audio preferences page."""
    section = AudioSection(win)
    return section.page
