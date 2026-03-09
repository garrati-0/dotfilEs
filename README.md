# 👾 My Hyprland Dotfiles

[Versione Italiana](README_it.md)

---

Welcome to my dotfiles repository! This setup is based on **Hyprland** and aims to combine an eye-catching aesthetic (with a retro-gaming touch) with high productivity and efficiency.

I spent a lot of time creating custom widgets to have everything at my fingertips without having to open the terminal for basic operations.

### 📸 Showcase

#### Desktop & Workflow
![Desktop](assets/scatto.png)
![Lockscreen](assets/scatto_lockscreen.png)
![Workflow Setup](assets/2026-03-06_213418.png)

#### Control Center & Custom Widgets
The heart of the setup. A complete control center and quick menus to manage the system.
**Version 1 (Classic):**
![Control Center v1](assets/2026-03-06_213426.png)

**Version 2 (Android Style):**
![Control Center v2](assets/2026-03-09_191418.png)

![Quick Menus](assets/2026-03-06_213556.png)

#### Network, Bluetooth, and Audio Management
![Network Management](assets/2026-03-06_213528.png)
![Bluetooth Management](assets/2026-03-06_213535.png)
![Audio Management](assets/2026-03-06_213445.png)

#### Custom Settings App (Python)
A graphical interface I built from scratch to manage core settings.
![Network Settings](assets/2026-03-06_214116.png)
![Bluetooth Settings](assets/2026-03-06_214122.png)
![Appearance Settings](assets/2026-03-06_214127.png)

#### Power Menu
![Power Menu](assets/2026-03-06_213434.png)

---

## 🛠️ Technologies and Tools Used

* **Window Manager:** [Hyprland](https://hyprland.org/)
* **Terminal:** Kitty
* **Status Bar:** Waybar
* **Application Launcher:** Rofi
* **Widget System:** Eww (Elkowars Wacky Widgets)

---

## ✨ Main Features

### 🎨 Custom Widgets with Eww
I used Eww to create an ecosystem of floating widgets fully integrated with the system's style:
* **Control Center:** A unified panel featuring quick toggles (Wi-Fi, Bluetooth, Night Mode, etc.), a media player, a to-do list, and a mini system monitor (CPU, RAM, etc.).
* **Wi-Fi Manager:** Displays available and known networks, allowing a quick one-click connection.
* **Bluetooth Manager:** View, connect, and disconnect paired devices (e.g., headphones).
* **Volume Control:** Sliders for volume and a quick selector to change the audio output device.
* **Quick Menu (Dropdown):** A dropdown menu to quickly access Settings, File Manager, Terminal, Launcher, and Power options.

### ⚙️ Custom Settings App (Python)
Instead of relying on third-party tools, I'm developing my own application written in **Python** to manage the system. Currently, it allows you to:
* Manage Wi-Fi connections and Hotspots.
* Manage Bluetooth devices.
* Change the wallpaper.
* Manage other basic settings.

> *Note: This tool is still in development, and I plan to expand it significantly in the future!*

---

## 📦 Installation

This is not a step-by-step guide on how to install an OS from scratch, but a quick overview of the dependencies required to make these dotfiles work (especially the Eww widgets and the Python app).

### 1. Essential Dependencies
Make sure you have the following packages installed via your distribution's package manager (e.g., `pacman`, `yay`, `apt`, etc.):

* **Core & UI:** `hyprland`, `kitty`, `waybar`, `rofi-wayland`, `eww` (make sure it's the Wayland build)
* **Network & Bluetooth:** `networkmanager` (used by Wi-Fi widgets), `bluez`, `bluez-utils` (for Bluetooth control via panels)
* **Audio:** `pipewire`, `wireplumber`, and CLI tools like `pamixer` or `wpctl` (crucial for linking Eww sliders with system audio)
* **Custom Settings App:** `python3` and the necessary modules to run the GUI (e.g., GTK or PyQt libraries, depending on how you compiled the app).
* **Fonts:** To ensure icons render correctly in the panels and Waybar, you must install a [Nerd Font](https://www.nerdfonts.com/) (e.g., *JetBrainsMono Nerd Font*).

### 2. Applying the Dotfiles

**⚠️ Warning:** Before proceeding, I highly recommend backing up your current configuration folders!

Open your terminal and run:

```bash
# 1. Clone this repository
git clone https://github.com/garrati-0/dotfilEs.git

# 2. Enter the cloned folder
cd dotfilEs

# 3. Backup your current configurations (optional but recommended)
mv ~/.config/hypr ~/.config/hypr.backup
mv ~/.config/eww ~/.config/eww.backup
# (repeat for rofi, waybar, kitty, etc.)

# 4. Copy the new configurations to your home
cp -r .config/* ~/.config/
```

### 3. Check Paths & Final Touches (CRITICAL)
After copying the files, you must check and update the hardcoded paths.

**Images and Wallpapers:** Check `hyprland.conf`, your Eww `.yuck` files, and your Waybar CSS to ensure that paths pointing to profile pictures, assets, or wallpapers match your system's username (e.g., change `/home/garrati-0/...` to `/home/YOUR_USERNAME/...`).

**Scripts:** Ensure your scripts and the Python app have the correct execution permissions:

```bash
chmod +x ~/.config/path/to/your/script.py
```
Finally, restart Hyprland (log out and log back in) to apply all the changes.

---

## 🚀 To-Do / Future Developments
Ricing never ends! Here is what I plan to implement next:

* [ ] **App Dock:** Create or integrate a dock for quick access to favorite applications.
* [ ] **GNOME-style Multitasking:** Implement a dynamic and visual workspace overview similar to GNOME's activities overview.
* [ ] **Calendar Integration:** Add a calendar linked to Google Calendar inside the widgets.
* [ ] **Clipboard History:** Create a widget or a Rofi menu to manage clipboard history.
* [ ] **Expand Python App:** Add new tabs and features to my settings app (e.g., theme management, display management, etc.).
