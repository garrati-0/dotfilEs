#!/bin/bash
# Script per Waybar: estrae la copertina MPRIS e la salva in /tmp/waybar-cover.png
# Eseguire questo script in background (es. all'avvio del sistema)

TEMPORARY_COVER="/tmp/waybar-cover.png"

while true; do
    # Estrai l'URL della copertina
    CURRENT_COVER_URL=$(playerctl metadata mpris:artUrl 2>/dev/null | sed 's|^file://||')
    
    # Se non c'è copertina o l'URL è vuoto, rimuovi l'immagine temporanea
    if [ -z "$CURRENT_COVER_URL" ]; then
        if [ -L "$TEMPORARY_COVER" ]; then
            rm "$TEMPORARY_COVER"
        fi
        sleep 2
        continue
    fi

    # Se l'URL è un file locale, crea un link simbolico
    if [[ "$CURRENT_COVER_URL" == /* ]]; then
        if [ "$CURRENT_COVER_URL" != "$(readlink "$TEMPORARY_COVER")" ]; then
            ln -sf "$CURRENT_COVER_URL" "$TEMPORARY_COVER"
        fi
    else
        # Se l'URL è un link internet, usa wget per scaricarlo (richiede wget)
        if ! command -v wget &> /dev/null; then
            echo "Errore: wget non installato. Installa wget per scaricare copertine online."
        else
            if [ ! -f "$TEMPORARY_COVER" ] || [ "$(readlink "$TEMPORARY_COVER")" != "" ]; then
                 rm -f "$TEMPORARY_COVER" # Rimuovi se è un link simbolico
            fi
            wget -qO "$TEMPORARY_COVER" "$CURRENT_COVER_URL"
        fi
    fi
    
    # Pausa per evitare un utilizzo eccessivo della CPU
    sleep 2
done
