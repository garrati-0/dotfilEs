#!/bin/bash
LC_ALL=C

# Controlla se il Bluetooth è acceso
POWER_STATE=$(bluetoothctl show | grep "Powered: yes")

if [ -z "$POWER_STATE" ]; then
    echo '{"status": "disabled", "name": "Bluetooth Spento", "icon": "󰂲 ", "devices": []}'
    exit 0
fi

# Ottieni i dispositivi attualmente connessi
CONNECTED_DEVICES=$(bluetoothctl devices Connected)
# Prende il nome del primo dispositivo connesso (rimuovendo "Device XX:XX:XX...")
ACTIVE_NAME=$(echo "$CONNECTED_DEVICES" | head -n 1 | cut -d ' ' -f 3-)

if [ -z "$ACTIVE_NAME" ]; then
    ACTIVE_NAME="Disconnesso"
    ICON="󰂯 "
else
    ICON="󰂱 "
fi

# Ottieni tutti i dispositivi accoppiati (salvati)
PAIRED_DEVICES=$(bluetoothctl devices Paired)
DEVICES_JSON="["
FIRST=true

# Cicla i dispositivi salvati per costruire il JSON
while IFS= read -r line; do
    if [ -z "$line" ]; then continue; fi
    
    # Estrai il MAC address e il Nome
    MAC=$(echo "$line" | awk '{print $2}')
    NAME=$(echo "$line" | cut -d ' ' -f 3-)
    
    # Verifica se questo specifico MAC è tra quelli connessi
    if echo "$CONNECTED_DEVICES" | grep -q "$MAC"; then
        CONNECTED="true"
    else
        CONNECTED="false"
    fi
    
    if [ "$FIRST" = true ]; then 
        FIRST=false 
    else 
        DEVICES_JSON="${DEVICES_JSON}," 
    fi
    
    DEVICES_JSON="${DEVICES_JSON}{\"name\": \"$NAME\", \"mac\": \"$MAC\", \"connected\": $CONNECTED}"
done <<< "$PAIRED_DEVICES"

DEVICES_JSON="${DEVICES_JSON}]"

# Stampa il risultato finale
echo "{\"status\": \"enabled\", \"name\": \"$ACTIVE_NAME\", \"icon\": \"$ICON\", \"devices\": $DEVICES_JSON}"
