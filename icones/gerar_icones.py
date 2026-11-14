#!/usr/bin/env python3
# Arquivo: icones/gerar_icones.py
# Projeto: GAMMA Debian (tema Contador)
# Versão: 1.0.0
# Data e hora: 14/11/2026 19:34 (America/Sao_Paulo)
# Autoria: lstavares84, com Claude Opus 5.5 (Anthropic). Criação original.
#
# Cria o tema de ícones "GAMMA" no computador do usuário. Ele herda do
# Papirus-Dark (instalado pelo pacote papirus-icon-theme, licença GPL-3.0) e
# substitui só as pastas, recoloridas com a paleta GAMMA. Os ícones derivados
# são gerados localmente e não ficam neste repositório.
# Uso: python3 icones/gerar_icones.py [destino]   (padrão: ~/.icons/GAMMA)
import pathlib
import re
import sys

ORIGEM = pathlib.Path("/usr/share/icons/Papirus")
DESTINO = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.home() / ".icons" / "GAMMA"

# cores da variante verde do Papirus -> paleta GAMMA
TROCA = {
    "#87b158": "#6EAA6E",   # frente da pasta (sub)
    "#60924b": "#40783C",   # fundo da pasta (neutro, borda)
    "#e4e4e4": "#BEFFAA",   # papel (ice)
    "#2f3e1f": "#0A300C",   # emblema (OK, preenchimento)
}
PADRAO = re.compile(r"^(folder|user)-blue(.*)\.svg$")


def recolorir(texto):
    for a, b in TROCA.items():
        texto = re.sub(a, b, texto, flags=re.IGNORECASE)
    return texto


def main():
    if not ORIGEM.is_dir():
        sys.exit("Papirus não encontrado em /usr/share/icons/Papirus. Instale com: sudo apt install papirus-icon-theme")
    pastas = sorted(p for p in ORIGEM.iterdir() if p.is_dir() and (p / "places").is_dir())
    total = 0
    tamanhos = []
    for pasta in pastas:
        places = pasta / "places"
        saida = DESTINO / pasta.name / "places"
        criado = False
        for item in places.iterdir():
            real = item.resolve()
            m = PADRAO.match(real.name)
            if not m:
                continue
            fonte = real.with_name(f"{m.group(1)}-green{m.group(2)}.svg")
            if not fonte.exists():
                continue
            if not criado:
                saida.mkdir(parents=True, exist_ok=True)
                criado = True
            (saida / item.name).write_text(recolorir(fonte.read_text(encoding="utf-8")), encoding="utf-8")
            total += 1
        if criado:
            tamanhos.append(pasta.name)

    def escala(nome):
        return 2 if "@2x" in nome else 1

    def base(nome):
        return int(nome.split("x")[0])

    dirs = [f"{t}/places" for t in tamanhos]
    secoes = "\n".join(
        f"[{t}/places]\nContext=Places\nSize={base(t)}\nScale={escala(t)}\nType=Fixed\n" for t in tamanhos)
    indice = (
        "# Gerado por icones/gerar_icones.py (GAMMA Debian, versão 1.0.0)\n"
        "[Icon Theme]\nName=GAMMA\nComment=Papirus-Dark com pastas na paleta GAMMA\n"
        "Inherits=Papirus-Dark,Papirus,Adwaita,hicolor\n"
        f"Directories={','.join(dirs)}\n\n{secoes}")
    DESTINO.mkdir(parents=True, exist_ok=True)
    (DESTINO / "index.theme").write_text(indice, encoding="utf-8")
    print(f"ícones: {total} pastas recoloridas em {len(tamanhos)} tamanhos, destino {DESTINO}")


if __name__ == "__main__":
    main()
