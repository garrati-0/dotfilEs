#!/bin/bash
LC_ALL=C

# Prendi lo stato e rimuovi eventuali spazi
STATE=$(nmcli -t -f WIFI general | tr -d ' ')

if [ "$STATE" = "enabled" ]; then
    # Torniamo al tuo metodo originale: è il più preciso per l'SSID attivo
    ACTIVE_SSID=$(nmcli -t -c no -f NAME,TYPE connection show --active | grep 802-11-wireless | cut -d: -f1 | head -n 1)
    
    if [ -z "$ACTIVE_SSID" ]; then
        ACTIVE_SSID="Disconnesso"
        ICON="󰤯 "
    else
        ICON="󰤨 "
    fi

    # 1. Ottieni tutte le connessioni salvate
    SAVED_NETS=$(nmcli -g NAME connection show)
    # 2. Ottieni tutti gli SSID nelle vicinanze (escludendo righe vuote o artefatti)
    NEARBY_NETS=$(nmcli -t -f SSID dev wifi | grep -v '^$' | grep -v '^--$' | sort -u)

    NETWORKS_JSON="["
    FIRST=true

    # Cicla le reti vicine e vedi se sono tra quelle salvate
    while IFS= read -r SSID; do
        if echo "$SAVED_NETS" | grep -Fqx "$SSID"; then
            if [ "$FIRST" = true ]; then 
                FIRST=false 
            else 
                NETWORKS_JSON="${NETWORKS_JSON}," 
            fi
            
            # Segna la rete come connessa (true) o disconnessa (false)
            if [ "$SSID" = "$ACTIVE_SSID" ]; then
                NETWORKS_JSON="${NETWORKS_JSON}{\"ssid\": \"$SSID\", \"connected\": true}"
            else
                NETWORKS_JSON="${NETWORKS_JSON}{\"ssid\": \"$SSID\", \"connected\": false}"
            fi
        fi
    done <<< "$NEARBY_NETS"
    
    NETWORKS_JSON="${NETWORKS_JSON}]"

    # Stampa il JSON completo
    echo "{\"status\": \"enabled\", \"ssid\": \"$ACTIVE_SSID\", \"icon\": \"$ICON\", \"networks\": $NETWORKS_JSON}"
else
    # Se il wifi è spento, invia un array di reti vuoto
    echo '{"status": "disabled", "ssid": "Wi-Fi Spento", "icon": "󰤭 ", "networks": []}'
fi
