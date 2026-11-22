#!/usr/bin/env python3
# Arquivo: ferramentas/gerar_sistema.py
# Projeto: GAMMA Debian (tema Contador)
# Versão: 1.0.0
# Data e hora: 21/11/2026 22:05 (America/Sao_Paulo)
# Autoria: lstavares84, com Claude Opus 5.5 (Anthropic). Criação original.
#
# Gera os arquivos das telas de inicialização (opção A, "Terminal"):
#   sistema/grub/GAMMA       fundo, realce do item e fontes .pf2 do GRUB
#   sistema/plymouth/gamma   fundo e peças animadas do Plymouth
#   sistema/lightdm          fundos do login para os dois monitores
# Os fundos saem de book/fonte/boot.html (Firefox headless); as peças com
# transparência são desenhadas aqui com Pillow, na escala de 3440x1440.
# Requer: firefox, python3-pil, python3-fonttools, grub-mkfont (grub-common).
# Uso: python3 ferramentas/gerar_sistema.py
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
FONTE_MONO = RAIZ / "fontes" / "JetBrainsMono[wght].ttf"
SIS = RAIZ / "sistema"
GRUB = SIS / "grub" / "GAMMA"
PLY = SIS / "plymouth" / "gamma"
LDM = SIS / "lightdm"

C = dict(bg="#030A04", acc="#78FF5A", ice="#BEFFAA", white="#E6FFE1", sub="#6EAA6E", dim="#234B23",
         amb="#FFBE00", red="#FF3C32", waf="#3C2C00", ndf="#081209", ndb="#1E341E")


