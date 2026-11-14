#!/usr/bin/env python3
# Arquivo: ferramentas/gerar_cursor.py
# Projeto: GAMMA Debian (tema Contador)
# Versão: 1.0.0
# Data e hora: 14/11/2026 19:30 (America/Sao_Paulo)
# Autoria: lstavares84, com Claude Opus 5.5 (Anthropic). Criação original.
# Gera o tema de cursor GAMMA-cursor (X11) com PIL e xcursorgen.
# Uso: python3 ferramentas/gerar_cursor.py   (requer xcursorgen, pacote x11-apps)
import math
import os
import pathlib
import shutil
import subprocess
import tempfile
from PIL import Image, ImageDraw

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DEST = RAIZ / "cursor" / "GAMMA-cursor"
TAMANHOS = [24, 32, 48, 64]
SS = 8
G = 32.0  # grade de desenho

BG = (3, 10, 4, 255)
ACC = (120, 255, 90, 255)
DIM = (35, 75, 35, 255)
RED = (255, 60, 50, 255)
CRF = (72, 4, 4, 255)
OKF = (10, 48, 12, 255)


def hexp(cx, cy, r, rot=0):
    out = []
    for i in range(6):
        a = math.radians(-90 + 60 * i + rot)
        out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def poly(d, pts, k, fill=BG, line=ACC, lw=1.5):
    p = [(x * k, y * k) for x, y in pts]
    d.polygon(p, fill=fill)
    d.line(p + [p[0]], fill=line, width=max(1, round(lw * k)), joint="curve")


def lines(d, segs, k, lw=1.6, under=True, cor=ACC):
    for s in segs:
        p = [(x * k, y * k) for x, y in s]
        if under:
            d.line(p, fill=BG, width=round((lw + 2.6) * k), joint="curve")
    for s in segs:
        p = [(x * k, y * k) for x, y in s]
        d.line(p, fill=cor, width=max(1, round(lw * k)), joint="curve")


SETA = [(5, 3), (5, 25), (10.5, 20), (14.5, 28.5), (18, 27), (14.2, 18.6), (21.5, 18.6)]


def seta(d, k):
    poly(d, SETA, k)


def emblema(d, k, tipo):
    cx, cy = 23.5, 24.5
    poly(d, hexp(cx, cy, 6), k, fill=OKF, line=ACC, lw=1.3)
    if tipo == "mais":
        lines(d, [[(cx - 3, cy), (cx + 3, cy)], [(cx, cy - 3), (cx, cy + 3)]], k, 1.4, False)
    elif tipo == "link":
        lines(d, [[(cx - 2.5, cy + 2.5), (cx + 2.5, cy - 2.5)], [(cx - 0.5, cy - 2.5), (cx + 2.5, cy - 2.5), (cx + 2.5, cy + 0.5)]], k, 1.3, False)
    elif tipo == "menu":
        lines(d, [[(cx - 3, cy - 2), (cx + 3, cy - 2)], [(cx - 3, cy), (cx + 3, cy)], [(cx - 3, cy + 2), (cx + 3, cy + 2)]], k, 1.0, False)
    elif tipo == "ajuda":
        d.ellipse([(cx - 1) * k, (cy + 1.6) * k, (cx + 1) * k, (cy + 3.4) * k], fill=ACC)
        lines(d, [[(cx - 2, cy - 2), (cx - 1, cy - 3.4), (cx + 1, cy - 3.4), (cx + 2.2, cy - 2), (cx, cy), (cx, cy + 0.6)]], k, 1.2, False)


def spinner(d, k, cx, cy, r, frame, lw=1.8):
    pts = hexp(cx, cy, r)
    pp = [(x * k, y * k) for x, y in pts]
    d.polygon(pp, fill=BG)
    d.line(pp + [pp[0]], fill=DIM, width=round(lw * k), joint="curve")
    for j in range(2):
        a = pts[(frame + j) % 6]
        b = pts[(frame + j + 1) % 6]
        d.line([(a[0] * k, a[1] * k), (b[0] * k, b[1] * k)], fill=ACC, width=round(lw * k))


def seta_dupla(d, k, ang):
    """Seta dupla centrada, ângulo em graus (0 = horizontal)."""
    base = [(-12, 0), (-6, -6), (-6, -2.5), (6, -2.5), (6, -6), (12, 0), (6, 6), (6, 2.5), (-6, 2.5), (-6, 6)]
    a = math.radians(ang)
    pts = [(16 + x * math.cos(a) - y * math.sin(a), 16 + x * math.sin(a) + y * math.cos(a)) for x, y in base]
    poly(d, pts, k)


