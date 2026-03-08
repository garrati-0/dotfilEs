"""Bluetooth settings section — BlueZ via pydbus."""

import gi
import threading

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib

try:
    from pydbus import SystemBus
    HAS_PYDBUS = True
except ImportError:
    HAS_PYDBUS = False


BLUEZ_SERVICE = "org.bluez"
ADAPTER_IFACE = "org.bluez.Adapter1"
DEVICE_IFACE = "org.bluez.Device1"


def _device_icon(icon_name: str) -> str:
    """Map BlueZ icon hint to a GTK icon name."""
    mapping = {
        "audio-headset": "audio-headphones-symbolic",
        "audio-headphones": "audio-headphones-symbolic",
        "audio-card": "audio-speakers-symbolic",
        "input-keyboard": "input-keyboard-symbolic",
        "input-mouse": "input-mouse-symbolic",
        "input-gaming": "input-gaming-symbolic",
        "phone": "phone-symbolic",
        "computer": "computer-symbolic",
    }
    return mapping.get(icon_name, "bluetooth-symbolic")


class BluetoothSection:
    """Manages the Bluetooth preferences page."""

    def __init__(self, win):
        self.win = win
        self.page = Adw.PreferencesPage()
        self.bus = None
        self.adapter = None
        self.adapter_path = None

        if not HAS_PYDBUS:
            err_group = Adw.PreferencesGroup(title="Bluetooth")
            err_group.add(
                Adw.ActionRow(
                    title="pydbus not installed",
                    subtitle="Install pydbus to manage Bluetooth",
                )
            )
            self.page.add(err_group)
            return

        # --- Power toggle group -------------------------------------------
        toggle_group = Adw.PreferencesGroup(title="Bluetooth")
        self.bt_switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        toggle_row = Adw.ActionRow(
            title="Bluetooth",
            subtitle="Enable or disable Bluetooth adapter",
        )
        toggle_row.add_suffix(self.bt_switch)
        toggle_row.set_activatable_widget(self.bt_switch)
        toggle_group.add(toggle_row)
        self.page.add(toggle_group)

        # --- Paired devices group -----------------------------------------
        self.paired_group = Adw.PreferencesGroup(title="Paired Devices")
        self.page.add(self.paired_group)

        # --- Available devices group --------------------------------------
        self.available_group = Adw.PreferencesGroup(title="Available Devices")

        scan_btn = Gtk.Button(
            icon_name="view-refresh-symbolic",
            valign=Gtk.Align.CENTER,
            css_classes=["flat"],
            tooltip_text="Scan for devices",
        )
        scan_btn.connect("clicked", self._on_scan_clicked)
        self.available_group.set_header_suffix(scan_btn)
        self.page.add(self.available_group)

        # Init adapter in background thread
        threading.Thread(target=self._init_adapter, daemon=True).start()

    # ---- Adapter init (background) ----------------------------------------

    def _init_adapter(self):
        try:
            self.bus = SystemBus()
            manager = self.bus.get(BLUEZ_SERVICE, "/")
            objects = manager.GetManagedObjects()

            for path, ifaces in objects.items():
                if ADAPTER_IFACE in ifaces:
                    self.adapter_path = path
                    self.adapter = self.bus.get(BLUEZ_SERVICE, path)
                    break

            if self.adapter:
                GLib.idle_add(self._adapter_ready)
            else:
                GLib.idle_add(self._no_adapter)
        except Exception as e:
            GLib.idle_add(self._show_error, f"BlueZ unavailable: {e}")

    def _adapter_ready(self):
        powered = self.adapter.Powered
        self.bt_switch.set_active(powered)
        self.bt_switch.connect("notify::active", self._on_bt_toggle)
        self._refresh_devices()

    def _no_adapter(self):
        self.bt_switch.set_sensitive(False)

    # ---- Toggle -----------------------------------------------------------

    def _on_bt_toggle(self, switch, _pspec):
        if self.adapter:
            try:
                self.adapter.Powered = switch.get_active()
            except Exception:
                pass
            GLib.timeout_add(1000, self._refresh_devices)

    # ---- Scan -------------------------------------------------------------

    def _on_scan_clicked(self, _btn):
        if not self.adapter:
            return
        threading.Thread(target=self._do_scan, daemon=True).start()

    def _do_scan(self):
        try:
            self.adapter.StartDiscovery()
            import time
            time.sleep(5)
            try:
                self.adapter.StopDiscovery()
            except Exception:
                pass
        except Exception:
            pass
        GLib.idle_add(self._refresh_devices)

    # ---- Device list ------------------------------------------------------

    def _refresh_devices(self):
        if not self.bus or not self.adapter_path:
            return

        # Rebuild paired group
        self.page.remove(self.paired_group)
        self.paired_group = Adw.PreferencesGroup(title="Paired Devices")

        self.page.remove(self.available_group)
        self.available_group = Adw.PreferencesGroup(title="Available Devices")
        scan_btn = Gtk.Button(
            icon_name="view-refresh-symbolic",
            valign=Gtk.Align.CENTER,
            css_classes=["flat"],
            tooltip_text="Scan for devices",
        )
        scan_btn.connect("clicked", self._on_scan_clicked)
        self.available_group.set_header_suffix(scan_btn)

        try:
            manager = self.bus.get(BLUEZ_SERVICE, "/")
            objects = manager.GetManagedObjects()
        except Exception:
            self.page.add(self.paired_group)
            self.page.add(self.available_group)
            return

        paired_count = 0
        avail_count = 0

        for path, ifaces in objects.items():
            if DEVICE_IFACE not in ifaces:
                continue
            if not path.startswith(self.adapter_path + "/"):
                continue

            props = ifaces[DEVICE_IFACE]
            name = props.get("Name", props.get("Address", "Unknown"))
            paired = props.get("Paired", False)
            connected = props.get("Connected", False)
            icon_hint = props.get("Icon", "bluetooth")

            row = Adw.ActionRow(title=name)
            row.add_prefix(
                Gtk.Image.new_from_icon_name(_device_icon(icon_hint))
            )

            if connected:
                row.set_subtitle("Connected")
                disc_btn = Gtk.Button(
                    label="Disconnect",
                    valign=Gtk.Align.CENTER,
                    css_classes=["destructive-action", "pill"],
                )
                disc_btn._dev_path = path
                disc_btn.connect("clicked", self._on_disconnect)
                row.add_suffix(disc_btn)
            else:
                conn_btn = Gtk.Button(
                    label="Connect",
                    valign=Gtk.Align.CENTER,
                    css_classes=["suggested-action", "pill"],
                )
                conn_btn._dev_path = path
                conn_btn.connect("clicked", self._on_connect)
                row.add_suffix(conn_btn)

            if paired:
                self.paired_group.add(row)
                paired_count += 1
            else:
                self.available_group.add(row)
                avail_count += 1

        if paired_count == 0:
            self.paired_group.add(
                Adw.ActionRow(title="No paired devices")
            )
        if avail_count == 0:
            self.available_group.add(
                Adw.ActionRow(title="No devices found", subtitle="Tap scan to search")
            )

        self.page.add(self.paired_group)
        self.page.add(self.available_group)

    # ---- Connect / Disconnect ---------------------------------------------

    def _on_connect(self, btn):
        path = btn._dev_path
        threading.Thread(
            target=self._do_connect, args=(path,), daemon=True
        ).start()

    def _do_connect(self, path):
        try:
            dev = self.bus.get(BLUEZ_SERVICE, path)
            dev.Connect()
        except Exception as e:
            GLib.idle_add(self._show_error, f"Connect failed: {e}")
        GLib.idle_add(self._refresh_devices)

    def _on_disconnect(self, btn):
        path = btn._dev_path
        threading.Thread(
            target=self._do_disconnect, args=(path,), daemon=True
        ).start()

    def _do_disconnect(self, path):
        try:
            dev = self.bus.get(BLUEZ_SERVICE, path)
            dev.Disconnect()
        except Exception as e:
            GLib.idle_add(self._show_error, f"Disconnect failed: {e}")
        GLib.idle_add(self._refresh_devices)

    # ---- Errors -----------------------------------------------------------

    def _show_error(self, msg):
        dialog = Adw.AlertDialog(heading="Bluetooth Error", body=str(msg))
        dialog.add_response("ok", "OK")
        dialog.present(self.win)


def build_bluetooth_page(win) -> Adw.PreferencesPage:
    """Build and return the Bluetooth preferences page."""
    section = BluetoothSection(win)
    return section.page
