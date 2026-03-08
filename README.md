# 👾 My Hyprland Dotfiles

Benvenuti nel mio repository di dotfiles! Questo setup è basato su **Hyprland** e punta a unire un'estetica accattivante (con un tocco retro-gaming) a un'alta produttività ed efficienza.

Ho dedicato molto tempo alla creazione di widget personalizzati per avere tutto a portata di mano senza dover aprire il terminale per le operazioni di base.

## 📸 Showcase

### Desktop & Workflow

![Desktop](assets/scatto.png)
![Lockscreen](assets/scatto_lockscreen.png)
![Workflow Setup](assets/2026-03-06_213418.png)

### Control Center & Widget personalizzati

Il cuore del setup. Un control center completo e menu rapidi per gestire il sistema.

![Control Center](assets/2026-03-06_213426.png)
![Menu Rapidi](assets/2026-03-06_213556.png)

### Gestione Rete, Bluetooth e Audio

![Gestione Rete](assets/2026-03-06_213528.png)
![Gestione Bluetooth](assets/2026-03-06_213535.png)
![Gestione Audio](assets/2026-03-06_213445.png)

### App Impostazioni Custom (Python)

Un'interfaccia grafica creata da me per gestire le impostazioni principali.

![Impostazioni Rete](assets/2026-03-06_214116.png)
![Impostazioni Bluetooth](assets/2026-03-06_214122.png)
![Impostazioni Aspetto](assets/2026-03-06_214127.png)

### Power Menu

![Power Menu](assets/2026-03-06_213434.png)

---

## 🛠️ Tecnologie e Programmi Utilizzati

* **Window Manager:** [Hyprland](https://www.google.com/search?q=https://hyprland.org/)
* **Terminale:** Kitty
* **Barra di stato:** Waybar
* **Application Launcher:** Rofi
* **Sistema di Widget:** Eww (Elkowars Wacky Widgets)

---

## ✨ Funzionalità Principali

### 🎨 Widget Custom con Eww

Ho sfruttato Eww per creare un ecosistema di widget fluttuanti completamente integrati con lo stile del sistema:

* **Control Center:** Un pannello unificato che include toggle rapidi (Wi-Fi, Bluetooth, Modalità Notte, ecc.), un media player, una to-do list e un piccolo monitor di sistema (CPU, RAM, ecc.).
* **Wi-Fi Manager:** Mostra le reti visibili e quelle già associate, permettendo la connessione rapida con un clic.
* **Bluetooth Manager:** Permette di visualizzare, connettere e disconnettere i dispositivi associati (es. cuffie).
* **Controllo Volume:** Slider per il volume e selettore per cambiare rapidamente la periferica di uscita audio.
* **Menu Rapido (Dropdown):** Un menu a tendina per accedere rapidamente a Impostazioni, File Manager, Terminale, Launcher e opzioni di spegnimento.

### ⚙️ App di Impostazioni Personalizzata (Python)

Invece di affidarmi a tool di terze parti, sto sviluppando una mia applicazione scritta in **Python** per gestire il sistema.
Attualmente permette di:

* Gestire le connessioni Wi-Fi e l'Hotspot.
* Gestire i dispositivi Bluetooth.
* Cambiare lo sfondo.
* Gestire altre impostazioni di base.

*Nota: Questo tool è ancora in via di sviluppo e ho intenzione di ampliarlo notevolmente in futuro!*

---

## 🚀 To-Do / Sviluppi Futuri

Il ricing non finisce mai! Ecco cosa ho in programma di implementare prossimamente:

* [ ] **Integrazione Calendario:** Aggiungere un calendario collegato a Google Calendar all'interno dei widget.
* [ ] **Clipboard History:** Creare un widget o un menu in Rofi per gestire la cronologia degli appunti.
* [ ] **Espansione dell'App Python:** Aggiungere nuove schede e funzionalità alla mia app di impostazioni (es. gestione temi, gestione display, ecc.).

Certo! Aggiungiamo una sezione dedicata all'installazione che sia chiara e dritta al punto. Non c'è bisogno di scrivere un manuale, basta indicare i mattoni fondamentali per far funzionare i tuoi script e widget (come NetworkManager e BlueZ) e mostrare i comandi base per applicare i file.

Ecco come puoi integrare la sezione nel tuo `README.md` (puoi inserirla subito dopo la sezione "Tecnologie e Programmi Utilizzati" o alla fine, prima del "To-Do"):

---

## 📦 Installazione

Questa non è una guida passo-passo su come installare il sistema operativo da zero, ma una rapida panoramica delle dipendenze necessarie per far funzionare correttamente questi dotfiles (in particolare i widget creati con Eww e l'app Python).

### 1. Dipendenze Essenziali

Assicurati di avere i seguenti pacchetti installati tramite il gestore della tua distribuzione (es. `pacman`, `yay`, `apt`, ecc.):

* **Core & UI:** `hyprland`, `kitty`, `waybar`, `rofi-wayland`, `eww` (assicurati che sia la versione compilata per Wayland)
* **Gestione Rete & Bluetooth:** `networkmanager` (utilizzato dai widget Wi-Fi), `bluez`, `bluez-utils` (per il controllo del Bluetooth tramite i pannelli)
* **Audio:** `pipewire`, `wireplumber` e strumenti a riga di comando come `pamixer` o `wpctl` (fondamentali per far comunicare gli slider di Eww con l'audio di sistema)
* **App Impostazioni Custom:** `python3` e i moduli necessari per avviare la GUI (es. librerie GTK o PyQt, a seconda di come hai compilato l'app).
* **Font:** Per far sì che le icone nei pannelli e in Waybar si vedano correttamente, devi installare un [Nerd Font](https://www.nerdfonts.com/) (es. *JetBrainsMono Nerd Font*).

### 2. Applicare i Dotfiles

**⚠️ Attenzione:** Prima di procedere, ti consiglio caldamente di fare un backup delle tue attuali cartelle di configurazione!

Apri il terminale ed esegui:

```bash
# 1. Clona questo repository
git clone https://github.com/garrati-0/dotfilEs.git

# 2. Entra nella cartella clonata
cd TUO-REPO

# 3. Esegui il backup delle tue configurazioni attuali (opzionale ma consigliato)
mv ~/.config/hypr ~/.config/hypr.backup
mv ~/.config/eww ~/.config/eww.backup
# (ripeti per rofi, waybar, kitty, ecc.)

# 4. Copia le nuove configurazioni nella tua home
cp -r .config/* ~/.config/

```

### 3. Ultimi tocchi

Una volta copiati i file, assicurati che i tuoi script e l'app scritta in Python abbiano i permessi di esecuzione. Puoi farlo con un comando simile a questo:

```bash
chmod +x ~/.config/percorso/del/tuo/script.py

```

Infine, riavvia Hyprland (uscendo e rientrando dalla sessione) per applicare tutte le modifiche.