def mover(d, k):
    pts = [(16, 3), (21, 8), (18, 8), (18, 14), (24, 14), (24, 11), (29, 16), (24, 21), (24, 18), (18, 18), (18, 24), (21, 24),
           (16, 29), (11, 24), (14, 24), (14, 18), (8, 18), (8, 21), (3, 16), (8, 11), (8, 14), (14, 14), (14, 8), (11, 8)]
    poly(d, pts, k)


MAO = [(12.5, 4), (12.5, 16), (11, 14.6), (8.6, 14.4), (7.6, 16.4), (12.2, 24.5), (14.5, 28.5), (25, 28.5), (26.5, 22), (26.5, 15.5),
       (24.5, 14), (22.5, 14.6), (22, 13.2), (19.8, 12.6), (18.8, 13.2), (18.2, 12), (16, 11.6), (15.6, 4), (14, 2.8)]

DESENHOS = {
    "default": (lambda d, k, f: seta(d, k), (5, 3)),
    "text": (lambda d, k, f: lines(d, [[(12, 5), (20, 5)], [(16, 5), (16, 27)], [(12, 27), (20, 27)]], k), (16, 16)),
    "pointer": (lambda d, k, f: poly(d, MAO, k), (13.6, 3.2)),
    "crosshair": (lambda d, k, f: (lines(d, [[(16, 3), (16, 12)], [(16, 20), (16, 29)], [(3, 16), (12, 16)], [(20, 16), (29, 16)]], k),
                                   poly(d, hexp(16, 16, 1.8), k, fill=ACC, line=ACC, lw=0.6)), (16, 16)),
    "move": (lambda d, k, f: mover(d, k), (16, 16)),
    "not-allowed": (lambda d, k, f: (poly(d, hexp(16, 16, 12), k, fill=CRF, line=RED, lw=1.8),
                                     lines(d, [[(9.5, 22.5), (22.5, 9.5)]], k, 2.0, False, RED)), (16, 16)),
    "ew-resize": (lambda d, k, f: seta_dupla(d, k, 0), (16, 16)),
    "ns-resize": (lambda d, k, f: seta_dupla(d, k, 90), (16, 16)),
    "nwse-resize": (lambda d, k, f: seta_dupla(d, k, 45), (16, 16)),
    "nesw-resize": (lambda d, k, f: seta_dupla(d, k, -45), (16, 16)),
    "copy": (lambda d, k, f: (seta(d, k), emblema(d, k, "mais")), (5, 3)),
    "alias": (lambda d, k, f: (seta(d, k), emblema(d, k, "link")), (5, 3)),
    "context-menu": (lambda d, k, f: (seta(d, k), emblema(d, k, "menu")), (5, 3)),
    "help": (lambda d, k, f: (seta(d, k), emblema(d, k, "ajuda")), (5, 3)),
    "cell": (lambda d, k, f: poly(d, [(13, 4), (19, 4), (19, 13), (28, 13), (28, 19), (19, 19), (19, 28), (13, 28), (13, 19), (4, 19), (4, 13), (13, 13)], k), (16, 16)),
    "wait": (lambda d, k, f: spinner(d, k, 16, 16, 11, f), (16, 16)),
    "progress": (lambda d, k, f: (seta(d, k), spinner(d, k, 24, 24.5, 6, f, 1.5)), (5, 3)),
}
ANIMADOS = {"wait", "progress"}
QUADROS = 6
ATRASO = 90

