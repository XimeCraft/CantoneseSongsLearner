import tkinter as tk
from tkinter import ttk

from tkmacosx import Button


# ------------------------------------------------------------------
#  Colors
#  -- One palette for light mode and one for dark mode,
#     picked from the system appearance when the app starts
# ------------------------------------------------------------------

LIGHT = {
    'bg': '#FAFAFA',          # window
    'surface': '#EDEDED',     # text boxes, lists
    'surface2': '#E2E2E2',    # headers, lyric line
    'fg': '#1E1E1E',
    'muted': '#6B6B6B',
    'accent': '#2B57B7',
    'on_accent': 'white',
    'answer': '#2E7D32',      # correct pronunciation shown for a wrong syllable
    'good': '#2E7D32',
    'bad': '#C62828',
    'button': '#616161',
    'button_over': '#757575',
    'on_button': 'white',
}

DARK = {
    'bg': '#1E1E1E',
    'surface': '#2C2C2C',
    'surface2': '#363636',
    'fg': '#E8E8E8',
    'muted': '#9A9A9A',
    'accent': '#3D6FD9',
    'on_accent': 'white',
    'answer': '#7CCB7F',
    'good': '#7CCB7F',
    'bad': '#EF6B6B',
    'button': '#4A4A4A',
    'button_over': '#5C5C5C',
    'on_button': 'white',
}

# Current palette, filled by apply()
C = dict(LIGHT)

FONT_FAMILY = 'PingFang SC'


def font(size=14, weight='normal'):
    return (FONT_FAMILY, size, weight)


def is_dark(root):
    try:
        return bool(int(root.tk.call('tk::unsupported::MacWindowStyle', 'isdark', root)))
    except tk.TclError:
        return False


def apply(root):
    """Pick the palette and set default colors for every widget."""

    C.update(DARK if is_dark(root) else LIGHT)
    root.configure(bg=C['bg'])

    # tk widgets
    root.option_add('*Background', C['bg'])
    root.option_add('*Foreground', C['fg'])
    root.option_add('*Font', font(14))
    for cls in ('Text', 'Entry', 'Listbox'):
        root.option_add(f'*{cls}.Background', C['surface'])
        root.option_add(f'*{cls}.insertBackground', C['fg'])
        root.option_add(f'*{cls}.selectBackground', C['accent'])
        root.option_add(f'*{cls}.selectForeground', C['on_accent'])
        root.option_add(f'*{cls}.relief', 'flat')
        root.option_add(f'*{cls}.borderWidth', 0)
        root.option_add(f'*{cls}.highlightThickness', 1)
        root.option_add(f'*{cls}.highlightBackground', C['surface2'])
        root.option_add(f'*{cls}.highlightColor', C['accent'])

    # ttk widgets
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('Treeview', background=C['surface'], fieldbackground=C['surface'],
                    foreground=C['fg'], rowheight=30, font=font(14), borderwidth=0)
    style.map('Treeview', background=[('selected', C['accent'])],
              foreground=[('selected', C['on_accent'])])
    style.configure('Treeview.Heading', background=C['surface2'], foreground=C['fg'],
                    font=font(13, 'bold'), relief='flat', padding=4)
    style.map('Treeview.Heading', background=[('active', C['surface2'])])
    style.configure('Vertical.TScrollbar', background=C['surface2'], troughcolor=C['bg'],
                    arrowcolor=C['muted'], bordercolor=C['bg'], relief='flat')
    style.configure('Horizontal.TProgressbar', background=C['accent'], troughcolor=C['surface'],
                    bordercolor=C['surface'], lightcolor=C['accent'], darkcolor=C['accent'])
    style.configure('TCheckbutton', background=C['bg'], foreground=C['fg'], font=font(13))
    style.map('TCheckbutton', background=[('active', C['bg'])])
    style.configure('TCombobox', fieldbackground=C['surface'], background=C['surface2'],
                    foreground=C['fg'], arrowcolor=C['muted'], bordercolor=C['surface2'],
                    lightcolor=C['surface'], darkcolor=C['surface'], padding=(8, 4))
    style.map('TCombobox', fieldbackground=[('readonly', C['surface'])],
              foreground=[('readonly', C['fg'])],
              selectbackground=[('readonly', C['surface'])],
              selectforeground=[('readonly', C['fg'])],
              background=[('active', C['surface2']), ('pressed', C['surface2'])])
    for opt, value in (('background', C['surface']), ('foreground', C['fg']),
                       ('selectBackground', C['accent']), ('selectForeground', C['on_accent'])):
        root.option_add(f'*TCombobox*Listbox.{opt}', value)
    root.option_add('*TCombobox*Listbox.font', font(13))


def button(parent, text, command, width=150, accent=False):
    bg = C['accent'] if accent else C['button']
    return Button(parent, text=text, command=command, width=width, height=32,
                  bg=bg, fg=C['on_button'], overbackground=C['button_over'] if not accent else bg,
                  activebackground=C['button_over'], borderless=1, focuscolor='', font=font(13))


def label(parent, text='', size=14, color='fg', weight='normal', **kw):
    return tk.Label(parent, text=text, fg=C[color], font=font(size, weight), **kw)
