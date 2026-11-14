#!/usr/bin/env bash
# Arquivo: restaurar.sh
# Projeto: GAMMA Debian (tema Contador)
# Versão: 1.0.0
# Data e hora: 14/11/2026 19:40 (America/Sao_Paulo)
# Autoria: lstavares84, com Claude Opus 5.5 (Anthropic). Criação original.
#
# Volta às configurações que existiam antes do GAMMA ser aplicado.
# Uso:
#   restaurar.sh                 usa o backup mais recente
#   restaurar.sh DIR_BACKUP      usa um backup específico
#   restaurar.sh --remover       restaura e apaga os arquivos instalados
set -euo pipefail

ESTADO="$HOME/.local/share/gamma-theme"
REMOVER=0
DIR=""

for a in "$@"; do
  case "$a" in
    --remover) REMOVER=1 ;;
    -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
    *) DIR="$a" ;;
  esac
done

if [[ -z "$DIR" ]]; then
  [[ -f "$ESTADO/ultimo-backup" ]] || { echo "nenhum backup encontrado em $ESTADO" >&2; exit 1; }
  DIR="$(cat "$ESTADO/ultimo-backup")"
fi

SCRIPT="$ESTADO/gamma_config.py"
[[ -f "$SCRIPT" ]] || SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/ferramentas/gamma_config.py"

python3 "$SCRIPT" restaurar "$DIR"
pgrep -u "$USER" -x xfdesktop >/dev/null && xfdesktop --reload >/dev/null 2>&1 || true

if [[ $REMOVER -eq 1 ]]; then
  rm -rf "$HOME/.themes/GAMMA" "$HOME/.icons/GAMMA" "$HOME/.icons/GAMMA-cursor" \
         "$HOME/.local/share/fonts/gamma" "$HOME/.local/share/backgrounds/gamma" \
         "$HOME/.local/share/xfce4/terminal/colorschemes/gamma.theme" \
         "$HOME/.local/share/gtksourceview-4/styles/gamma.xml"
  fc-cache -f "$HOME/.local/share/fonts" >/dev/null 2>&1 || true
  echo "arquivos do GAMMA removidos (os backups continuam em $ESTADO/backups)"
fi
