#!/usr/bin/env python3
# Arquivo: ferramentas/adaptar_alice.py
# Projeto: GAMMA Debian (tema Contador)
# Versão: 1.0.0
# Data e hora: 22/11/2026 21:20 (America/Sao_Paulo)
# Autoria: lstavares84, com Claude Opus 5.5 (Anthropic). Script original; as imagens
#          de entrada (book/fonte/alice/) foram fornecidas pelo autor do tema.
# Adapta as 5 imagens "Alice Meets Matrix" para o celular (1272x2772): recorta em
# volta do assunto, amplia e estende topo e base com fundo gerado a partir da cena
# (névoa espelhada e desfocada, grão, linhas de varredura e chuva de código).
# No coelho, os rótulos de espectro nuclear ficam fora do recorte e viram sinais de rádio.
# Uso: python3 ferramentas/adaptar_alice.py book/fonte/alice wallpapers/celular/1272x2772 \
#        ~/.local/share/fonts/gamma/JetBrainsMono[wght].ttf
import sys, random, numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageChops, ImageEnhance

ENT, SAI, MONO = sys.argv[1:4]
W, H = 1272, 2772

def faixa(src, box, largura=W):
    im = src.crop(box)
    h = round(im.height * largura / im.width)
    im = im.resize((largura, h), Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))

def borda_cor(band, lado, n=24):
    a = np.asarray(band, float)
    rows = a[:n] if lado == 'top' else a[-n:]
    return rows.mean(0)          # perfil (largura x 3)

def extensao(band, altura, lado, escurecer=0.85, blur=60, modo='espelho'):
    """névoa gerada espelhando a cena junto da borda, com desfoque forte e escurecimento"""
    a = np.asarray(band, float)
    if modo == 'estica':        # estica as últimas linhas (bom para fundos lisos)
        rows = a[:40] if lado == 'top' else a[-40:]
        ext = np.asarray(Image.fromarray(rows.astype('uint8')).resize((W, altura), Image.BICUBIC), float)
    elif lado == 'top':
        ext = np.pad(a, ((altura, 0), (0, 0), (0, 0)), mode='symmetric')[:altura]
    else:
        ext = np.pad(a, ((0, altura), (0, 0), (0, 0)), mode='symmetric')[-altura:]
    im = Image.fromarray(ext.astype('uint8')).filter(ImageFilter.GaussianBlur(blur))
    t = np.asarray(im, float)
    y = np.linspace(0, 1, altura)[:, None, None]
    fade = (1 - y) if lado == 'top' else y          # 1 = longe da faixa
    lum = t.mean(2, keepdims=True)
    t = t * 0.75 + lum * 0.25                        # tira um pouco da saturação
    t = t * (1 - escurecer * fade ** 0.9)
    return Image.fromarray(np.clip(t, 0, 255).astype('uint8'))

def compor(band, y0, esc_top=0.85, esc_bot=0.85, blur=60, fundir=140, modo=('espelho', 'espelho'), blur_top=None):
    out = Image.new('RGB', (W, H))
    top = extensao(band, y0 + fundir, 'top', esc_top, blur_top or blur, modo[0])
    bot_h = H - (y0 + band.height) + fundir
    bot = extensao(band, bot_h, 'bot', esc_bot, blur, modo[1])
    out.paste(top, (0, 0)); out.paste(bot, (0, H - bot_h))
    # máscara da faixa com bordas suaves em cima e embaixo
    m = np.ones((band.height, W))
    r = np.linspace(0, 1, fundir)
    m[:fundir] *= r[:, None]; m[-fundir:] *= r[::-1][:, None]
    out.paste(band, (0, y0), Image.fromarray((m * 255).astype('uint8')))
    return out

