"""Appearance — Wallpaper picker using swww and desktop environment reloaders."""

import os
import subprocess

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GdkPixbuf, Gdk, GLib

PICTURES_DIR = os.path.expanduser("~/pictures")
SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
THUMB_SIZE = 200


def _is_image(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in SUPPORTED_EXTS


def _load_thumbnail(path: str, size: int = THUMB_SIZE) -> Gdk.Texture | None:
    """Load an image file as a square Gdk.Texture thumbnail."""
    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            path, size, size, True
        )
        return Gdk.Texture.new_for_pixbuf(pixbuf)
    except Exception:
        return None


class AppearanceSection:
    """Manages the Appearance preferences page."""

    def __init__(self, win):
        self.win = win
        self.page = Adw.PreferencesPage()
        self._selected_path: str | None = None

        # --- Wallpaper group ------------------------------------------------
        wall_group = Adw.PreferencesGroup(
            title="Background",
            description="Select an image from ~/pictures to set as background",
        )

        # FlowBox inside a ScrolledWindow for the wallpaper grid
        self.flowbox = Gtk.FlowBox(
            homogeneous=True,
            min_children_per_line=2,
            max_children_per_line=5,
            column_spacing=10,
            row_spacing=10,
            selection_mode=Gtk.SelectionMode.SINGLE,
            valign=Gtk.Align.START,
            margin_top=8,
            margin_bottom=8,
            margin_start=8,
            margin_end=8,
        )
        self.flowbox.connect("child-activated", self._on_wallpaper_selected)

        scroll = Gtk.ScrolledWindow(
            hscrollbar_policy=Gtk.PolicyType.NEVER,
            vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
            min_content_height=380,
            vexpand=True,
            child=self.flowbox,
        )

        wall_group.add(scroll)
        self.page.add(wall_group)

        # --- Ambiente Desktop group -----------------------------------------
        desktop_group = Adw.PreferencesGroup(
            title="Desktop Environment",
            description="Manage graphical interface components",
        )

        # Ricarica Waybar
        waybar_row = Adw.ActionRow(
            title="Reload Waybar",
            subtitle="Reload the status bar configuration"
        )
        waybar_btn = Gtk.Button(
            icon_name="view-refresh-symbolic",
            valign=Gtk.Align.CENTER,
            css_classes=["circular"]
        )
        waybar_btn.connect("clicked", self._on_reload_waybar)
        waybar_row.add_suffix(waybar_btn)
        waybar_row.set_activatable_widget(waybar_btn)
        desktop_group.add(waybar_row)

        # Ricarica Hyprland
        hypr_row = Adw.ActionRow(
            title="Reload Hyprland",
            subtitle="Reload the window manager configuration"
        )
        hypr_btn = Gtk.Button(
            icon_name="view-refresh-symbolic",
            valign=Gtk.Align.CENTER,
            css_classes=["circular"]
        )
        hypr_btn.connect("clicked", self._on_reload_hyprland)
        hypr_row.add_suffix(hypr_btn)
        hypr_row.set_activatable_widget(hypr_btn)
        desktop_group.add(hypr_row)

        self.page.add(desktop_group)

        # Populate grid
        self._populate_wallpapers()

    def _populate_wallpapers(self):
        """Scan ~/pictures and add thumbnails to the flow box."""
        if not os.path.isdir(PICTURES_DIR):
            placeholder = Gtk.Label(
                label="Folder ~/pictures does not exist.\nCreate it and add your images.",
                justify=Gtk.Justification.CENTER,
                css_classes=["dim-label"],
                margin_top=40,
                margin_bottom=40,
            )
            self.flowbox.append(placeholder)
            return

        images = sorted(
            f
            for f in os.listdir(PICTURES_DIR)
            if _is_image(f)
        )

        if not images:
            placeholder = Gtk.Label(
                label="No images found in ~/pictures",
                css_classes=["dim-label"],
                margin_top=40,
                margin_bottom=40,
            )
            self.flowbox.append(placeholder)
            return

        for fname in images:
            full_path = os.path.join(PICTURES_DIR, fname)
            texture = _load_thumbnail(full_path)
            if texture is None:
                continue

            picture = Gtk.Picture.new_for_paintable(texture)
            picture.set_content_fit(Gtk.ContentFit.COVER)
            picture.set_size_request(THUMB_SIZE, int(THUMB_SIZE * 0.65))

            # Frame with rounded corners
            frame = Gtk.Frame(
                child=picture,
                css_classes=["card"],
            )
            frame.set_overflow(Gtk.Overflow.HIDDEN)

            overlay = Gtk.Overlay(child=frame)

            # Store path on the overlay for retrieval
            overlay._wallpaper_path = full_path

            self.flowbox.append(overlay)

    def _on_wallpaper_selected(self, flowbox, child):
        """Apply the selected wallpaper using swww img."""
        widget = child.get_child()
        if not hasattr(widget, "_wallpaper_path"):
            return

        path = widget._wallpaper_path
        self._selected_path = path

        try:
            subprocess.Popen(
                ["hyprctl", "hyprpaper", "wallpaper", f",{path}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            self._show_error(
                "hyprctl not found. Ensure Hyprland is running."
            )

    def _on_reload_waybar(self, button):
        """Reload waybar config."""
        subprocess.Popen(
            ["sh", "-c", "killall -SIGUSR2 waybar || (killall waybar && waybar &)"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def _on_reload_hyprland(self, button):
        """Reload hyprland config."""
        try:
            subprocess.Popen(
                ["hyprctl", "reload"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            self._show_error("Could not reload Hyprland.")

    def _show_error(self, msg: str):
        dialog = Adw.AlertDialog(heading="Background Error", body=msg)
        dialog.add_response("ok", "OK")
        dialog.present(self.win)


def build_appearance_page(win) -> Adw.PreferencesPage:
    """Build and return the Appearance preferences page."""
    section = AppearanceSection(win)
    return section.page
