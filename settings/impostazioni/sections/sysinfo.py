"""System Information section — comprehensive hardware / OS details."""

import os
import platform
import socket
import subprocess
import re

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw


def _cpu_model() -> str:
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return "Unknown"


def _cpu_cores() -> str:
    try:
        physical = set()
        logical = 0
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("processor"):
                    logical += 1
                if line.startswith("core id"):
                    physical.add(line.split(":")[1].strip())
        phys = len(physical) if physical else logical
        return f"{phys} cores / {logical} threads"
    except Exception:
        return "Unknown"


def _total_ram() -> str:
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    kb = int(line.split()[1])
                    gib = kb / 1024 / 1024
                    return f"{gib:.1f} GiB"
    except Exception:
        pass
    return "Unknown"


def _gpu_info() -> str:
    """Try to get GPU info from lspci."""
    try:
        out = subprocess.check_output(
            ["lspci"], text=True, timeout=3
        )
        for line in out.splitlines():
            low = line.lower()
            if "vga" in low or "3d" in low or "display" in low:
                # Line format: "00:02.0 VGA compatible controller: Intel..."
                return line.split(":", 2)[2].strip() if line.count(":") >= 2 else line
        return "Unknown"
    except Exception:
        return "Unknown"


def _battery_info() -> str:
    """Read battery status from /sys/class/power_supply."""
    base = "/sys/class/power_supply"
    try:
        for entry in os.listdir(base):
            path = os.path.join(base, entry)
            type_path = os.path.join(path, "type")
            if os.path.isfile(type_path):
                with open(type_path) as f:
                    if f.read().strip() != "Battery":
                        continue
            cap_path = os.path.join(path, "capacity")
            status_path = os.path.join(path, "status")
            if os.path.isfile(cap_path):
                with open(cap_path) as f:
                    cap = f.read().strip()
                status = ""
                if os.path.isfile(status_path):
                    with open(status_path) as f:
                        status = f.read().strip()
                return f"{cap}% ({status})"
    except Exception:
        pass
    return "No battery detected"


def _hyprland_version() -> str:
    try:
        out = subprocess.check_output(
            ["hyprctl", "version"], text=True, timeout=3
        )
        for line in out.splitlines():
            if "Tag:" in line:
                return line.split("Tag:", 1)[1].strip()
            if line.startswith("Hyprland"):
                return line.strip()
        return out.strip().splitlines()[0] if out.strip() else "Unknown"
    except Exception:
        return "Not running / not found"


def _disk_info() -> str:
    try:
        st = os.statvfs("/")
        total = st.f_frsize * st.f_blocks
        used = total - st.f_frsize * st.f_bfree
        total_gib = total / (1024 ** 3)
        used_gib = used / (1024 ** 3)
        return f"{used_gib:.1f} / {total_gib:.1f} GiB"
    except Exception:
        return "Unknown"


def _uptime() -> str:
    try:
        with open("/proc/uptime") as f:
            secs = float(f.read().split()[0])
        days = int(secs // 86400)
        hours = int((secs % 86400) // 3600)
        mins = int((secs % 3600) // 60)
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        parts.append(f"{mins}m")
        return " ".join(parts)
    except Exception:
        return "Unknown"


def _desktop_session() -> str:
    return os.environ.get("XDG_CURRENT_DESKTOP", "Unknown")


def _display_server() -> str:
    session = os.environ.get("XDG_SESSION_TYPE", "Unknown")
    return session.capitalize()


def _shell_version() -> str:
    shell = os.environ.get("SHELL", "/bin/bash")
    try:
        out = subprocess.check_output(
            [shell, "--version"], text=True, timeout=3
        )
        first_line = out.strip().splitlines()[0]
        return first_line
    except Exception:
        return os.path.basename(shell)


def build_sysinfo_page(win) -> Adw.PreferencesPage:
    """Build and return the System Info preferences page."""
    page = Adw.PreferencesPage()

    # ---- Device group ----------------------------------------------------
    device_group = Adw.PreferencesGroup(title="Device")

    hostname_row = Adw.ActionRow(title="Hostname", subtitle=socket.gethostname())
    hostname_row.add_prefix(Gtk.Image.new_from_icon_name("computer-symbolic"))
    device_group.add(hostname_row)

    uptime_row = Adw.ActionRow(title="Uptime", subtitle=_uptime())
    uptime_row.add_prefix(Gtk.Image.new_from_icon_name("preferences-system-time-symbolic"))
    device_group.add(uptime_row)

    page.add(device_group)

    # ---- Hardware group --------------------------------------------------
    hw_group = Adw.PreferencesGroup(title="Hardware")

    cpu_row = Adw.ActionRow(title="Processor", subtitle=_cpu_model())
    cpu_row.add_prefix(Gtk.Image.new_from_icon_name("processor-symbolic"))
    hw_group.add(cpu_row)

    cores_row = Adw.ActionRow(title="CPU Cores", subtitle=_cpu_cores())
    cores_row.add_prefix(Gtk.Image.new_from_icon_name("preferences-other-symbolic"))
    hw_group.add(cores_row)

    ram_row = Adw.ActionRow(title="Memory", subtitle=_total_ram())
    ram_row.add_prefix(Gtk.Image.new_from_icon_name("memory-symbolic"))
    hw_group.add(ram_row)

    gpu_row = Adw.ActionRow(title="Graphics", subtitle=_gpu_info())
    gpu_row.add_prefix(Gtk.Image.new_from_icon_name("video-display-symbolic"))
    hw_group.add(gpu_row)

    disk_row = Adw.ActionRow(title="Disk Usage (/)", subtitle=_disk_info())
    disk_row.add_prefix(Gtk.Image.new_from_icon_name("drive-harddisk-symbolic"))
    hw_group.add(disk_row)

    batt_row = Adw.ActionRow(title="Battery", subtitle=_battery_info())
    batt_row.add_prefix(Gtk.Image.new_from_icon_name("battery-symbolic"))
    hw_group.add(batt_row)

    page.add(hw_group)

    # ---- Software group --------------------------------------------------
    sw_group = Adw.PreferencesGroup(title="Software")

    kernel_row = Adw.ActionRow(title="Kernel", subtitle=platform.release())
    kernel_row.add_prefix(Gtk.Image.new_from_icon_name("emblem-system-symbolic"))
    sw_group.add(kernel_row)

    os_row = Adw.ActionRow(
        title="Operating System",
        subtitle=f"{platform.system()} {platform.machine()}",
    )
    os_row.add_prefix(Gtk.Image.new_from_icon_name("emblem-system-symbolic"))
    sw_group.add(os_row)

    hypr_row = Adw.ActionRow(title="Hyprland", subtitle=_hyprland_version())
    hypr_row.add_prefix(Gtk.Image.new_from_icon_name("preferences-desktop-display-symbolic"))
    sw_group.add(hypr_row)

    desktop_row = Adw.ActionRow(title="Desktop", subtitle=_desktop_session())
    desktop_row.add_prefix(Gtk.Image.new_from_icon_name("user-desktop-symbolic"))
    sw_group.add(desktop_row)

    display_row = Adw.ActionRow(title="Display Server", subtitle=_display_server())
    display_row.add_prefix(Gtk.Image.new_from_icon_name("video-display-symbolic"))
    sw_group.add(display_row)

    shell_row = Adw.ActionRow(title="Shell", subtitle=_shell_version())
    shell_row.add_prefix(Gtk.Image.new_from_icon_name("utilities-terminal-symbolic"))
    sw_group.add(shell_row)

    page.add(sw_group)

    return page
