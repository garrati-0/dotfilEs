#!/bin/bash
TODO_FILE="$HOME/.config/eww/todo.txt"

# Create file if it doesn't exist
[ -f "$TODO_FILE" ] || touch "$TODO_FILE"

generate_literal() {
  local literal="(box :class \"todo-list\" :orientation \"v\" :space-evenly false :spacing 6 "
  local count=0

  while IFS= read -r line; do
    if [ -n "$line" ]; then
      literal+="(box :class \"todo-item\" :orientation \"h\" :space-evenly false :spacing 8 :valign \"center\" "
      literal+="(button :class \"todo-del\" :onclick \"scripts/todo.sh del $count &\" (label :text \"󰅖\")) "
      # Escape quotes in the task text
      safe_line=${line//\"/\\\"}
      literal+="(label :class \"todo-text\" :halign \"start\" :wrap true :text \"$safe_line\")) "
      ((count++))
    fi
  done < "$TODO_FILE"

  if [ "$count" -eq 0 ]; then
    literal+="(label :class \"todo-empty\" :halign \"center\" :text \"Nessun task in sospeso\")"
  fi

  literal+=")"
  echo "$literal"
}

case "$1" in
  add)
    if [ -n "$2" ]; then
      echo "$2" >> "$TODO_FILE"
      generate_literal
    fi
    ;;
  del)
    if [ -n "$2" ]; then
      # sed uses 1-based indexing
      sed -i "$(( $2 + 1 ))d" "$TODO_FILE"
      generate_literal
    fi
    ;;
  get)
    generate_literal
    ;;
esac
