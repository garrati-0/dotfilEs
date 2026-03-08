"""Wi-Fi settings section — NetworkManager via GI bindings."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("NM", "1.0")

from gi.repository import Gtk, Adw, GLib, NM


def _signal_icon(strength: int) -> str:
    """Return an icon name for the given signal strength (0-100)."""
    if strength >= 75:
        return "network-wireless-signal-excellent-symbolic"
    elif strength >= 50:
        return "network-wireless-signal-good-symbolic"
    elif strength >= 25:
        return "network-wireless-signal-ok-symbolic"
    else:
        return "network-wireless-signal-weak-symbolic"


# Access enums that start with a digit via getattr
_ApFlags = getattr(NM, "80211ApFlags")


def _get_ap_security(ap) -> str:
    """Return a human-readable security label for an access point."""
    flags = ap.get_flags()
    wpa = ap.get_wpa_flags()
    rsn = ap.get_rsn_flags()
    if rsn or wpa:
        return "WPA/WPA2"
    elif flags & _ApFlags.PRIVACY:
        return "WEP"
    return "Open"


class WifiSection:
    """Manages the Wi-Fi preferences page and its interactions."""

    def __init__(self, win):
        self.win = win
        self.client: NM.Client | None = None
        self.page = Adw.PreferencesPage()

        # --- Toggle group -------------------------------------------------
        toggle_group = Adw.PreferencesGroup(title="Wireless")
        self.wifi_switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        toggle_row = Adw.ActionRow(title="Wi-Fi", subtitle="Enable or disable Wi-Fi")
        toggle_row.add_suffix(self.wifi_switch)
        toggle_row.set_activatable_widget(self.wifi_switch)
        toggle_group.add(toggle_row)
        self.page.add(toggle_group)

        # --- Known Networks Modal Button ----------------------------------
        self.known_row = Adw.ActionRow(
            title="Known Networks",
            subtitle="Manage saved Wi-Fi networks",
            activatable=True
        )
        self.known_btn = Gtk.Button(
            icon_name="go-next-symbolic",
            valign=Gtk.Align.CENTER,
            css_classes=["flat"]
        )
        self.known_row.add_suffix(self.known_btn)
        self.known_row.connect("activated", self._on_known_networks_clicked)
        self.known_btn.connect("clicked", self._on_known_networks_clicked)
        toggle_group.add(self.known_row)

        # --- Hotspot ------------------------------------------------------
        self.hotspot_switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        self.hotspot_row = Adw.ActionRow(
            title="Wi-Fi Hotspot",
            subtitle="Share your internet connection",
            activatable=True
        )
        self.hotspot_row.add_suffix(self.hotspot_switch)
        self.hotspot_row.set_activatable_widget(self.hotspot_switch)
        self.hotspot_switch.connect("notify::active", self._on_hotspot_toggle)
        toggle_group.add(self.hotspot_row)

        self.hotspot_password_entry = Gtk.PasswordEntry(
            valign=Gtk.Align.CENTER, 
            show_peek_icon=True
        )
        self.hotspot_password_entry.set_text("12345678")
        self.hotspot_password_row = Adw.ActionRow(title="Hotspot Password (min. 8 chars)")
        self.hotspot_password_row.add_suffix(self.hotspot_password_entry)
        toggle_group.add(self.hotspot_password_row)

        # --- Available Networks group -------------------------------------
        self.networks_group = Adw.PreferencesGroup(title="Available Networks")

        refresh_btn = Gtk.Button(
            icon_name="view-refresh-symbolic",
            valign=Gtk.Align.CENTER,
            css_classes=["flat"],
            tooltip_text="Rescan",
        )
        refresh_btn.connect("clicked", self._on_refresh)
        self.networks_group.set_header_suffix(refresh_btn)

        self.page.add(self.networks_group)

        self.saved_dialog = None
        self.saved_group = None
        self.saved_group_container = None

        # --- Init NM client async ----------------------------------------
        NM.Client.new_async(None, self._on_client_ready)

    # ---- NM client init ---------------------------------------------------

    def _on_client_ready(self, _source, result):
        try:
            self.client = NM.Client.new_finish(result)
        except Exception as e:
            self._show_error(f"NetworkManager unavailable: {e}")
            return

        # Wire switch to Wi-Fi state
        enabled = self.client.wireless_get_enabled()
        self.wifi_switch.set_active(enabled)
        self.wifi_switch.connect("notify::active", self._on_wifi_toggle)

        self._refresh_networks()
        self._refresh_saved()

    # ---- Toggle -----------------------------------------------------------

    def _on_wifi_toggle(self, switch, _pspec):
        if self.client:
            self.client.wireless_set_enabled(switch.get_active())
            GLib.timeout_add(1500, self._refresh_networks)

    def _on_hotspot_toggle(self, switch, _pspec):
        import subprocess
        active = switch.get_active()
        try:
            if active:
                pwd = self.hotspot_password_entry.get_text()
                if pwd and len(pwd) >= 8:
                    subprocess.Popen(["nmcli", "device", "wifi", "hotspot", "password", pwd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    self.hotspot_password_entry.set_text("12345678")
                    subprocess.Popen(["nmcli", "device", "wifi", "hotspot", "password", "12345678"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen(["nmcli", "connection", "down", "Hotspot"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Hotspot toggle failed: {e}")

    def _on_known_networks_clicked(self, *args):
        self._show_known_networks_dialog()

    # ---- Network list -----------------------------------------------------

    def _clear_group(self, group):
        """Remove all rows from a preferences group."""
        while True:
            child = group.get_first_child()
            # Skip the header/frame — Adw groups wrap rows in a GtkListBox
            # We iterate the internal listbox
            break  # fall through to alternative approach

        # Alternative: rebuild group by removing/adding
        # We can't easily iterate Adw groups, so we track children ourselves
        pass

    def _refresh_networks(self):
        """Rescan and repopulate the available networks list."""
        if not self.client:
            return

        # Remove old rows by rebuilding the group
        self.page.remove(self.networks_group)
        self.networks_group = Adw.PreferencesGroup(title="Available Networks")
        refresh_btn = Gtk.Button(
            icon_name="view-refresh-symbolic",
            valign=Gtk.Align.CENTER,
            css_classes=["flat"],
            tooltip_text="Rescan",
        )
        refresh_btn.connect("clicked", self._on_refresh)
        self.networks_group.set_header_suffix(refresh_btn)

        # Find wireless device
        devices = self.client.get_devices()
        wifi_dev = None
        for d in devices:
            if d.get_device_type() == NM.DeviceType.WIFI:
                wifi_dev = d
                break

        if not wifi_dev:
            row = Adw.ActionRow(title="No Wi-Fi adapter found")
            self.networks_group.add(row)
            self.page.add(self.networks_group)
            return

        # Request a fresh scan
        try:
            wifi_dev.request_scan_async(None, None, None)
        except Exception:
            pass

        # Gather APs, dedup by SSID
        aps = wifi_dev.get_access_points()
        seen = set()
        active_conn = wifi_dev.get_active_connection()
        active_ssid = None
        if active_conn:
            conn = active_conn.get_connection()
            if conn:
                s_wifi = conn.get_setting_wireless()
                if s_wifi:
                    ssid_bytes = s_wifi.get_ssid()
                    if ssid_bytes:
                        active_ssid = ssid_bytes.get_data().decode("utf-8", errors="replace")

        for ap in aps:
            ssid_bytes = ap.get_ssid()
            if not ssid_bytes:
                continue
            ssid = ssid_bytes.get_data().decode("utf-8", errors="replace")
            if not ssid or ssid in seen:
                continue
            seen.add(ssid)

            strength = ap.get_strength()
            security = _get_ap_security(ap)

            row = Adw.ActionRow(
                title=ssid,
                subtitle=f"{security} · {strength}%",
                activatable=True,
            )
            row.add_prefix(Gtk.Image.new_from_icon_name(_signal_icon(strength)))

            if security != "Open":
                row.add_prefix(
                    Gtk.Image.new_from_icon_name("channel-secure-symbolic")
                )

            if ssid == active_ssid:
                row.add_suffix(
                    Gtk.Label(label="Connected", css_classes=["dim-label"])
                )
            else:
                connect_btn = Gtk.Button(
                    label="Connect",
                    valign=Gtk.Align.CENTER,
                    css_classes=["suggested-action", "pill"],
                )
                connect_btn._ssid = ssid
                connect_btn._security = security
                connect_btn._ap = ap
                connect_btn._device = wifi_dev
                connect_btn.connect("clicked", self._on_connect_clicked)
                row.add_suffix(connect_btn)

            self.networks_group.add(row)

        if not seen:
            row = Adw.ActionRow(title="No networks found", subtitle="Try rescanning")
            self.networks_group.add(row)

        # Re-insert groups in order
        self.page.add(self.networks_group)

    def _show_known_networks_dialog(self):
        self.saved_dialog = Adw.PreferencesWindow(
            transient_for=self.win,
            modal=True,
            title="Known Networks",
            default_width=400,
            default_height=500,
            search_enabled=False
        )
        page = Adw.PreferencesPage()
        
        # Keep a reference to the group so we can manipulate it later if needed
        self.saved_group_container = page
        self._refresh_saved()
        
        self.saved_dialog.add(page)
        self.saved_dialog.present()

    def _refresh_saved(self):
        """Populate saved (known) connections."""
        if not hasattr(self, 'saved_dialog') or not self.saved_dialog:
            return
        if not self.saved_group_container:
            return

        if self.saved_group:
            self.saved_group_container.remove(self.saved_group)

        self.saved_group = Adw.PreferencesGroup(title="Saved Networks")
        self.saved_group_container.add(self.saved_group)

        connections = self.client.get_connections() if self.client else []
        count = 0
        for conn in connections:
            s_wifi = conn.get_setting_wireless()
            if not s_wifi:
                continue
            ssid_bytes = s_wifi.get_ssid()
            if not ssid_bytes:
                continue
            ssid = ssid_bytes.get_data().decode("utf-8", errors="replace")

            row = Adw.ActionRow(title=ssid, subtitle="Saved")
            row.add_prefix(
                Gtk.Image.new_from_icon_name("network-wireless-symbolic")
            )

            forget_btn = Gtk.Button(
                icon_name="user-trash-symbolic",
                valign=Gtk.Align.CENTER,
                css_classes=["flat", "error"],
                tooltip_text="Forget network",
            )
            forget_btn._conn = conn
            forget_btn._ssid = ssid
            forget_btn.connect("clicked", self._on_forget_clicked)
            row.add_suffix(forget_btn)

            self.saved_group.add(row)
            count += 1

        if count == 0:
            row = Adw.ActionRow(title="No saved networks")
            self.saved_group.add(row)

    # ---- Connect ----------------------------------------------------------

    def _on_connect_clicked(self, btn):
        ssid = btn._ssid
        security = btn._security
        ap = btn._ap
        device = btn._device

        if security == "Open":
            self._do_connect(ssid, None, ap, device)
        else:
            self._ask_password(ssid, ap, device)

    def _ask_password(self, ssid, ap, device):
        """Show an Adw.AlertDialog to input the Wi-Fi password."""
        dialog = Adw.AlertDialog(
            heading=f"Connect to {ssid}",
            body="Enter the network password:",
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("connect", "Connect")
        dialog.set_response_appearance("connect", Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response("connect")
        dialog.set_close_response("cancel")

        entry = Gtk.PasswordEntry(
            show_peek_icon=True,
            placeholder_text="Password",
            hexpand=True,
        )
        entry.set_margin_start(12)
        entry.set_margin_end(12)
        dialog.set_extra_child(entry)

        dialog.connect(
            "response",
            self._on_password_response,
            entry,
            ssid,
            ap,
            device,
        )
        dialog.present(self.win)

    def _on_password_response(self, dialog, response, entry, ssid, ap, device):
        if response != "connect":
            return
        password = entry.get_text()
        if password:
            self._do_connect(ssid, password, ap, device)

    def _do_connect(self, ssid, password, ap, device):
        """Create an NM connection profile and activate it."""
        if not self.client:
            return

        profile = NM.SimpleConnection.new()

        # 802-11-wireless setting
        s_conn = NM.SettingConnection.new()
        s_conn.set_property("id", ssid)
        s_conn.set_property("type", "802-11-wireless")
        s_conn.set_property("autoconnect", True)
        profile.add_setting(s_conn)

        s_wifi = NM.SettingWireless.new()
        s_wifi.set_property("ssid", GLib.Bytes.new(ssid.encode("utf-8")))
        profile.add_setting(s_wifi)

        if password:
            s_sec = NM.SettingWirelessSecurity.new()
            s_sec.set_property("key-mgmt", "wpa-psk")
            s_sec.set_property("psk", password)
            profile.add_setting(s_sec)

        self.client.add_and_activate_connection_async(
            profile, device, ap.get_path(), None, self._on_connect_done, ssid
        )

    def _on_connect_done(self, client, result, ssid):
        try:
            client.add_and_activate_connection_finish(result)
        except Exception as e:
            self._show_error(f"Failed to connect to {ssid}: {e}")
            return
        GLib.timeout_add(2000, self._refresh_networks)

    # ---- Forget -----------------------------------------------------------

    def _on_forget_clicked(self, btn):
        conn = btn._conn
        ssid = btn._ssid

        dialog = Adw.AlertDialog(
            heading=f"Forget \"{ssid}\"?",
            body="You will need to re-enter the password to connect again.",
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("forget", "Forget")
        dialog.set_response_appearance("forget", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("cancel")
        dialog.set_close_response("cancel")
        dialog.connect("response", self._on_forget_response, conn)
        
        present_window = getattr(self, "saved_dialog", self.win)
        dialog.present(present_window)

    def _on_forget_response(self, dialog, response, conn):
        if response != "forget":
            return
        conn.delete_async(None, self._on_forget_done, None)

    def _on_forget_done(self, conn, result, _data):
        try:
            conn.delete_finish(result)
        except Exception:
            pass
        self._refresh_saved()
        self._refresh_networks()

    # ---- Refresh ----------------------------------------------------------

    def _on_refresh(self, _btn):
        self._refresh_networks()
        self._refresh_saved()

    # ---- Errors -----------------------------------------------------------

    def _show_error(self, msg):
        dialog = Adw.AlertDialog(heading="Error", body=msg)
        dialog.add_response("ok", "OK")
        dialog.present(self.win)


def build_wifi_page(win) -> Adw.PreferencesPage:
    """Build and return the Wi-Fi preferences page."""
    section = WifiSection(win)
    # Keep reference to prevent GC
    section.page._section = section
    return section.page
