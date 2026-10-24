from tkinter import *


def center_window(window, ws_width=880, ws_height=680):
    """Initial window size and postion
    """

    # Fit small screens
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    ws_width = min(ws_width, screen_width - 40)
    ws_height = min(ws_height, screen_height - 80)

    # Set Window to center
    center_x = int(screen_width/2 - ws_width/2)
    center_y = int(screen_height/2 - ws_height/2)

    # set window to the center of the screen
    window.geometry(f'{ws_width}x{ws_height}+{center_x}+{center_y}')
    window.minsize(760, 560)
    window.resizable(True, True)

    # Add window icon
    try:
        window.iconbitmap('assets/windowIcon.icns')
    except TclError:
        pass

def menubar(window, items):
    """items: list of (label, command); None adds a separator
    """
    menubar = Menu(window)
    mainmenu = Menu(menubar, tearoff=0)

    menubar.add_cascade(label='Main', menu=mainmenu)
    for item in items:
        if item is None:
            mainmenu.add_separator()
        else:
            mainmenu.add_command(label=item[0], command=item[1])
    mainmenu.add_separator()
    mainmenu.add_command(label='Exit', command=window.quit)

    window.config(menu=menubar)
