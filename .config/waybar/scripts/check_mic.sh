#!/bin/bash

# Controlla se c'è un flusso audio in entrata che NON sia in pausa ("Corked: no")
if LC_ALL=C pactl list source-outputs | grep -q "Corked: no"; then
    
    # Estrai i nomi delle applicazioni (es. "Google Chrome input")
    APPS=$(LC_ALL=C pactl list source-outputs | grep 'application.name = ' | cut -d'"' -f2 | paste -sd ", " -)
    
    # Se per qualche motivo non trova il nome, usa un testo di sicurezza
    if [ -z "$APPS" ]; then
        APPS="App sconosciuta"
    fi
    
    # Stampa il JSON con il nome dell'app nel tooltip!
    echo "{\"alt\": \"active\", \"class\": \"active\", \"tooltip\": \"🎤 In uso da: $APPS\"}"
else
    echo "{\"alt\": \"inactive\", \"class\": \"inactive\", \"tooltip\": \"\"}"
fi
