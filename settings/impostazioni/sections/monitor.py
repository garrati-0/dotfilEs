"""System Monitor section — live CPU, RAM, Disk, Network gauges."""

import os
import time

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib


# ---------------------------------------------------------------------------
# Data helpers — read from /proc so we avoid external dependencies
# ---------------------------------------------------------------------------

_prev_cpu = None          # (idle, total) from last reading
_prev_net = None          # (rx, tx, time) from last reading


def _read_cpu_percent() -> float:
    """Read CPU usage % from /proc/stat (delta between calls)."""
    global _prev_cpu
    try:
        with open("/proc/stat") as f:
            parts = f.readline().split()
        # user nice system idle iowait irq softirq steal
        values = list(map(int, parts[1:9]))
        idle = values[3] + values[4]
        total = sum(values)

        if _prev_cpu is None:
            _prev_cpu = (idle, total)
            return 0.0

        d_idle = idle - _prev_cpu[0]
        d_total = total - _prev_cpu[1]
        _prev_cpu = (idle, total)

        if d_total == 0:
            return 0.0
        return (1.0 - d_idle / d_total) * 100.0
    except Exception:
        return 0.0


def _read_mem() -> tuple[float, float, float]:
    """Return (used_gib, total_gib, percent)."""
    try:
        info = {}
        with open("/proc/meminfo") as f:
            for line in f:
                parts = line.split()
                info[parts[0].rstrip(":")] = int(parts[1])
        total = info["MemTotal"]
        available = info.get("MemAvailable", info.get("MemFree", total))
        used = total - available
        total_gib = total / 1048576
        used_gib = used / 1048576
        percent = used / total * 100 if total else 0
        return used_gib, total_gib, percent
    except Exception:
        return 0.0, 0.0, 0.0


def _read_swap() -> tuple[float, float, float]:
    """Return (used_gib, total_gib, percent) for swap."""
    try:
        info = {}
        with open("/proc/meminfo") as f:
            for line in f:
                parts = line.split()
                info[parts[0].rstrip(":")] = int(parts[1])
        total = info.get("SwapTotal", 0)
        free = info.get("SwapFree", total)
        used = total - free
        if total == 0:
            return 0.0, 0.0, 0.0
        return used / 1048576, total / 1048576, used / total * 100
    except Exception:
        return 0.0, 0.0, 0.0


def _read_disk() -> tuple[float, float, float]:
    """Return (used_gib, total_gib, percent) for /."""
    try:
        st = os.statvfs("/")
        total = st.f_frsize * st.f_blocks
        free = st.f_frsize * st.f_bfree
        used = total - free
        total_gib = total / (1024 ** 3)
        used_gib = used / (1024 ** 3)
        percent = used / total * 100 if total else 0
        return used_gib, total_gib, percent
    except Exception:
        return 0.0, 0.0, 0.0


def _read_net_speed() -> tuple[float, float]:
    """Return (download_kBs, upload_kBs) since last call."""
    global _prev_net
    try:
        rx_total = 0
        tx_total = 0
        with open("/proc/net/dev") as f:
            for line in f:
                if ":" not in line:
                    continue
                iface, data = line.split(":", 1)
                iface = iface.strip()
                if iface == "lo":
                    continue
                parts = data.split()
                rx_total += int(parts[0])
                tx_total += int(parts[8])

        now = time.monotonic()
        if _prev_net is None:
            _prev_net = (rx_total, tx_total, now)
            return 0.0, 0.0

        dt = now - _prev_net[2]
        if dt <= 0:
            dt = 1.0
        dl = (rx_total - _prev_net[0]) / 1024 / dt
        ul = (tx_total - _prev_net[1]) / 1024 / dt
        _prev_net = (rx_total, tx_total, now)
        return max(0, dl), max(0, ul)
    except Exception:
        return 0.0, 0.0


