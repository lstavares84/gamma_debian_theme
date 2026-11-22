#!/usr/bin/env bash
# Arquivo: instalar-sistema.sh
# Projeto: GAMMA Debian (tema Contador)
# Versão: 1.1.0
# Data e hora: 22/11/2026 08:40 (America/Sao_Paulo)
# 1.0.1: não encerra em silêncio quando ainda não há backup (pipefail).
# 1.1.0: o greeter GAMMA é gravado com o caminho completo do programa e só é
#        ativado depois de testado com o PATH reduzido da sessão do greeter.
#        Antes, "env lightdm-gtk-greeter" não achava /usr/sbin e o login ficava preto.
# Autoria: lstavares84, com Claude Opus 5.5 (Anthropic). Criação original.
#
# Aplica o GAMMA nas telas que ficam fora da sessão do usuário: menu do GRUB,
# tela de carga do Plymouth (inclusive o pedido da senha do disco) e tela de
# login do LightDM. Precisa de root:  sudo ./instalar-sistema.sh
# Antes de mudar qualquer coisa, guarda os arquivos originais em
# /var/backups/gamma-sistema/AAAAMMDD-HHMMSS e anota o que foi criado. Se já
# houver um backup ativo (instalação anterior), reaproveita ele: os originais
# do Debian nunca são trocados pela versão GAMMA.
#
# Opções:
#   --sem-grub        não mexe no GRUB
#   --sem-plymouth    não mexe no Plymouth
#   --sem-login       não mexe no LightDM
#   --desfazer [DIR]  volta ao estado do backup (padrão: o mais recente)
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_BK=/var/backups/gamma-sistema
FAZ_GRUB=1; FAZ_PLY=1; FAZ_LOGIN=1; DESFAZER=0; DIR_DESFAZER=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --sem-grub) FAZ_GRUB=0 ;;
    --sem-plymouth) FAZ_PLY=0 ;;
    --sem-login) FAZ_LOGIN=0 ;;
    --desfazer) DESFAZER=1; if [[ $# -gt 1 && "$2" != --* ]]; then DIR_DESFAZER="$2"; shift; fi ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "opção desconhecida: $1" >&2; exit 2 ;;
  esac
  shift
done

msg() { printf '\033[38;2;120;255;90m▸\033[0m %s\n' "$*"; }
aviso() { printf '\033[38;2;255;190;0m!\033[0m %s\n' "$*"; }

[[ $EUID -eq 0 ]] || { echo "Precisa de root: sudo $0 $*" >&2; exit 1; }

# ---------------------------------------------------------------- desfazer
if [[ $DESFAZER -eq 1 ]]; then
  DIR="${DIR_DESFAZER:-$(ls -1d "$BASE_BK"/2*/ 2>/dev/null | grep -v desfeito | sort | tail -1 || true)}"
  DIR="${DIR%/}"
  [[ -n "$DIR" && -f "$DIR/criados.txt" ]] || { echo "backup não encontrado em $BASE_BK" >&2; exit 1; }
  msg "Desfazendo a partir de $DIR"
  # apaga o que o GAMMA criou (só caminhos anotados na instalação)
  while IFS= read -r alvo; do
    [[ -n "$alvo" && -e "$alvo" ]] && rm -rf -- "$alvo" && echo "  removido $alvo"
  done < "$DIR/criados.txt"
  # devolve os arquivos originais
  if [[ -d "$DIR/arquivos" ]]; then
    (cd "$DIR/arquivos" && find . -type f -print0) | while IFS= read -r -d '' f; do
      cp -a "$DIR/arquivos/$f" "/${f#./}" && echo "  restaurado /${f#./}"
    done
  fi
  grep -q grub "$DIR/partes.txt" && { msg "Atualizando o GRUB"; update-grub; }
  grep -q plymouth "$DIR/partes.txt" && { msg "Atualizando o initramfs (pode levar um minuto)"; update-initramfs -u -k all; }
  fc-cache -f >/dev/null 2>&1 || true
  mv "$DIR" "$DIR.desfeito"
  msg "Pronto. Reinicie para ver as telas originais."
  exit 0
fi

# ---------------------------------------------------------------- conferências
for f in sistema/grub/GAMMA/theme.txt sistema/plymouth/gamma/gamma.script sistema/lightdm/greeter.css tema/GAMMA/gtk-3.0/gtk.css; do
  [[ -f "$RAIZ/$f" ]] || { echo "falta $f (rode a partir da pasta do projeto)" >&2; exit 1; }
done
[[ $FAZ_GRUB -eq 1 ]] && ! command -v update-grub >/dev/null && { aviso "update-grub não encontrado; pulando o GRUB"; FAZ_GRUB=0; }
[[ $FAZ_PLY -eq 1 ]] && ! command -v plymouth-set-default-theme >/dev/null && { aviso "Plymouth não instalado; pulando (sudo apt install plymouth)"; FAZ_PLY=0; }
GREETER_BIN="$(command -v lightdm-gtk-greeter || true)"
[[ $FAZ_LOGIN -eq 1 && ! -x "$GREETER_BIN" ]] && { aviso "lightdm-gtk-greeter não encontrado; pulando o login"; FAZ_LOGIN=0; }

BK="$(ls -1d "$BASE_BK"/2*/ 2>/dev/null | grep -v desfeito | sort | head -1 || true)"
BK="${BK%/}"
if [[ -z "$BK" ]]; then
  BK="$BASE_BK/$(date +%Y%m%d-%H%M%S)"
  mkdir -p "$BK/arquivos"
  : > "$BK/criados.txt"; : > "$BK/partes.txt"
fi

guarda() {  # guarda o original do Debian uma única vez
  local f="$1"
  if [[ -e "$f" && ! -e "$BK/arquivos$f" ]]; then mkdir -p "$BK/arquivos$(dirname "$f")"; cp -a "$f" "$BK/arquivos$f"; fi
}
cria() {    # anota um caminho do GAMMA (o --desfazer apaga)
  grep -qxF "$1" "$BK/criados.txt" || echo "$1" >> "$BK/criados.txt"
}
parte() { grep -qxF "$1" "$BK/partes.txt" || echo "$1" >> "$BK/partes.txt"; }
msg "Backup em $BK"

# Confere um arquivo de /usr/share/xgreeters como o LightDM vai usar: o programa da
# linha Exec (pulando "env" e variáveis) precisa existir com o PATH reduzido da
# sessão do greeter, e o executável precisa existir de fato.
greeter_ok() {
  local exec_line prog
  exec_line="$(sed -n 's/^Exec=//p' "$1" | head -1)"
  prog="$(printf '%s\n' "$exec_line" | awk '{for(i=1;i<=NF;i++){if($i=="env"||$i~/=/)continue;print $i;exit}}')"
  [[ -n "$prog" ]] || return 1
  env -i PATH=/usr/local/bin:/usr/bin:/bin sh -c 'command -v "$1"' _ "$prog" >/dev/null 2>&1 || return 1
  [[ -x "$(env -i PATH=/usr/local/bin:/usr/bin:/bin sh -c 'command -v "$1"' _ "$prog")" ]]
}

# ---------------------------------------------------------------- GRUB
if [[ $FAZ_GRUB -eq 1 ]]; then
  parte grub
  msg "GRUB: tema em /boot/grub/themes/GAMMA"
  mkdir -p /boot/grub/themes
  cria /boot/grub/themes/GAMMA
  rm -rf /boot/grub/themes/GAMMA
  cp -r "$RAIZ/sistema/grub/GAMMA" /boot/grub/themes/GAMMA
  mkdir -p /etc/default/grub.d
  cria /etc/default/grub.d/gamma.cfg
  cat > /etc/default/grub.d/gamma.cfg <<'EOF'
# GAMMA Debian: tema do GRUB e tela de carga do Plymouth (instalar-sistema.sh)
GRUB_THEME="/boot/grub/themes/GAMMA/theme.txt"
GRUB_GFXMODE="3440x1440,auto"
GRUB_GFXPAYLOAD_LINUX="keep"
case " $GRUB_CMDLINE_LINUX_DEFAULT " in *" splash "*) ;; *) GRUB_CMDLINE_LINUX_DEFAULT="$GRUB_CMDLINE_LINUX_DEFAULT splash" ;; esac
EOF
  update-grub