# ---------- fundos via Firefox ----------
def renderizar(tmp, params, w, h, saida):
    """Firefox não grava screenshot em caminho com acento; trabalha numa pasta temporária."""
    alvo = tmp / "r.png"
    if alvo.exists():
        alvo.unlink()
    url = f"file://{tmp}/boot.html?{params}&w={w}&h={h}"
    subprocess.run(["firefox", "--headless", "--no-remote", "--profile", str(tmp / "perfil"),
                    f"--window-size={w},{h}", "--screenshot", str(alvo), url],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    Image.open(alvo).convert("RGB").save(saida, optimize=True)
    print("  ", saida.relative_to(RAIZ))


# ---------- texto com Pillow ----------
_cache = {}


def fonte(tam, peso):
    k = (tam, peso)
    if k not in _cache:
        f = ImageFont.truetype(str(FONTE_MONO), tam)
        f.set_variation_by_axes([peso])
        _cache[k] = f
    return _cache[k]


def escreve(d, x, base, txt, tam, peso, cor, ls=0, ancora="ls"):
    """Escreve com espaçamento entre letras; ancora 'ls' (esquerda) ou 'rs' (direita), na linha de base."""
    f = fonte(tam, peso)
    larg = sum(f.getlength(ch) + ls for ch in txt) - ls
    if ancora == "rs":
        x -= larg
    for ch in txt:
        d.text((x, base), ch, font=f, fill=cor, anchor="ls")
        x += f.getlength(ch) + ls
    return larg


def com_brilho(img, cor, raio=6, forca=0.55):
    """Brilho de fósforo: cópia desfocada por baixo."""
    a = img.split()[3]
    glow = Image.new("RGBA", img.size, cor)
    glow.putalpha(a.filter(ImageFilter.GaussianBlur(raio)).point(lambda v: int(v * forca)))
    return Image.alpha_composite(glow, img)


def nova(w, h):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def linha_log(rotulo, valor=None, cor_valor="acc", titulo=False):
    """Linha do registro de carga: 1640x44, linha de base em y=32."""
    im = nova(1640, 44)
    d = ImageDraw.Draw(im)
    escreve(d, 0, 32, rotulo, 20, 700 if titulo else 500, C["ice"] if titulo else C["sub"], ls=2)
    if valor:
        fim = 1640 - len(valor) * 12 - 24
        for x in range(460, fim, 12):
            d.rectangle([x, 25, x + 1, 26], fill=C["dim"])
        escreve(d, 1640, 32, valor, 20, 700, C[cor_valor], ancora="rs")
    return im


def hexagono(cx, cy, r):
    import math
    return [(cx + r * math.cos(math.radians(-90 + 60 * i)), cy + r * math.sin(math.radians(-90 + 60 * i))) for i in range(6)]


def gerar_plymouth():
    print("Plymouth: peças")
    pecas = {
        "linha0": linha_log("GAMMA-6 INITIAL PROGRAM LOAD", titulo=True),
        "linha1": linha_log("MEMORY TEST", "524288 WORDS  OK"),
        "linha2": linha_log("CLOCK SYNC", "STRATUM 2  OK"),
        "linha3": linha_log("CRYPTO MODULE", "KEYED  OK"),
        "linha4": linha_log("PERIPHERAL BUS", "6 DEVICES  OK"),
        "selado": linha_log("SYSTEM VOLUME", "SEALED", "amb"),
        "liberado": linha_log("SYSTEM VOLUME", "UNSEALED  OK"),
        "desliga0": linha_log("GAMMA-6 SHUTDOWN SEQUENCE", titulo=True),
        "desliga1": linha_log("TERMINATING SESSIONS", "OK"),
        "desliga2": linha_log("SEALING SYSTEM VOLUME", "OK"),
        "desliga3": linha_log("POWER DOWN", "STANDBY", "amb"),
    }
    # pedido da chave (linha de base 32 em todas as faixas de 44)
    im = nova(1640, 44); escreve(ImageDraw.Draw(im), 0, 32, "CRYPTOGRAPHIC KEY REQUIRED TO UNSEAL SYSTEM VOLUME", 22, 700, C["amb"], ls=2)
    pecas["pedido"] = im
    im = nova(1640, 44); escreve(ImageDraw.Draw(im), 0, 32, "LOADING OPERATING SYSTEM", 18, 700, C["amb"], ls=3)
    pecas["carregando"] = im
    im = nova(1640, 44); escreve(ImageDraw.Draw(im), 0, 32, "FAILED ATTEMPTS ARE LOGGED.", 17, 500, C["dim"], ls=2)
    pecas["registro"] = im
    # "KEY >" e o asterisco: 50 de altura, linha de base em y=36
    im = nova(120, 50); escreve(ImageDraw.Draw(im), 0, 36, "KEY >", 26, 700, C["ice"])
    pecas["chave"] = im
    im = nova(32, 50); escreve(ImageDraw.Draw(im), 8, 36, "*", 26, 700, C["acc"])
    pecas["bala"] = com_brilho(im, C["acc"], 4)
    im = nova(32, 46); ImageDraw.Draw(im).rectangle([8, 8, 23, 37], fill=C["acc"])
    pecas["cursor"] = com_brilho(im, C["acc"], 4)
    # segmentos da barra de carga (18x20)
    for nome, cor in (("seg_on", C["amb"]), ("seg_off", C["waf"])):
        im = nova(18, 20); ImageDraw.Draw(im).rectangle([0, 0, 17, 19], fill=cor)
        pecas[nome] = im
    # nó aceso do anel giratório (centro em 20,20)
    im = nova(40, 40); ImageDraw.Draw(im).polygon(hexagono(20, 20, 9), fill=C["acc"])
    pecas["no"] = com_brilho(im, C["acc"], 4)
    for nome, im in pecas.items():
        im.save(PLY / f"{nome}.png", optimize=True)
    print(f"   {len(pecas)} imagens em {PLY.relative_to(RAIZ)}")


def gerar_grub_pecas():
    print("GRUB: realce e fontes")
    for lado in ("c", "n", "ne", "e", "se", "s", "sw", "w", "nw"):
        Image.new("RGB", (4, 4), C["acc"]).save(GRUB / f"select_{lado}.png")
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    with tempfile.TemporaryDirectory() as t:
        for peso, estilo in ((400, "Regular"), (700, "Bold")):
            f = instancer.instantiateVariableFont(TTFont(str(FONTE_MONO)), {"wght": peso}, updateFontNames=True)
            ttf = Path(t) / f"jbm-{estilo}.ttf"
            f.save(str(ttf))
            for tam in {"Regular": (16, 24), "Bold": (18, 24)}[estilo]:
                saida = GRUB / f"jetbrains-mono-{estilo.lower()}-{tam}.pf2"
                subprocess.run(["grub-mkfont", "-s", str(tam), "-o", str(saida), str(ttf)], check=True)
                print("  ", saida.relative_to(RAIZ))
    shutil.copy(RAIZ / "fontes" / "OFL-JetBrainsMono.txt", GRUB / "OFL-JetBrainsMono.txt")


def main():
    for p in (GRUB, PLY, LDM):
        p.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="gamma-") as t:
        tmp = Path(t)
        shutil.copy(RAIZ / "book" / "fonte" / "boot.html", tmp / "boot.html")
        (tmp / "perfil").mkdir()
        print("Fundos (Firefox headless)")
        renderizar(tmp, "t=grub&o=a&f=1", 3440, 1440, GRUB / "background.png")
        renderizar(tmp, "t=ply&o=a&f=1", 3440, 1440, PLY / "fundo.png")
        renderizar(tmp, "t=login&o=a&f=1", 3440, 1440, LDM / "fundo-3440x1440.png")
        renderizar(tmp, "t=login&o=a2&f=1", 2560, 1080, LDM / "fundo-2560x1080.png")
    gerar_plymouth()
    gerar_grub_pecas()


if __name__ == "__main__":
    os.chdir(RAIZ)
    main()