def _read_uptime() -> str:
    """Return human-readable uptime."""
    try:
        with open("/proc/uptime") as f:
            secs = float(f.read().split()[0])
        hours = int(secs // 3600)
        mins = int((secs % 3600) // 60)
        if hours > 0:
            return f"{hours}h {mins}m"
        return f"{mins}m"
    except Exception:
        return "—"


def _read_load() -> str:
    """Return 1/5/15 min load averages."""
    try:
        avgs = os.getloadavg()
        return f"{avgs[0]:.2f}  {avgs[1]:.2f}  {avgs[2]:.2f}"
    except Exception:
        return "—"


def _read_temp() -> str:
    """Read CPU temperature from thermal zones."""
    base = "/sys/class/thermal"
    try:
        for entry in sorted(os.listdir(base)):
            tpath = os.path.join(base, entry, "temp")
            if os.path.isfile(tpath):
                with open(tpath) as f:
                    val = int(f.read().strip())
                return f"{val / 1000:.0f} °C"
    except Exception:
        pass
    return "—"


# ---------------------------------------------------------------------------
# Gauge CSS class helper
# ---------------------------------------------------------------------------

def _gauge_css(pct: float) -> str:
    if pct >= 90:
        return "gauge-value-crit"
    elif pct >= 70:
        return "gauge-value-warn"
    return "gauge-value"


# ---------------------------------------------------------------------------
# Monitor Section
# ---------------------------------------------------------------------------

class MonitorSection:
    """Live system monitor with auto-refreshing gauges."""

    def __init__(self, win):
        self.win = win
        self.page = Adw.PreferencesPage()

        # --- CPU group ----------------------------------------------------
        cpu_group = Adw.PreferencesGroup(title="Processor")

        self.cpu_label = Gtk.Label(label="0%", css_classes=["gauge-value"],
                                   valign=Gtk.Align.CENTER, width_chars=5)
        self.cpu_bar = Gtk.LevelBar(min_value=0, max_value=100, hexpand=True,
                                     valign=Gtk.Align.CENTER)
        self.cpu_bar.set_value(0)
        cpu_row = Adw.ActionRow(title="CPU Usage")
        cpu_row.add_suffix(self.cpu_bar)
        cpu_row.add_suffix(self.cpu_label)
        cpu_group.add(cpu_row)

        self.load_label = Gtk.Label(label="—", css_classes=["dim-label"],
                                    valign=Gtk.Align.CENTER)
        load_row = Adw.ActionRow(title="Load Average",
                                  subtitle="1 min · 5 min · 15 min")
        load_row.add_suffix(self.load_label)
        cpu_group.add(load_row)

        self.temp_label = Gtk.Label(label="—", css_classes=["dim-label"],
                                    valign=Gtk.Align.CENTER)
        temp_row = Adw.ActionRow(title="CPU Temperature")
        temp_row.add_suffix(self.temp_label)
        cpu_group.add(temp_row)

        self.page.add(cpu_group)

        # --- Memory group -------------------------------------------------
        mem_group = Adw.PreferencesGroup(title="Memory")

        self.mem_label = Gtk.Label(label="0%", css_classes=["gauge-value"],
                                   valign=Gtk.Align.CENTER, width_chars=5)
        self.mem_bar = Gtk.LevelBar(min_value=0, max_value=100, hexpand=True,
                                     valign=Gtk.Align.CENTER)
        self.mem_detail = Gtk.Label(label="", css_classes=["dim-label"],
                                    valign=Gtk.Align.CENTER, width_chars=14)
        mem_row = Adw.ActionRow(title="RAM Usage")
        mem_row.add_suffix(self.mem_bar)
        mem_row.add_suffix(self.mem_detail)
        mem_row.add_suffix(self.mem_label)
        mem_group.add(mem_row)

        self.swap_label = Gtk.Label(label="—", css_classes=["dim-label"],
                                    valign=Gtk.Align.CENTER)
        swap_row = Adw.ActionRow(title="Swap Usage")
        swap_row.add_suffix(self.swap_label)
        mem_group.add(swap_row)

        self.page.add(mem_group)

        # --- Disk group ---------------------------------------------------
        disk_group = Adw.PreferencesGroup(title="Storage")

        self.disk_label = Gtk.Label(label="0%", css_classes=["gauge-value"],
                                    valign=Gtk.Align.CENTER, width_chars=5)
        self.disk_bar = Gtk.LevelBar(min_value=0, max_value=100, hexpand=True,
                                      valign=Gtk.Align.CENTER)
        self.disk_detail = Gtk.Label(label="", css_classes=["dim-label"],
                                     valign=Gtk.Align.CENTER, width_chars=14)
        disk_row = Adw.ActionRow(title="Disk Usage (/)")
        disk_row.add_suffix(self.disk_bar)
        disk_row.add_suffix(self.disk_detail)
        disk_row.add_suffix(self.disk_label)
        disk_group.add(disk_row)

        self.page.add(disk_group)

        # --- Network group ------------------------------------------------
        net_group = Adw.PreferencesGroup(title="Network")

        self.dl_label = Gtk.Label(label="↓ 0 KB/s", css_classes=["accent-label"],
                                   valign=Gtk.Align.CENTER, width_chars=14)
        self.ul_label = Gtk.Label(label="↑ 0 KB/s", css_classes=["dim-label"],
                                   valign=Gtk.Align.CENTER, width_chars=14)
        net_row = Adw.ActionRow(title="Speed")
        net_row.add_suffix(self.dl_label)
        net_row.add_suffix(self.ul_label)
        net_group.add(net_row)

        self.page.add(net_group)

        # --- Uptime group -------------------------------------------------
        misc_group = Adw.PreferencesGroup(title="System")

        self.uptime_label = Gtk.Label(label="—", css_classes=["dim-label"],
                                       valign=Gtk.Align.CENTER)
        uptime_row = Adw.ActionRow(title="Uptime")
        uptime_row.add_suffix(self.uptime_label)
        misc_group.add(uptime_row)

        self.page.add(misc_group)

        # --- Start timer --------------------------------------------------
        self._update()  # initial reading
        GLib.timeout_add(2000, self._update)

    def _update(self):
        """Refresh all gauges."""
        # CPU
        cpu = _read_cpu_percent()
        self.cpu_bar.set_value(cpu)
        self.cpu_label.set_label(f"{cpu:.0f}%")
        self.cpu_label.set_css_classes([_gauge_css(cpu)])

        self.load_label.set_label(_read_load())
        self.temp_label.set_label(_read_temp())

        # Memory
        used_g, total_g, mem_pct = _read_mem()
        self.mem_bar.set_value(mem_pct)
        self.mem_label.set_label(f"{mem_pct:.0f}%")
        self.mem_label.set_css_classes([_gauge_css(mem_pct)])
        self.mem_detail.set_label(f"{used_g:.1f}/{total_g:.1f} GiB")

        s_used, s_total, s_pct = _read_swap()
        if s_total > 0:
            self.swap_label.set_label(f"{s_used:.1f}/{s_total:.1f} GiB ({s_pct:.0f}%)")
        else:
            self.swap_label.set_label("None")

        # Disk
        d_used, d_total, d_pct = _read_disk()
        self.disk_bar.set_value(d_pct)
        self.disk_label.set_label(f"{d_pct:.0f}%")
        self.disk_label.set_css_classes([_gauge_css(d_pct)])
        self.disk_detail.set_label(f"{d_used:.0f}/{d_total:.0f} GiB")

        # Network
        dl, ul = _read_net_speed()
        if dl >= 1024:
            self.dl_label.set_label(f"↓ {dl/1024:.1f} MB/s")
        else:
            self.dl_label.set_label(f"↓ {dl:.0f} KB/s")
        if ul >= 1024:
            self.ul_label.set_label(f"↑ {ul/1024:.1f} MB/s")
        else:
            self.ul_label.set_label(f"↑ {ul:.0f} KB/s")

        # Uptime
        self.uptime_label.set_label(_read_uptime())

        return True  # keep timer alive


def build_monitor_page(win) -> Adw.PreferencesPage:
    """Build and return the Monitor preferences page."""
    section = MonitorSection(win)
    return section.page