fi

# ---------------------------------------------------------------- Plymouth
if [[ $FAZ_PLY -eq 1 ]]; then
  parte plymouth
  msg "Plymouth: tema em /usr/share/plymouth/themes/gamma"
  guarda /etc/plymouth/plymouthd.conf
  cria /usr/share/plymouth/themes/gamma
  rm -rf /usr/share/plymouth/themes/gamma
  cp -r "$RAIZ/sistema/plymouth/gamma" /usr/share/plymouth/themes/gamma
  plymouth-set-default-theme gamma
  msg "Atualizando o initramfs (pode levar um minuto)"
  update-initramfs -u -k all
  if [[ $FAZ_GRUB -eq 0 ]] && ! grep -q 'splash' /proc/cmdline; then
    aviso "a linha do kernel não tem 'splash'; sem ela o Plymouth fica em modo texto"
  fi
fi

# ---------------------------------------------------------------- LightDM
if [[ $FAZ_LOGIN -eq 1 ]]; then
  parte login
  msg "Login: tema GTK, cursor, fontes e fundos em /usr/share"
  cria /usr/share/themes/GAMMA-Login
  rm -rf /usr/share/themes/GAMMA-Login
  cp -r "$RAIZ/tema/GAMMA" /usr/share/themes/GAMMA-Login
  sed -i 's/^Name=.*/Name=GAMMA-Login/' /usr/share/themes/GAMMA-Login/index.theme
  { printf '\n'; cat "$RAIZ/sistema/lightdm/greeter.css"; } >> /usr/share/themes/GAMMA-Login/gtk-3.0/gtk.css
  cria /usr/share/icons/GAMMA-cursor
  rm -rf /usr/share/icons/GAMMA-cursor
  cp -r "$RAIZ/cursor/GAMMA-cursor" /usr/share/icons/GAMMA-cursor
  cria /usr/local/share/fonts/gamma
  mkdir -p /usr/local/share/fonts/gamma
  cp "$RAIZ"/fontes/*.ttf "$RAIZ"/fontes/OFL-*.txt /usr/local/share/fonts/gamma/
  fc-cache -f >/dev/null
  cria /usr/share/backgrounds/gamma-login
  mkdir -p /usr/share/backgrounds/gamma-login
  cp "$RAIZ"/sistema/lightdm/fundo-*.png /usr/share/backgrounds/gamma-login/
  chmod -R a+rX /usr/share/themes/GAMMA-Login /usr/share/icons/GAMMA-cursor /usr/local/share/fonts/gamma /usr/share/backgrounds/gamma-login
  guarda /etc/lightdm/lightdm-gtk-greeter.conf
  install -m 644 "$RAIZ/sistema/lightdm/lightdm-gtk-greeter.conf" /etc/lightdm/lightdm-gtk-greeter.conf
  [[ -d /usr/share/icons/Papirus-Dark ]] || sed -i 's/^icon-theme-name=.*/icon-theme-name=Adwaita/' /etc/lightdm/lightdm-gtk-greeter.conf
  # greeter GAMMA: Exec com o caminho completo descoberto agora (a sessão do greeter
  # roda com PATH reduzido, sem /usr/sbin, onde o Debian põe o lightdm-gtk-greeter)
  cria /usr/share/xgreeters/gamma-greeter.desktop
  sed "s#^Exec=.*#Exec=env LANGUAGE=en $GREETER_BIN#" "$RAIZ/sistema/lightdm/gamma-greeter.desktop" > /usr/share/xgreeters/gamma-greeter.desktop
  chmod 644 /usr/share/xgreeters/gamma-greeter.desktop
  [[ -d /etc/lightdm/lightdm.conf.d ]] || cria /etc/lightdm/lightdm.conf.d
  mkdir -p /etc/lightdm/lightdm.conf.d
  cria /etc/lightdm/lightdm.conf.d/50-gamma.conf
  if greeter_ok /usr/share/xgreeters/gamma-greeter.desktop; then
    install -m 644 "$RAIZ/sistema/lightdm/50-gamma.conf" /etc/lightdm/lightdm.conf.d/50-gamma.conf
    msg "Greeter GAMMA testado: $(sed -n 's/^Exec=//p' /usr/share/xgreeters/gamma-greeter.desktop)"
  else
    # nunca deixa o LightDM apontando para um greeter que não abre: mantém o padrão
    rm -f /usr/share/xgreeters/gamma-greeter.desktop
    grep -v '^greeter-session=' "$RAIZ/sistema/lightdm/50-gamma.conf" > /etc/lightdm/lightdm.conf.d/50-gamma.conf
    chmod 644 /etc/lightdm/lightdm.conf.d/50-gamma.conf
    aviso "o greeter GAMMA não passou no teste; o login fica com o greeter padrão (tema GAMMA, mensagens no idioma do sistema)"
  fi
fi

cp "$0" "$BK/instalar-sistema.sh" 2>/dev/null || true
msg "Pronto. Reinicie para ver o GRUB, o Plymouth e o login."
msg "Para voltar: sudo $RAIZ/instalar-sistema.sh --desfazer"
