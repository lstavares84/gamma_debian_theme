#!/usr/bin/env python3
# Arquivo: ferramentas/gamma_config.py
# Projeto: GAMMA Debian (tema Contador)
# Versão: 1.0.0
# Data e hora: 14/11/2026 19:38 (America/Sao_Paulo)
# Autoria: lstavares84, com Claude Opus 5.5 (Anthropic). Criação original.
#
# Aplica e restaura as configurações do XFCE usadas pelo tema GAMMA.
# Antes de mudar qualquer valor, grava o valor atual (ou a ausência dele)
# num arquivo JSON de backup; "restaurar" usa esse arquivo para voltar
# exatamente ao estado anterior.
#
#   gamma_config.py aplicar  DIR_BACKUP [--sem-wallpaper] [--intervalo MIN]
#   gamma_config.py restaurar DIR_BACKUP
import json
import pathlib
import re
import subprocess
import sys

HOME = pathlib.Path.home()
WALL = HOME / ".local" / "share" / "backgrounds" / "gamma"
PALETA_TERMINAL = ("#0A1A0B;#FF3C32;#5ADC3C;#FFBE00;#3CB49B;#C8E632;#8CF0BE;#BEFFAA;"
                   "#40783C;#FF7A6E;#78FF5A;#FFD75A;#6EE6C8;#E1FF78;#BEFFE1;#E6FFE1")

BASE = [
    ("xsettings", "/Net/ThemeName", "string", "GAMMA"),
    ("xsettings", "/Net/IconThemeName", "string", "GAMMA"),
    ("xsettings", "/Gtk/CursorThemeName", "string", "GAMMA-cursor"),
    ("xsettings", "/Gtk/CursorThemeSize", "int", "24"),
    ("xsettings", "/Gtk/FontName", "string", "Roboto 10"),
    ("xsettings", "/Gtk/MonospaceFontName", "string", "JetBrains Mono 10"),
    ("xfwm4", "/general/theme", "string", "GAMMA"),
    ("xfwm4", "/general/title_font", "string", "Roboto Bold 10"),
    ("xfce4-notifyd", "/theme", "string", "GAMMA"),
    ("xfce4-terminal", "/color-foreground", "string", "#BEFFAA"),
    ("xfce4-terminal", "/color-background", "string", "#030A04"),
    ("xfce4-terminal", "/color-cursor", "string", "#78FF5A"),
    ("xfce4-terminal", "/color-cursor-foreground", "string", "#030A04"),
    ("xfce4-terminal", "/color-cursor-use-default", "bool", "false"),
    ("xfce4-terminal", "/color-selection", "string", "#E6FFE1"),
    ("xfce4-terminal", "/color-selection-background", "string", "#0A300C"),
    ("xfce4-terminal", "/color-selection-use-default", "bool", "false"),
    ("xfce4-terminal", "/color-bold", "string", "#E6FFE1"),
    ("xfce4-terminal", "/color-bold-use-default", "bool", "false"),
    ("xfce4-terminal", "/color-palette", "string", PALETA_TERMINAL),
    ("xfce4-terminal", "/tab-activity-color", "string", "#FFBE00"),
    ("xfce4-terminal", "/font-name", "string", "JetBrains Mono 11"),
    ("xfce4-terminal", "/font-use-system", "bool", "false"),
]

GSETTINGS = [
    ("org.xfce.mousepad.preferences.view", "color-scheme", "'gamma'"),
    ("org.xfce.mousepad.preferences.view", "use-default-monospace-font", "true"),
]

CURSOR_PADRAO = HOME / ".icons" / "default" / "index.theme"


def sh(*args, check=False):
    return subprocess.run(args, capture_output=True, text=True, check=check)


def monitores():
    """Lista (nome, largura) dos monitores conectados, lida do xrandr."""
    out = sh("xrandr", "--listmonitors").stdout
    res = []
    for linha in out.splitlines()[1:]:
        m = re.search(r"(\d+)/\d+x(\d+)/\d+\S*\s+(\S+)$", linha.strip())
        if m:
            res.append((m.group(3), int(m.group(1))))
    return res


def n_areas():
    r = sh("xfconf-query", "-c", "xfwm4", "-p", "/general/workspace_count")
    try:
        return max(1, int(r.stdout.strip()))
    except ValueError:
        return 1


