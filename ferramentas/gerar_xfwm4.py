#!/usr/bin/env python3
# Arquivo: ferramentas/gerar_xfwm4.py
# Projeto: GAMMA Debian (tema Contador)
# Versão: 1.0.0
# Data e hora: 14/11/2026 19:26 (America/Sao_Paulo)
# Autoria: lstavares84, com Claude Opus 5.5 (Anthropic). Criação original.
# Gera as imagens PNG e o themerc do tema de janelas xfwm4.
# Uso: python3 ferramentas/gerar_xfwm4.py
import math
import pathlib
from PIL import Image, ImageDraw

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DEST = RAIZ / "tema" / "GAMMA" / "xfwm4"

H = 32          # altura da barra de título (inclui 2 px de borda superior)
B = 2           # espessura das bordas laterais e inferior
BW = 30         # largura de cada botão
SS = 6          # superamostragem para traços suaves


def rgb(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


C = {k: rgb(v) for k, v in dict(
    bg="#030A04", accent="#78FF5A", ice="#BEFFAA", white="#E6FFE1", sub="#6EAA6E",
    dim="#234B23", red="#FF3C32", okf="#0A300C", crf="#480404", neb="#40783C",
    title="#050E06", outer_in="#030A04").items()}

# Cores por estado da janela: (externa, interna)
ESTADO = {
    "active": dict(outer=C["okf"], inner=C["accent"], sep=C["dim"], glyph=C["ice"]),
    "inactive": dict(outer=C["bg"], inner=C["dim"], sep=C["dim"], glyph=C["sub"]),
}


def barra(w, est):
    """Fundo da barra de título com borda superior dupla e separador inferior."""
    e = ESTADO[est]
    im = Image.new("RGBA", (w, H), C["title"])
    px = im.load()
    for x in range(w):
        px[x, 0] = e["outer"]
        px[x, 1] = e["inner"]
        px[x, H - 1] = e["sep"]
    return im


def salvar(im, nome):
    im.save(DEST / f"{nome}.png")


def pontos_hex(cx, cy, r):
    w = math.sqrt(3) / 2 * r
    return [(cx, cy - r), (cx + w, cy - r / 2), (cx + w, cy + r / 2),
            (cx, cy + r), (cx - w, cy + r / 2), (cx - w, cy - r / 2)]


def camada_glifo(desenho):
    """Desenha em alta resolução e reduz, devolvendo uma camada RGBA."""
    big = Image.new("RGBA", (BW * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    desenho(d, SS)
    return big.resize((BW, H), Image.LANCZOS)


def glifo(nome, cor, s):
    cx, cy = BW / 2 * s, (H / 2 + 1) * s
    lw = round(1.6 * s)
    d = None

    def f(dr, _):
        if nome == "close":
            k = 4.5 * s
            dr.line([(cx - k, cy - k), (cx + k, cy + k)], fill=cor, width=lw)
            dr.line([(cx + k, cy - k), (cx - k, cy + k)], fill=cor, width=lw)
        elif nome == "hide":
            dr.line([(cx - 5 * s, cy + 3 * s), (cx + 5 * s, cy + 3 * s)], fill=cor, width=lw)
        elif nome == "maximize":
            k = 4.5 * s
            dr.rectangle([cx - k, cy - k, cx + k, cy + k], outline=cor, width=lw)
        elif nome == "maximize-toggled":
            k = 3.6 * s
            o = 2.2 * s
            dr.rectangle([cx - k + o, cy - k - o, cx + k + o, cy + k - o], outline=cor, width=lw)
            dr.rectangle([cx - k - o * 0.4, cy - k + o * 0.4, cx + k - o * 0.4, cy + k + o * 0.4],
                         fill=None, outline=cor, width=lw)
        elif nome == "shade":
            dr.line([(cx - 5 * s, cy + 2 * s), (cx, cy - 3 * s), (cx + 5 * s, cy + 2 * s)], fill=cor, width=lw, joint="curve")
        elif nome == "shade-toggled":
            dr.line([(cx - 5 * s, cy - 2 * s), (cx, cy + 3 * s), (cx + 5 * s, cy - 2 * s)], fill=cor, width=lw, joint="curve")
        elif nome == "stick":
            dr.polygon(pontos_hex(cx, cy, 4.5 * s), outline=cor, width=lw)
        elif nome == "stick-toggled":
            dr.polygon(pontos_hex(cx, cy, 4.5 * s), fill=cor, outline=cor, width=lw)
        elif nome == "menu":
            dr.polygon(pontos_hex(cx, cy, 5.5 * s), outline=cor, width=lw)
            dr.ellipse([cx - 1.5 * s, cy - 1.5 * s, cx + 1.5 * s, cy + 1.5 * s], fill=cor)
    return f


def botao(nome, modo):
    """modo: active, inactive, prelight, pressed."""
    est = "inactive" if modo == "inactive" else "active"
    base = barra(BW, est)
    s = SS
    cor_glifo = ESTADO[est]["glyph"]
    fundo = None
    if modo == "prelight":
        if nome == "close":
            fundo = (C["crf"], C["red"])
            cor_glifo = C["white"]
        else:
            fundo = (C["okf"], C["accent"])
            cor_glifo = C["accent"]
    elif modo == "pressed":
        if nome == "close":
            fundo = (C["red"], C["red"])
        else:
            fundo = (C["accent"], C["accent"])
        cor_glifo = C["bg"]

    if fundo:
        def hexf(dr, _):
            dr.polygon(pontos_hex(BW / 2 * s, (H / 2 + 1) * s, 11.5 * s), fill=fundo[0], outline=fundo[1], width=round(1.3 * s))
        base.alpha_composite(camada_glifo(hexf))
    base.alpha_composite(camada_glifo(glifo(nome, cor_glifo, s)))
    # restaura as linhas de borda por cima, para que nada as cubra
    px = base.load()
    e = ESTADO[est]
    for x in range(BW):
        px[x, 0] = e["outer"]
        px[x, 1] = e["inner"]
        px[x, H - 1] = e["sep"]
    return base


def gerar():
    DEST.mkdir(parents=True, exist_ok=True)
    for est in ("active", "inactive"):
        e = ESTADO[est]
        for i in range(1, 6):
            salvar(barra(4, est), f"title-{i}-{est}")
        # cantos superiores: coluna externa + coluna interna + fundo da barra
        tl = Image.new("RGBA", (B, H), e["outer"])
        for y in range(1, H):
            tl.putpixel((1, y), e["inner"])
        salvar(tl, f"top-left-{est}")
        salvar(tl.transpose(Image.FLIP_LEFT_RIGHT), f"top-right-{est}")
        lado = Image.new("RGBA", (B, 1), e["outer"])
        lado.putpixel((1, 0), e["inner"])
        salvar(lado, f"left-{est}")
        salvar(lado.transpose(Image.FLIP_LEFT_RIGHT), f"right-{est}")
        baixo = Image.new("RGBA", (1, B), e["outer"])
        baixo.putpixel((0, 0), e["inner"])
        salvar(baixo, f"bottom-{est}")
        bl = Image.new("RGBA", (B, B), e["outer"])
        bl.putpixel((1, 0), e["inner"])
        salvar(bl, f"bottom-left-{est}")
        salvar(bl.transpose(Image.FLIP_LEFT_RIGHT), f"bottom-right-{est}")

    nomes = ["close", "hide", "maximize", "maximize-toggled", "shade", "shade-toggled",
             "stick", "stick-toggled", "menu"]
    for n in nomes:
        for modo in ("active", "inactive", "prelight", "pressed"):
            salvar(botao(n, modo), f"{n}-{modo}")

    themerc = """# Arquivo: tema/GAMMA/xfwm4/themerc
# Projeto: GAMMA Debian (tema Contador)
# Versão: 1.0.0
# Data e hora: 14/11/2026 19:26 (America/Sao_Paulo)
# Autoria: lstavares84, com Claude Opus 5.5 (Anthropic). Criação original.
# Gerado por ferramentas/gerar_xfwm4.py
button_offset=4
button_spacing=0
full_width_title=true
title_shadow_active=false
title_shadow_inactive=false
title_vertical_offset_active=1
title_vertical_offset_inactive=1
title_horizontal_offset=10
active_text_color=#E6FFE1
inactive_text_color=#6EAA6E
active_text_shadow_color=#030A04
inactive_text_shadow_color=#030A04
maximized_offset=0
shadow_delta_height=0
shadow_delta_width=0
shadow_delta_x=0
shadow_delta_y=-4
shadow_opacity=60
"""
    (DEST / "themerc").write_text(themerc, encoding="utf-8")
    print("xfwm4:", len(list(DEST.glob("*.png"))), "imagens")


if __name__ == "__main__":
    gerar()