def grao(im, forca=6, seed=1):
    rng = np.random.default_rng(seed)
    a = np.asarray(im, float) + rng.normal(0, forca, (H, W, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype('uint8'))

def varredura(im, periodo=4, forca=0.18, zonas=None):
    a = np.asarray(im, float).copy()
    for y in range(0, H, periodo):
        if zonas is None or any(z0 <= y < z1 for z0, z1 in zonas):
            a[y] *= (1 - forca)
    return Image.fromarray(a.astype('uint8'))

def chuva(im, zonas, seed=7, densidade=0.55, cor=(60, 255, 120), magenta=0.0, tam=26):
    """colunas de 0 e 1 caindo, só nas zonas (y0, y1, alfa_max) e com rastro que esmaece"""
    rnd = random.Random(seed)
    f = ImageFont.truetype(MONO, tam)
    camada = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(camada)
    passo = int(tam * 0.75)
    for x in range(8, W, passo):
        if rnd.random() > densidade: continue
        for (z0, z1, amax) in zonas:
            if rnd.random() < 0.35: continue
            comp = rnd.randint(6, 30); topo = rnd.randint(z0 - comp * tam // 2, z1)
            c = (255, 70, 220) if rnd.random() < magenta else cor
            for k in range(comp):
                y = topo + k * tam
                if not (z0 <= y < z1): continue
                cabeca = k == comp - 1
                a = amax * (0.25 + 0.75 * k / comp) * (1.0 if cabeca else rnd.uniform(0.4, 0.9))
                # esmaece perto das bordas da zona
                borda = min(y - z0, z1 - y) / 220
                a *= max(0, min(1, borda))
                cc = (220, 255, 225) if cabeca else c
                d.text((x, y), rnd.choice('01'), font=f, fill=cc + (int(a),))
    brilho = camada.filter(ImageFilter.GaussianBlur(5))
    base = im.convert('RGBA')
    base = Image.alpha_composite(base, brilho)
    base = Image.alpha_composite(base, camada)
    return base.convert('RGB')

def texto(im, itens):
    d = ImageDraw.Draw(im)
    for (x, y, s, tam, cor, anc) in itens:
        f = ImageFont.truetype(MONO, tam); d.text((x, y), s, font=f, fill=cor, anchor=anc)
    return im

def pico(im, x, y, w, h, picos, cor=(120, 255, 90)):
    """pequeno gráfico de sinal: linha de base com picos estreitos"""
    d = ImageDraw.Draw(im); pts = []
    for i in range(w + 1):
        v = 0.04 * np.sin(i / 7) + sum(a * np.exp(-((i - c * w) ** 2) / (2 * 4.0 ** 2)) for c, a in picos)
        pts.append((x + i, y - v * h))
    d.line(pts, fill=cor, width=3)

src = {n: Image.open(f'{ENT}/{n}.webp').convert('RGB') for n in range(1, 6)}

# 1 Olho: assunto centrado, névoa escura com linhas de varredura
b = faixa(src[1], (490, 0, 1610, 844))
im = compor(b, 900, 0.9, 0.9, 50, modo=('estica', 'estica'))
im = varredura(grao(im, 4, 1), 4, 0.16)
im.save(f'{SAI}/gamma-c11-olho.png')

# 2 Coelho: recorte só do coelho (rótulos de espectro nuclear ficam de fora)
s2 = src[2].copy(); d2 = ImageDraw.Draw(s2)
d2.rectangle((1248, 285, 1300, 380), fill=(2, 6, 3)); d2.rectangle((712, 392, 732, 472), fill=(2, 6, 3))
b = faixa(s2, (715, 0, 1285, 844))
im = compor(b, 470, 0.7, 0.7, 40, 120)
im = chuva(im, [(0, 600, 150), (2300, H, 150), (600, 2300, 55)], seed=12, densidade=0.5, tam=24)
pico(im, 110, 2470, 230, 90, [(0.5, 1.0)]); pico(im, 930, 2470, 230, 90, [(0.35, 0.9), (0.62, 0.8)])
im = texto(im, [
    (110, 2350, '433.92 MHz', 26, (190, 255, 170), 'ls'), (110, 2510, 'portadora', 22, (110, 170, 110), 'ls'),
    (930, 2350, '148.88 MHz', 26, (190, 255, 170), 'ls'), (930, 2510, 'ECO-1  K-7', 22, (110, 170, 110), 'ls'),
    (W - 110, 330, 'SIGNAL', 24, (120, 255, 90), 'rs'), (W - 110, 362, 'ANALYSIS', 24, (120, 255, 90), 'rs'),
    (W - 110, 394, '> RABBIT', 24, (120, 255, 90), 'rs'), (W - 110, 426, '> ???', 24, (120, 255, 90), 'rs'),
    (110, 2610, 'SOME PATTERNS ARE NOT RANDOM', 24, (120, 255, 90), 'ls'),
    (W - 110, 2610, 'RA 05h 42m 31s', 22, (110, 170, 110), 'rs')])
im.save(f'{SAI}/gamma-c12-coelho.png')

# 3 Arcos: Alice na cortina e o começo do mundo digital
b = faixa(src[3], (260, 0, 1060, 667))
im = compor(b, 1000, 0.75, 0.6, 70, 330)
im = chuva(im, [(80, 1150, 120), (2050, H, 90)], seed=31, densidade=0.45, magenta=0.08)
im.save(f'{SAI}/gamma-c13-arcos.png')

# 4 Lago: Alice na cortina; o coelho de luz é trazido para a água, embaixo
b = faixa(src[4], (330, 0, 1130, 667))
im = compor(b, 900, 0.75, 0.55, 70, 330)
coelho = src[4].crop((1640, 210, 1830, 470)).resize((380, 520), Image.LANCZOS)
mc = Image.new('L', coelho.size, 0); ImageDraw.Draw(mc).ellipse((60, 40, 320, 480), fill=255)
mc = mc.filter(ImageFilter.GaussianBlur(45))
reg = im.crop((W - 470, 1960, W - 90, 2480))
ca = np.asarray(coelho, float); lum = ca.mean(2); thr = np.percentile(lum, 80)
alfa = np.clip((lum - thr) / (lum.max() - thr) * 1.6, 0, 1)[..., None]   # só o que brilha
mist = Image.fromarray(np.clip(np.asarray(reg, float) * (1 - alfa) + ca * alfa, 0, 255).astype('uint8'))
im.paste(mist, (W - 470, 1960), mc)
im = chuva(im, [(80, 1000, 120)], seed=44, densidade=0.45, magenta=0.08)
im.save(f'{SAI}/gamma-c14-lago.png')

# 5 Cortina: já é vertical; amplia pouco e estende céu e névoa
b = faixa(src[5], (0, 0, 1086, 1448))
im = compor(b, 650, 0.55, 0.8, 80, 360, blur_top=130)
im = chuva(im, [(1500, 2300, 0)], seed=5)   # sem chuva extra: a cortina já tem
im.save(f'{SAI}/gamma-c15-cortina.png')
print('ok')
