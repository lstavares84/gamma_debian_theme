#!/usr/bin/env python3
# Arquivo: ferramentas/gerar_assets_gtk.py
# Projeto: GAMMA Debian (tema Contador)
# Versão: 1.0.0
# Data e hora: 14/11/2026 19:18 (America/Sao_Paulo)
# Autoria: lstavares84, com Claude Opus 5.5 (Anthropic). Criação original.
# Gera os SVG hexagonais usados pelo tema GTK 3 (caixas de seleção, opções,
# controle deslizante). Uso: python3 ferramentas/gerar_assets_gtk.py
import math
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "tema" / "GAMMA" / "gtk-3.0" / "assets"

BG, ACC, ICE, SUB, DIM = "#030A04", "#78FF5A", "#BEFFAA", "#6EAA6E", "#234B23"
OKF, NEF, NEB, NDF, NDB = "#0A300C", "#081C0A", "#40783C", "#081209", "#1E341E"


def pontos(cx, cy, r):
    w = math.sqrt(3) / 2 * r
    p = [(cx, cy - r), (cx + w, cy - r / 2), (cx + w, cy + r / 2),
         (cx, cy + r), (cx - w, cy + r / 2), (cx - w, cy - r / 2)]
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in p)


def svg(tamanho, corpo):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{tamanho}" height="{tamanho}" '
            f'viewBox="0 0 {tamanho} {tamanho}">{corpo}</svg>\n')


def hexa(t, preench, borda, larg=1.2, raio=None):
    r = raio if raio else t / 2 - larg
    return f'<polygon points="{pontos(t/2, t/2, r)}" fill="{preench}" stroke="{borda}" stroke-width="{larg}"/>'


VISTO = '<path d="M5.2 9.4l2.6 2.6 5.2-5.6" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="square"/>'
TRACO = '<rect x="5" y="8.2" width="8" height="1.6" fill="{c}"/>'


def gerar():
    DESTINO.mkdir(parents=True, exist_ok=True)
    t = 18
    a = {
        # caixa de seleção
        "check-unchecked": hexa(t, "none", SUB),
        "check-unchecked-hover": hexa(t, OKF, ICE),
        "check-unchecked-disabled": hexa(t, NEF, NEB),
        "check-checked": hexa(t, ACC, ACC) + VISTO.format(c=BG),
        "check-checked-hover": hexa(t, ICE, ICE) + VISTO.format(c=BG),
        "check-checked-disabled": hexa(t, NEB, NEB) + VISTO.format(c=NEF),
        "check-mixed": hexa(t, OKF, ACC) + TRACO.format(c=ACC),
        "check-mixed-hover": hexa(t, OKF, ICE) + TRACO.format(c=ICE),
        "check-mixed-disabled": hexa(t, NEF, NEB) + TRACO.format(c=NEB),
        # botão de opção
        "radio-unchecked": hexa(t, "none", SUB),
        "radio-unchecked-hover": hexa(t, OKF, ICE),
        "radio-unchecked-disabled": hexa(t, NEF, NEB),
        "radio-checked": hexa(t, OKF, ACC, 1.4) + hexa(t, ACC, ACC, 0.1, 4.2),
        "radio-checked-hover": hexa(t, OKF, ICE, 1.4) + hexa(t, ICE, ICE, 0.1, 4.2),
        "radio-checked-disabled": hexa(t, NEF, NEB, 1.4) + hexa(t, NEB, NEB, 0.1, 4.2),
        # controle deslizante
        "slider": hexa(t, ACC, ACC),
        "slider-hover": hexa(t, ICE, ICE),
        "slider-disabled": hexa(t, NEB, NEB),
    }
    for nome, corpo in a.items():
        (DESTINO / f"{nome}.svg").write_text(svg(t, corpo), encoding="utf-8")
    # indicador de área de trabalho (painel)
    for nome, (f, b) in {"ws-active": (ACC, ACC), "ws-busy": ("none", ICE), "ws-empty": ("none", DIM)}.items():
        (DESTINO / f"{nome}.svg").write_text(svg(16, hexa(16, f, b, 1.3)), encoding="utf-8")
    print(f"{len(a) + 3} arquivos em {DESTINO}")


if __name__ == "__main__":
    gerar()
