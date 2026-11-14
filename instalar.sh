#!/usr/bin/env bash
# Arquivo: instalar.sh
# Projeto: GAMMA Debian (tema Contador)
# Versão: 1.0.0
# Data e hora: 14/11/2026 19:40 (America/Sao_Paulo)
# Autoria: lstavares84, com Claude Opus 5.5 (Anthropic). Criação original.
#
# Instala o tema GAMMA para o usuário atual, sem sudo, e aplica no XFCE.
# Antes de aplicar, guarda as configurações atuais em
# ~/.local/share/gamma-theme/backups/AAAAMMDD-HHMMSS. Para voltar: ./restaurar.sh
#
# Opções:
#   --sem-aplicar     só copia os arquivos, não muda as configurações
#   --sem-wallpaper   não mexe nos papéis de parede
#   --intervalo MIN   intervalo de troca dos papéis de parede (padrão 30)
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DADOS="$HOME/.local/share"
ESTADO="$DADOS/gamma-theme"
APLICAR=1
ARGS_CFG=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --sem-aplicar) APLICAR=0 ;;
    --sem-wallpaper) ARGS_CFG+=("--sem-wallpaper") ;;
    --intervalo) ARGS_CFG+=("--intervalo" "$2"); shift ;;
    -h|--help) sed -n '2,17p' "$0"; exit 0 ;;
    *) echo "opção desconhecida: $1" >&2; exit 2 ;;
  esac
  shift
done

msg() { printf '\033[38;2;120;255;90m▸\033[0m %s\n' "$*"; }
aviso() { printf '\033[38;2;255;190;0m!\033[0m %s\n' "$*"; }

if [[ $EUID -eq 0 ]]; then
  echo "Rode como seu usuário, sem sudo." >&2
  exit 1
fi

for cmd in python3 xfconf-query fc-cache; do
  command -v "$cmd" >/dev/null || { echo "falta o comando: $cmd" >&2; exit 1; }
done

msg "Copiando tema GTK, xfwm4 e notificações para ~/.themes/GAMMA"
mkdir -p "$HOME/.themes"
rm -rf "$HOME/.themes/GAMMA"
cp -a "$RAIZ/tema/GAMMA" "$HOME/.themes/GAMMA"

msg "Copiando cursor para ~/.icons/GAMMA-cursor"
mkdir -p "$HOME/.icons"
rm -rf "$HOME/.icons/GAMMA-cursor"
cp -a "$RAIZ/cursor/GAMMA-cursor" "$HOME/.icons/GAMMA-cursor"

if [[ -d /usr/share/icons/Papirus ]]; then
  msg "Gerando ícones GAMMA a partir do Papirus instalado"
  rm -rf "$HOME/.icons/GAMMA"
  python3 "$RAIZ/icones/gerar_icones.py" "$HOME/.icons/GAMMA"
  command -v gtk-update-icon-cache >/dev/null && gtk-update-icon-cache -q -f "$HOME/.icons/GAMMA" 2>/dev/null || true
else
  aviso "Papirus não encontrado; os ícones atuais serão mantidos (sudo apt install papirus-icon-theme)"
fi

msg "Instalando fontes Roboto e JetBrains Mono em ~/.local/share/fonts/gamma"
mkdir -p "$DADOS/fonts/gamma"
cp -a "$RAIZ"/fontes/*.ttf "$RAIZ"/fontes/OFL-*.txt "$DADOS/fonts/gamma/"
fc-cache -f "$DADOS/fonts" >/dev/null

msg "Instalando esquema do terminal e do editor"
mkdir -p "$DADOS/xfce4/terminal/colorschemes" "$DADOS/gtksourceview-4/styles"
cp "$RAIZ/terminal/gamma.theme" "$DADOS/xfce4/terminal/colorschemes/gamma.theme"
cp "$RAIZ/editor/gamma.xml" "$DADOS/gtksourceview-4/styles/gamma.xml"

msg "Copiando papéis de parede para ~/.local/share/backgrounds/gamma"
mkdir -p "$DADOS/backgrounds/gamma"
rm -rf "$DADOS/backgrounds/gamma/3440x1440" "$DADOS/backgrounds/gamma/2560x1080"
cp -a "$RAIZ/wallpapers/3440x1440" "$RAIZ/wallpapers/2560x1080" "$DADOS/backgrounds/gamma/"

mkdir -p "$ESTADO/backups"
cp "$RAIZ/ferramentas/gamma_config.py" "$RAIZ/restaurar.sh" "$ESTADO/"
chmod +x "$ESTADO/restaurar.sh"

if [[ $APLICAR -eq 1 ]]; then
  DIR_BACKUP="$ESTADO/backups/$(date +%Y%m%d-%H%M%S)"
  msg "Guardando configurações atuais e aplicando o GAMMA"
  mkdir -p "$DIR_BACKUP"
  # cópia extra de todos os canais do xfconf, só por segurança
  cp -a "$HOME/.config/xfce4/xfconf/xfce-perchannel-xml" "$DIR_BACKUP/xfconf-completo" 2>/dev/null || true
  python3 "$ESTADO/gamma_config.py" aplicar "$DIR_BACKUP" "${ARGS_CFG[@]}" || aviso "algumas configurações falharam (veja acima)"
  echo "$DIR_BACKUP" > "$ESTADO/ultimo-backup"
  if pgrep -u "$USER" -x xfdesktop >/dev/null; then
    xfdesktop --reload >/dev/null 2>&1 || true
  fi
  msg "Pronto. Para voltar ao tema anterior: $ESTADO/restaurar.sh"
else
  msg "Arquivos copiados. Nada foi aplicado (--sem-aplicar)."
fi