def itens_wallpaper(intervalo):
    itens = []
    for nome, largura in monitores():
        pasta = WALL / ("3440x1440" if largura >= 3000 else "2560x1080")
        imagens = sorted(pasta.glob("*.png"))
        if not imagens:
            continue
        for ws in range(n_areas()):
            p = f"/backdrop/screen0/monitor{nome}/workspace{ws}"
            itens += [
                ("xfce4-desktop", f"{p}/last-image", "string", str(imagens[0])),
                ("xfce4-desktop", f"{p}/image-style", "int", "5"),
                ("xfce4-desktop", f"{p}/backdrop-cycle-enable", "bool", "true"),
                ("xfce4-desktop", f"{p}/backdrop-cycle-period", "int", "1"),
                ("xfce4-desktop", f"{p}/backdrop-cycle-timer", "uint", str(intervalo)),
                ("xfce4-desktop", f"{p}/backdrop-cycle-random-order", "bool", "true"),
            ]
    return itens


def ler(canal, prop):
    r = sh("xfconf-query", "-c", canal, "-p", prop)
    if r.returncode != 0:
        return None
    return r.stdout.rstrip("\n")


def gravar(canal, prop, tipo, valor):
    r = sh("xfconf-query", "-c", canal, "-p", prop, "-n", "-t", tipo, "-s", valor)
    if r.returncode != 0:
        # a propriedade pode existir com outro tipo: remove e cria de novo
        sh("xfconf-query", "-c", canal, "-p", prop, "-r")
        r = sh("xfconf-query", "-c", canal, "-p", prop, "-n", "-t", tipo, "-s", valor)
    return r.returncode == 0


def aplicar(dir_backup, sem_wallpaper=False, intervalo=30):
    dir_backup = pathlib.Path(dir_backup)
    dir_backup.mkdir(parents=True, exist_ok=True)
    itens = list(BASE)
    if not sem_wallpaper:
        itens += itens_wallpaper(intervalo)

    backup = {"xfconf": [], "gsettings": [], "cursor_padrao": None}
    for canal, prop, tipo, _ in itens:
        backup["xfconf"].append({"canal": canal, "prop": prop, "tipo": tipo, "valor": ler(canal, prop)})
    for esquema, chave, _ in GSETTINGS:
        r = sh("gsettings", "get", esquema, chave)
        backup["gsettings"].append({"esquema": esquema, "chave": chave,
                                    "valor": r.stdout.strip() if r.returncode == 0 else None})
    if CURSOR_PADRAO.exists():
        backup["cursor_padrao"] = CURSOR_PADRAO.read_text(encoding="utf-8")
    (dir_backup / "backup.json").write_text(json.dumps(backup, indent=2, ensure_ascii=False), encoding="utf-8")

    falhas = [f"{c} {p}" for c, p, t, v in itens if not gravar(c, p, t, v)]
    for esquema, chave, valor in GSETTINGS:
        if sh("gsettings", "set", esquema, chave, valor).returncode != 0:
            falhas.append(f"gsettings {esquema} {chave}")
    CURSOR_PADRAO.parent.mkdir(parents=True, exist_ok=True)
    CURSOR_PADRAO.write_text("[Icon Theme]\nName=Default\nInherits=GAMMA-cursor\n", encoding="utf-8")

    print(f"aplicado: {len(itens) + len(GSETTINGS) - len(falhas)} configurações; backup em {dir_backup}")
    for f in falhas:
        print("  falhou:", f)
    return 0 if not falhas else 1


def restaurar(dir_backup):
    arq = pathlib.Path(dir_backup) / "backup.json"
    if not arq.exists():
        sys.exit(f"backup não encontrado: {arq}")
    b = json.loads(arq.read_text(encoding="utf-8"))
    falhas = []
    for it in b["xfconf"]:
        if it["valor"] is None:
            sh("xfconf-query", "-c", it["canal"], "-p", it["prop"], "-r")
        elif not gravar(it["canal"], it["prop"], it["tipo"], it["valor"]):
            falhas.append(f'{it["canal"]} {it["prop"]}')
    for it in b["gsettings"]:
        if it["valor"] is not None:
            if sh("gsettings", "set", it["esquema"], it["chave"], it["valor"]).returncode != 0:
                falhas.append(f'gsettings {it["chave"]}')
    if b.get("cursor_padrao") is None:
        if CURSOR_PADRAO.exists():
            CURSOR_PADRAO.unlink()
    else:
        CURSOR_PADRAO.write_text(b["cursor_padrao"], encoding="utf-8")
    print(f"restaurado a partir de {arq}")
    for f in falhas:
        print("  falhou:", f)
    return 0 if not falhas else 1


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("aplicar", "restaurar"):
        sys.exit(__doc__ or "uso: gamma_config.py aplicar|restaurar DIR_BACKUP")
    if sys.argv[1] == "aplicar":
        intervalo = 30
        if "--intervalo" in sys.argv:
            intervalo = int(sys.argv[sys.argv.index("--intervalo") + 1])
        sys.exit(aplicar(sys.argv[2], "--sem-wallpaper" in sys.argv, intervalo))
    sys.exit(restaurar(sys.argv[2]))