APELIDOS = {
    "default": ["left_ptr", "arrow", "top_left_arrow", "right_ptr", "center_ptr", "draft_large", "draft_small", "x-cursor", "X_cursor"],
    "text": ["xterm", "ibeam", "vertical-text"],
    "pointer": ["hand", "hand1", "hand2", "pointing_hand", "grab", "openhand", "9d800788f1b08800ae810202380a0822", "e29285e634086352946a0e7090d73106"],
    "crosshair": ["cross", "tcross", "cross_reverse", "diamond_cross", "zoom-in", "zoom-out", "target"],
    "move": ["fleur", "all-scroll", "grabbing", "closedhand", "dnd-move", "size_all", "4498f0e0c1937ffe01fd06f973665830", "9081237383d90e509aa00f00170e968f"],
    "not-allowed": ["forbidden", "crossed_circle", "circle", "no-drop", "dnd-no-drop", "dnd-none", "pirate", "03b6e0fcb3499374a867c041f52298f0"],
    "ew-resize": ["col-resize", "e-resize", "w-resize", "sb_h_double_arrow", "h_double_arrow", "left_side", "right_side", "size_hor", "split_h", "028006030e0e7ebffc7f7070c0600140", "14fef782d02440884392942c11205230"],
    "ns-resize": ["row-resize", "n-resize", "s-resize", "sb_v_double_arrow", "v_double_arrow", "top_side", "bottom_side", "size_ver", "split_v", "00008160000006810000408080010102", "2870a09082c103050810ffdffffe0204"],
    "nwse-resize": ["nw-resize", "se-resize", "top_left_corner", "bottom_right_corner", "size_fdiag", "c7088f0f3e6c8088236ef8e1e3e70000"],
    "nesw-resize": ["ne-resize", "sw-resize", "top_right_corner", "bottom_left_corner", "size_bdiag", "fcf1c3c7cd4491d801f1e1c78f100000"],
    "copy": ["dnd-copy", "1081e37283d90000800003c07f3ef6bf", "6407b0e94181790501fd1e167b474872"],
    "alias": ["link", "dnd-link", "640fb0e74195791501fd1ed57b41487f", "3085a0e285430894940527032f8b26df"],
    "context-menu": [],
    "help": ["question_arrow", "whats_this", "left_ptr_help", "5c6cd98b3f3ebcb1f9c7f1c204630408", "d9ce0ab605698f320427677b458ad60b"],
    "cell": ["plus"],
    "wait": ["watch"],
    "progress": ["left_ptr_watch", "half-busy", "08e8e1c95fe2fc01f976f1e063a24ccd", "3ecb610c1bf2410f44200f48c40d3599"],
}


def render(nome, tam, frame):
    k = tam * SS / G
    im = Image.new("RGBA", (tam * SS, tam * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    DESENHOS[nome][0](d, k, frame)
    return im.resize((tam, tam), Image.LANCZOS)


def gerar():
    if not shutil.which("xcursorgen"):
        raise SystemExit("xcursorgen não encontrado (pacote x11-apps).")
    if DEST.exists():
        shutil.rmtree(DEST)
    (DEST / "cursors").mkdir(parents=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        for nome, (_, (hx, hy)) in DESENHOS.items():
            linhas = []
            quadros = QUADROS if nome in ANIMADOS else 1
            for tam in TAMANHOS:
                for f in range(quadros):
                    arq = tmp / f"{nome}-{tam}-{f}.png"
                    render(nome, tam, f).save(arq)
                    x, y = round(hx * tam / G), round(hy * tam / G)
                    linha = f"{tam} {x} {y} {arq}"
                    if quadros > 1:
                        linha += f" {ATRASO}"
                    linhas.append(linha)
            cfg = tmp / f"{nome}.cfg"
            cfg.write_text("\n".join(linhas) + "\n")
            subprocess.run(["xcursorgen", str(cfg), str(DEST / "cursors" / nome)], check=True)
            for ap in APELIDOS.get(nome, []):
                alvo = DEST / "cursors" / ap
                if not alvo.exists():
                    os.symlink(nome, alvo)
        # prévia para o README
        prev = Image.new("RGBA", (len(DESENHOS) * 56 + 8, 64), (3, 10, 4, 255))
        for i, nome in enumerate(DESENHOS):
            prev.alpha_composite(render(nome, 48, 1), (8 + i * 56, 8))
        prev.save(RAIZ / "cursor" / "previa.png")
    (DEST / "index.theme").write_text(
        "# Arquivo: cursor/GAMMA-cursor/index.theme\n"
        "# Projeto: GAMMA Debian (tema Contador). Versão 1.0.0, 14/11/2026 19:30 (America/Sao_Paulo)\n"
        "# Autoria: lstavares84, com Claude Opus 5.5 (Anthropic). Criação original.\n"
        "[Icon Theme]\nName=GAMMA-cursor\nComment=Cursor do tema GAMMA Contador\nInherits=Adwaita\n",
        encoding="utf-8")
    n = len(list((DEST / "cursors").iterdir()))
    print(f"cursor: {len(DESENHOS)} desenhos, {n} nomes em {DEST}")


if __name__ == "__main__":
    gerar()
