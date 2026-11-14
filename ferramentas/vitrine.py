#!/usr/bin/env python3
# Arquivo: ferramentas/vitrine.py
# Projeto: GAMMA Debian (tema Contador)
# Versão: 1.0.0
# Data e hora: 14/11/2026 19:46 (America/Sao_Paulo)
# Autoria: lstavares84, com Claude Opus 5.5 (Anthropic). Criação original.
# Janela de teste com os principais controles GTK 3, para conferir o tema.
# Uso: python3 ferramentas/vitrine.py   (requer python3-gi)
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402


def secao(titulo):
    lb = Gtk.Label(label=titulo, xalign=0)
    lb.get_style_context().add_class("dim-label")
    return lb


def main():
    win = Gtk.Window(title="Vitrine GAMMA")
    win.set_default_size(980, 640)
    win.connect("destroy", Gtk.main_quit)

    raiz = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    win.add(raiz)

    barra = Gtk.MenuBar()
    for nome, itens in (("Arquivo", ["Abrir", "Salvar", None, "Sair"]), ("Editar", ["Copiar", "Colar"]), ("Ajuda", ["Sobre"])):
        mi = Gtk.MenuItem(label=nome)
        sub = Gtk.Menu()
        for it in itens:
            sub.append(Gtk.SeparatorMenuItem() if it is None else Gtk.MenuItem(label=it))
        mi.set_submenu(sub)
        barra.append(mi)
    raiz.pack_start(barra, False, False, 0)

    nb = Gtk.Notebook()
    raiz.pack_start(nb, True, True, 0)

    pag = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=24, margin=20)
    nb.append_page(pag, Gtk.Label(label="Controles"))
    nb.append_page(Gtk.Label(label="Segunda aba"), Gtk.Label(label="Estilo"))
    nb.append_page(Gtk.Label(label="Terceira aba"), Gtk.Label(label="Ícones"))

    # coluna 1: lista
    col1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    col1.pack_start(secao("Tema"), False, False, 0)
    loja = Gtk.ListStore(str, str)
    for n, t in [("Adwaita", "gtk3"), ("Adwaita-dark", "gtk3"), ("GAMMA", "ativo"), ("HighContrast", "gtk3"),
                 ("Kokodi", "xfwm4"), ("Moheli", "xfwm4"), ("Daloa", "xfwm4"), ("Smoke", "xfwm4"), ("Retro", "xfwm4"),
                 ("Default", "xfwm4"), ("Bright", "xfwm4"), ("Emacs", "gtk2"), ("Raleigh", "gtk2"), ("XP-Balloon", "notify")]:
        loja.append([n, t])
    tv = Gtk.TreeView(model=loja)
    for i, titulo in enumerate(["Nome", "Tipo"]):
        tv.append_column(Gtk.TreeViewColumn(titulo, Gtk.CellRendererText(), text=i))
    tv.get_selection().select_path(Gtk.TreePath(2))
    sw = Gtk.ScrolledWindow()
    sw.set_size_request(300, 360)
    sw.add(tv)
    col1.pack_start(sw, True, True, 0)
    pag.pack_start(col1, False, False, 0)

    # coluna 2: campos e seleção
    col2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    col2.pack_start(secao("Fonte da interface"), False, False, 0)
    e1 = Gtk.Entry(text="Roboto Regular 10")
    col2.pack_start(e1, False, False, 0)
    col2.pack_start(secao("Fonte monoespaçada"), False, False, 0)
    e2 = Gtk.Entry(text="JetBrains Mono 11")
    col2.pack_start(e2, False, False, 0)
    combo = Gtk.ComboBoxText()
    for t in ("Subpixel RGB", "Escala de cinza", "Nenhuma"):
        combo.append_text(t)
    combo.set_active(0)
    linha = Gtk.Box(spacing=10)
    linha.pack_start(combo, True, True, 0)
    linha.pack_start(Gtk.SpinButton.new_with_range(72, 200, 1), False, False, 0)
    col2.pack_start(linha, False, False, 0)
    c1 = Gtk.CheckButton(label="Ativar antisserrilhado")
    c1.set_active(True)
    c2 = Gtk.CheckButton(label="Usar dicas completas")
    c3 = Gtk.CheckButton(label="Detectar DPI (indisponível)")
    c3.set_sensitive(False)
    r1 = Gtk.RadioButton(label="Escala 1x")
    r2 = Gtk.RadioButton.new_with_label_from_widget(r1, "Escala 1,25x")
    for w in (c1, c2, c3, r1, r2):
        col2.pack_start(w, False, False, 0)
    sl = Gtk.Box(spacing=10)
    sw1 = Gtk.Switch()
    sw1.set_active(True)
    sl.pack_start(sw1, False, False, 0)
    sl.pack_start(Gtk.Switch(), False, False, 0)
    col2.pack_start(sl, False, False, 0)
    pag.pack_start(col2, True, True, 0)

    # coluna 3: valores e botões
    col3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    col3.pack_start(secao("DPI personalizado"), False, False, 0)
    esc = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 72, 144, 1)
    esc.set_value(110)
    col3.pack_start(esc, False, False, 0)
    pb = Gtk.ProgressBar()
    pb.set_fraction(0.64)
    col3.pack_start(secao("Copiando"), False, False, 0)
    col3.pack_start(pb, False, False, 0)
    lv = Gtk.LevelBar()
    lv.set_value(0.61)
    col3.pack_start(lv, False, False, 0)
    ib = Gtk.InfoBar()
    ib.set_message_type(Gtk.MessageType.WARNING)
    ib.get_content_area().add(Gtk.Label(label="Reabra os programas para ver a nova fonte."))
    col3.pack_start(ib, False, False, 0)
    ib2 = Gtk.InfoBar()
    ib2.set_message_type(Gtk.MessageType.ERROR)
    ib2.get_content_area().add(Gtk.Label(label="Sem permissão de escrita."))
    col3.pack_start(ib2, False, False, 0)
    bts = Gtk.Box(spacing=8)
    b1 = Gtk.Button(label="Fechar")
    b2 = Gtk.Button(label="Aplicar")
    b2.get_style_context().add_class("suggested-action")
    b3 = Gtk.Button(label="Apagar")
    b3.get_style_context().add_class("destructive-action")
    b4 = Gtk.Button(label="Desabilitado")
    b4.set_sensitive(False)
    for b in (b1, b2, b3, b4):
        bts.pack_start(b, False, False, 0)
    col3.pack_start(bts, False, False, 0)
    pag.pack_start(col3, True, True, 0)

    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
