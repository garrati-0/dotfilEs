"""Power Management section — lock, suspend, reboot, shutdown, scheduled shutdown."""

import subprocess

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib


def _run_power_cmd(cmd: list[str]):
    """Run a power command in background."""
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class PowerSection:
    """Manages the Power Management preferences page."""

    def __init__(self, win):
        self.win = win
        self.page = Adw.PreferencesPage()
        self._shutdown_timer_id = None
        self._shutdown_remaining = 0

        # --- Quick Actions group ------------------------------------------
        actions_group = Adw.PreferencesGroup(
            title="Power Controls",
        )
        
        actions_expander = Adw.ExpanderRow(
            title="Quick Actions",
            subtitle="Session and system power controls",
        )

        # Lock
        lock_row = Adw.ActionRow(
            title="Lock Screen",
            subtitle="Lock the current session",
        )
        lock_row.add_prefix(Gtk.Image.new_from_icon_name("system-lock-screen-symbolic"))
        lock_btn = Gtk.Button(
            icon_name="system-lock-screen-symbolic",
            valign=Gtk.Align.CENTER,
            css_classes=["flat"],
            tooltip_text="Lock",
        )
        lock_btn.connect("clicked", self._on_lock)
        lock_row.add_suffix(lock_btn)
        lock_row.set_activatable_widget(lock_btn)
        actions_expander.add_row(lock_row)

        # Suspend
        suspend_row = Adw.ActionRow(
            title="Suspend",
            subtitle="Put the system to sleep",
        )
        suspend_row.add_prefix(Gtk.Image.new_from_icon_name("weather-clear-night-symbolic"))
        suspend_btn = Gtk.Button(
            icon_name="weather-clear-night-symbolic",
            valign=Gtk.Align.CENTER,
            css_classes=["flat"],
            tooltip_text="Suspend",
        )
        suspend_btn.connect("clicked", self._on_suspend)
        suspend_row.add_suffix(suspend_btn)
        suspend_row.set_activatable_widget(suspend_btn)
        actions_expander.add_row(suspend_row)

        # Hibernate
        hibernate_row = Adw.ActionRow(
            title="Hibernate",
            subtitle="Save state to disk and power off",
        )
        hibernate_row.add_prefix(Gtk.Image.new_from_icon_name("media-playback-pause-symbolic"))
        hibernate_btn = Gtk.Button(
            icon_name="media-playback-pause-symbolic",
            valign=Gtk.Align.CENTER,
            css_classes=["flat"],
            tooltip_text="Hibernate",
        )
        hibernate_btn.connect("clicked", self._on_hibernate)
        hibernate_row.add_suffix(hibernate_btn)
        hibernate_row.set_activatable_widget(hibernate_btn)
        actions_expander.add_row(hibernate_row)

        # Reboot
        reboot_row = Adw.ActionRow(
            title="Reboot",
            subtitle="Restart the system",
        )
        reboot_row.add_prefix(Gtk.Image.new_from_icon_name("system-reboot-symbolic"))
        reboot_btn = Gtk.Button(
            icon_name="system-reboot-symbolic",
            valign=Gtk.Align.CENTER,
            css_classes=["flat"],
            tooltip_text="Reboot",
        )
        reboot_btn.connect("clicked", self._on_reboot)
        reboot_row.add_suffix(reboot_btn)
        reboot_row.set_activatable_widget(reboot_btn)
        actions_expander.add_row(reboot_row)

        # Shutdown
        shutdown_row = Adw.ActionRow(
            title="Shutdown",
            subtitle="Power off the system",
        )
        shutdown_row.add_prefix(Gtk.Image.new_from_icon_name("system-shutdown-symbolic"))
        shutdown_btn = Gtk.Button(
            icon_name="system-shutdown-symbolic",
            valign=Gtk.Align.CENTER,
            css_classes=["destructive-action"],
            tooltip_text="Shutdown",
        )
        shutdown_btn.connect("clicked", self._on_shutdown)
        shutdown_row.add_suffix(shutdown_btn)
        shutdown_row.set_activatable_widget(shutdown_btn)
        actions_expander.add_row(shutdown_row)

        # Logout
        logout_row = Adw.ActionRow(
            title="Log Out",
            subtitle="End the current Hyprland session",
        )
        logout_row.add_prefix(Gtk.Image.new_from_icon_name("system-log-out-symbolic"))
        logout_btn = Gtk.Button(
            icon_name="system-log-out-symbolic",
            valign=Gtk.Align.CENTER,
            css_classes=["flat"],
            tooltip_text="Log Out",
        )
        logout_btn.connect("clicked", self._on_logout)
        logout_row.add_suffix(logout_btn)
        logout_row.set_activatable_widget(logout_btn)
        actions_expander.add_row(logout_row)

        actions_group.add(actions_expander)
        self.page.add(actions_group)

        # --- Scheduled Shutdown group -------------------------------------
        sched_group = Adw.PreferencesGroup(
            title="Scheduled Shutdown",
            description="Set a timer to automatically shut down",
        )

        # Timer dropdown (minutes)
        self.timer_options = ["5 min", "10 min", "15 min", "30 min",
                              "45 min", "60 min", "90 min", "120 min"]
        self.timer_values = [5, 10, 15, 30, 45, 60, 90, 120]

        self.timer_model = Gtk.StringList.new(self.timer_options)
        self.timer_dropdown = Gtk.DropDown(
            model=self.timer_model,
            valign=Gtk.Align.CENTER,
        )
        self.timer_dropdown.set_selected(3)  # default 30 min

        timer_row = Adw.ActionRow(title="Shutdown In")
        timer_row.add_suffix(self.timer_dropdown)
        sched_group.add(timer_row)

        # Start / Cancel buttons
        btn_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
            halign=Gtk.Align.CENTER,
            margin_top=8,
            margin_bottom=8,
        )

        self.start_btn = Gtk.Button(
            label="Start Timer",
            css_classes=["suggested-action", "pill"],
        )
        self.start_btn.connect("clicked", self._on_start_timer)

        self.cancel_btn = Gtk.Button(
            label="Cancel Timer",
            css_classes=["destructive-action", "pill"],
            sensitive=False,
        )
        self.cancel_btn.connect("clicked", self._on_cancel_timer)

        btn_box.append(self.start_btn)
        btn_box.append(self.cancel_btn)

        # Status label
        self.timer_status = Gtk.Label(
            label="No timer active",
            css_classes=["dim-label"],
            valign=Gtk.Align.CENTER,
        )

        status_row = Adw.ActionRow(title="Status")
        status_row.add_suffix(self.timer_status)
        sched_group.add(status_row)

        # Add button box as a separate row
        btn_row = Adw.PreferencesGroup()
        btn_row.add(btn_box)
        self.page.add(sched_group)
        self.page.add(btn_row)

        # --- Power Profile (if available) ---------------------------------
        profile_group = Adw.PreferencesGroup(
            title="Performance Profile",
            description="Adjust CPU power profile (requires power-profiles-daemon)",
        )

        self.profile_options = ["Power Saver", "Balanced", "Performance"]
        self.profile_values = ["power-saver", "balanced", "performance"]
        self.profile_model = Gtk.StringList.new(self.profile_options)
        self.profile_dropdown = Gtk.DropDown(
            model=self.profile_model,
            valign=Gtk.Align.CENTER,
        )

        # Read current profile
        current = self._get_power_profile()
        if current in self.profile_values:
            self.profile_dropdown.set_selected(self.profile_values.index(current))
        else:
            self.profile_dropdown.set_selected(1)

        self.profile_dropdown.connect("notify::selected", self._on_profile_changed)

        profile_row = Adw.ActionRow(title="Active Profile")
        profile_row.add_prefix(
            Gtk.Image.new_from_icon_name("power-profile-balanced-symbolic")
        )
        profile_row.add_suffix(self.profile_dropdown)
        profile_group.add(profile_row)

        self.page.add(profile_group)

    # ---- Power actions ----------------------------------------------------

    def _confirm_action(self, title, body, action_label, callback):
        """Show a confirmation dialog before executing a power action."""
        dialog = Adw.AlertDialog(heading=title, body=body)
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("confirm", action_label)
        dialog.set_response_appearance("confirm", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("cancel")
        dialog.set_close_response("cancel")
        dialog.connect("response", lambda d, r: callback() if r == "confirm" else None)
        dialog.present(self.win)

    def _on_lock(self, _btn):
        _run_power_cmd(["loginctl", "lock-session"])

    def _on_suspend(self, _btn):
        self._confirm_action("Suspend?", "The system will go to sleep.",
                             "Suspend", lambda: _run_power_cmd(["systemctl", "suspend"]))

    def _on_hibernate(self, _btn):
        self._confirm_action("Hibernate?", "The system will save state and power off.",
                             "Hibernate", lambda: _run_power_cmd(["systemctl", "hibernate"]))

    def _on_reboot(self, _btn):
        self._confirm_action("Reboot?", "The system will restart.",
                             "Reboot", lambda: _run_power_cmd(["systemctl", "reboot"]))

    def _on_shutdown(self, _btn):
        self._confirm_action("Shut Down?", "The system will power off.",
                             "Shut Down", lambda: _run_power_cmd(["systemctl", "poweroff"]))

    def _on_logout(self, _btn):
        self._confirm_action("Log Out?", "Your Hyprland session will end.",
                             "Log Out", lambda: _run_power_cmd(["hyprctl", "dispatch", "exit"]))

    # ---- Scheduled Shutdown -----------------------------------------------

    def _on_start_timer(self, _btn):
        idx = self.timer_dropdown.get_selected()
        minutes = self.timer_values[idx]
        self._shutdown_remaining = minutes * 60

        self.start_btn.set_sensitive(False)
        self.cancel_btn.set_sensitive(True)
        self.timer_dropdown.set_sensitive(False)

        self._update_timer_label()
        self._shutdown_timer_id = GLib.timeout_add_seconds(1, self._tick_timer)

    def _on_cancel_timer(self, _btn):
        if self._shutdown_timer_id is not None:
            GLib.source_remove(self._shutdown_timer_id)
            self._shutdown_timer_id = None

        self._shutdown_remaining = 0
        self.start_btn.set_sensitive(True)
        self.cancel_btn.set_sensitive(False)
        self.timer_dropdown.set_sensitive(True)
        self.timer_status.set_label("Timer cancelled")
        self.timer_status.set_css_classes(["dim-label"])

    def _tick_timer(self):
        self._shutdown_remaining -= 1
        if self._shutdown_remaining <= 0:
            self.timer_status.set_label("Shutting down...")
            self.timer_status.set_css_classes(["error-label"])
            _run_power_cmd(["systemctl", "poweroff"])
            return False

        self._update_timer_label()
        return True

    def _update_timer_label(self):
        m = self._shutdown_remaining // 60
        s = self._shutdown_remaining % 60
        self.timer_status.set_label(f"Shutdown in {m}:{s:02d}")
        if self._shutdown_remaining < 60:
            self.timer_status.set_css_classes(["error-label"])
        elif self._shutdown_remaining < 300:
            self.timer_status.set_css_classes(["warning-label"])
        else:
            self.timer_status.set_css_classes(["accent-label"])

    # ---- Power Profile ----------------------------------------------------

    def _get_power_profile(self) -> str:
        try:
            out = subprocess.check_output(
                ["powerprofilesctl", "get"], text=True, timeout=3
            ).strip()
            return out
        except Exception:
            return "balanced"

    def _on_profile_changed(self, dropdown, _pspec):
        idx = dropdown.get_selected()
        if idx < len(self.profile_values):
            val = self.profile_values[idx]
            subprocess.Popen(
                ["powerprofilesctl", "set", val],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )


def build_power_page(win) -> Adw.PreferencesPage:
    """Build and return the Power Management preferences page."""
    section = PowerSection(win)
    return section.page
