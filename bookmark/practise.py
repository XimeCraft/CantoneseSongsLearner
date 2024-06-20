"""
This project lets you try out Tkinter/and practice it!
Authors: David Mutchler, Valerie Galluzzi, Mark Hays, Amanda Stouder,
         their colleagues and Xiao.
"""  # TODO: 1. PUT YOUR NAME IN THE ABOVE LINE.

from curses.ascii import isdigit
from tkinter import *


def main():
    """ Constructs a GUI with stuff on it. """
    # ------------------------------------------------------------------
    # TODO: 2. After reading and understanding the m1e module,
    #   ** make a window that shows up. **
    # ------------------------------------------------------------------
    root = Tk()
    # root.configure(background='green')
    
    # ------------------------------------------------------------------
    # TODO: 3. After reading and understanding the m2e module,
    #   ** put a Frame on the window. **
    # ------------------------------------------------------------------
    frame = Frame(root, padx=10, pady=10)
    frame.grid()

    # ------------------------------------------------------------------
    # TODO: 4. After reading and understanding the m2e module,
    #   ** put a Button on the Frame. **
    # ------------------------------------------------------------------


    # ------------------------------------------------------------------
    # TODO: 5. After reading and understanding the m3e module,
    #   ** make your Button respond to a button-press **
    #   ** by printing   "Hello"  on the Console.     **
    # ------------------------------------------------------------------

    def print_hello():
        print('Hello!')

    button1 = Button(frame, text='Print', command=lambda: print_hello())
    button1.grid()
    
    # ------------------------------------------------------------------
    # TODO: 6. After reading and understanding the m4e module,
    #   -- Put an Entry box on the Frame.
    #   -- Put a second Button on the Frame.
    #   -- Make this new Button, when pressed, print "Hello"
    #        on the Console if the current string in the Entry box
    #        is the string 'ok', but print "Goodbye" otherwise.
    # ------------------------------------------------------------------

    e = Entry(frame, bg='light grey', width=100)
    e.grid()

    def check_string():
        current = e.get()
        if current == 'ok':
            print('Hello')
        else:
            print('Goodbye')

    button2 = Button(frame, text='Check string', command=lambda: check_string())
    button2.grid()

    # ------------------------------------------------------------------
    # TODO: 7.
    #    -- Put a second Entry on the Frame.
    #    -- Put a third Button on the frame.
    #    -- Make this new Button respond to a button-press as follows:
    #
    #    Pressing this new Button causes the STRING that the user typed
    #    in the FIRST Entry box to be printed N times on the Console,
    #      where N is the INTEGER that the user typed
    #      in the SECOND Entry box.
    #
    #    If the user fails to enter an integer,
    #    that is a "user error" -- do NOT deal with that.
    #
    # ------------------------------------------------------------------

    e2 = Entry(frame, bg='light green', width=100)
    e2.grid()

    def check_times():
        content = e.get()
        times = int(e2.get())

        if isinstance(times, int):
            print(content*times)
        else:
            print('user error')


    button3 = Button(frame, text='Check Tiimes', command=lambda: check_times())
    button3.grid()

    ####################################################################
    # HINT:
    #   You will need to obtain the INTEGER from the STRING
    #   that the GET method returns.
    #   Use the   int   function to do so, as in this example:
    #      s = entry_box.get()
    #      n = int(s)
    ####################################################################

    # ------------------------------------------------------------------
    # TODO: 8. As time permits, do other interesting GUI things!
    # ------------------------------------------------------------------
    root.mainloop()


def main2():
    """ Constructs a GUI that will be used MUCH later to control EV3. """
    # ------------------------------------------------------------------
    # TODO: 2. Follow along with the video to make a remote control GUI
    # For every grid() method call you will add a row and a column argument
    # ------------------------------------------------------------------

    root = Tk()
    root.title("MQTT Remote")

    main_frame = Frame(root, padx=20, pady=20)
    main_frame.grid()  # only grid call that does NOT need a row and column

    left_speed_label = Label(main_frame, text="Left")
    left_speed_label.grid()
    left_speed_entry = Entry(main_frame, width=8)
    left_speed_entry.insert(0, "600")
    left_speed_entry.grid()

    right_speed_label = Label(main_frame, text="Right")
    right_speed_label.grid()
    right_speed_entry = Entry(main_frame, width=8, justify=RIGHT)
    right_speed_entry.insert(0, "600")
    right_speed_entry.grid()

    forward_button = Button(main_frame, text="Forward")
    forward_button.grid()
    forward_button['command'] = lambda: print("Forward button")
    root.bind('<Up>', lambda event: print("Forward key"))

    left_button = Button(main_frame, text="Left")
    left_button.grid()
    left_button['command'] = lambda: print("Left button")
    root.bind('<Left>', lambda event: print("Left key"))

    stop_button = Button(main_frame, text="Stop")
    stop_button.grid()
    stop_button['command'] = lambda: print("Stop button")
    root.bind('<space>', lambda event: print("Stop key"))

    right_button = Button(main_frame, text="Right")
    right_button.grid()
    right_button['command'] = lambda: print("Right button")
    root.bind('<Right>', lambda event: print("Right key"))

    back_button = Button(main_frame, text="Back")
    back_button.grid()
    back_button['command'] = lambda: print("Back button")
    root.bind('<Down>', lambda event: print("Back key"))

    up_button = Button(main_frame, text="Up")
    up_button.grid()
    up_button['command'] = lambda: print("Up button")
    root.bind('<u>', lambda event: print("Up key"))

    down_button = Button(main_frame, text="Down")
    down_button.grid()
    down_button['command'] = lambda: print("Down button")
    root.bind('<j>', lambda event: print("Down key"))

    # Buttons for quit and exit
    q_button = Button(main_frame, text="Quit")
    q_button.grid()
    q_button['command'] = lambda: print("Quit button")

    e_button = Button(main_frame, text="Exit")
    e_button.grid()
    e_button['command'] = lambda: exit()

    root.mainloop()


import random


def main3():
    # Root (main) window
    root = Tk()
    root.title('Hello!')

    # Frame
    frame1 = Frame(root)
    frame1.grid()

    # Label
    label = Label(frame1, text='This is a Label above a Button')
    label.grid()

    # Two buttons
    change_title_button = Button(frame1,
                                     text='Change the Title (above)')
    change_title_button.grid()
    change_title_button['command'] = lambda: change_title(root)

    quit_button = Button(frame1, text='Quit')
    quit_button.grid()
    quit_button['command'] = lambda: close_window(root)

    # Another Label, with its text set another way
    label2 = Label(frame1)
    label2['text'] = 'Later, we will put Labels BESIDE Buttons'
    label2.grid()

    root.mainloop()


def change_title(root):
    # Make a new 8-letter title chosen randomly from 'A' to 'Z'.
    new_title = ''
    for k in range(8):  # @UnusedVariable
        new_title = new_title + chr(ord('A') + random.randrange(26))

    root.title(new_title)


def close_window(root):
    root.destroy()




"""
Example showing for tkinter and 
  -- Entry
  -- Using its GET and SET methods to get/set an Entry's information
     (as opposed to using a CONTROL VARIABLE as in a subsequent module)
     This is the SIMPLER way to use an Entry box.
     See a subsequent module for a more complicated alternative that is
     sometimes more convenient than this way.
Authors: David Mutchler and his colleagues
         at Rose-Hulman Institute of Technology.
"""

class Temperature(object):
    def __init__(self):
        self.entry_for_temperature = None
        self.label_for_temperature = None


def main4():
    # Data object to hold information needed for callbacks.
    temperature = Temperature()

    # Root window and Frame on it.
    root = Tk()

    frame = Frame(root, padx=20, pady=20)
    frame.grid()

    # The Entry box, into which the user can enter a temperature.
    # We store it in the Temperature object so that we can later
    # get its contents.
    entry = Entry(frame, width=8)
    entry.grid()
    temperature.entry_for_temperature = entry

    # A Label which will display the temperature corresponding to the
    # temperature that the user enters in the Entry box.
    # We store the label in the Temperature object so that we can later
    # put the computed temperature on it.
    label = Label(frame, text='Enter a temperature in the box')
    label.grid()
    temperature.label_for_temperature = label

    # Buttons that: get Entry value, compute and display temperature
    button1 = Button(frame, text='Compute Fahrenheit from Celsius')
    button1.grid()
    button1['command'] = lambda: fahrenheit_from_celsius(temperature)

    button2 = Button(frame, text='Compute Celsius from Fahrenheit')
    button2.grid()
    button2['command'] = lambda: celsius_from_fahrenheit(temperature)

    root.mainloop()


def celsius_from_fahrenheit(temperature):
    # Get the contents (as a STRING) from the Entry box.
    entry = temperature.entry_for_temperature
    contents_of_entry_box = entry.get()

    # Convert that STRING to a floating point NUMBER.
    # Use the number to compute the corresponding Celsius temperature.
    fahrenheit = float(contents_of_entry_box)
    celsius = (5 / 9) * (fahrenheit - 32)

    # Display the computed Celsius temperature in the Label
    # provided for it.
    format_string = '{:0.2f} Fahrenheit is {:0.2f} Celsius'
    answer = format_string.format(fahrenheit, celsius)
    temperature.label_for_temperature['text'] = answer


def fahrenheit_from_celsius(temperature):
    # Get the contents (as a STRING) from the Entry box.
    entry = temperature.entry_for_temperature
    contents_of_entry_box = entry.get()

    # Convert that STRING to a floating point NUMBER.
    # Use the number to compute corresponding Fahrenheit temperature.
    celsius = float(contents_of_entry_box)
    fahrenheit = (celsius * (9 / 5)) + 32

    # Display the computed Fahrenheit temperature in the Label
    # provided for it.
    format_string = '{:0.2f} Celsius is {:0.2f} Fahrenheit'
    answer = format_string.format(celsius, fahrenheit)
    temperature.label_for_temperature['text'] = answer


"""
Example showing for tkinter and how to:
  -- 1. BIND callback functions (event-handlers) to KEYBOARD EVENTs.
  -- 2. RESPOND to KEYBOARD events.
There is LOTS more you can do with Events beyond what is shown here.
See the next module for more, and for all (or at least most) of the
details, see Section 30 of:
  tkinterReference-NewMexicoTech.pdf
in the Graphics section of the Resources web page for this course.
That document is also available in html form at:
  http://infohost.nmt.edu/tcc/help/pubs/tkinter/events.html
Authors: David Mutchler and his colleagues
         at Rose-Hulman Institute of Technology.
"""

def main5():
    # Make root, frame and 3 buttons with callbacks.
    root = Tk()

    main_frame = Frame(root, padx=20, pady=20)
    main_frame.grid()

    left_button = Button(main_frame, text='Left')
    left_button.grid()

    right_button = Button(main_frame, text='Right')
    right_button.grid()

    spin_button = Button(main_frame, text='Spin')
    spin_button.grid()

    left_button['command'] = lambda: go_left_button()
    right_button['command'] = lambda: go_right()
    spin_button['command'] = lambda: spin()

    # --------------------------------------------------------------------
    # For general-purpose keyboard events, use    root.bind_all(...).
    # This method "binds" (attaches) the given EVENT to the given
    # CALLBACK FUNCTION for ALL widgets on this root and its descendants.
    #
    # Note that the lambda function for bind_all requires a parameter.
    # When the lambda function is called by tkinter in its mainloop,
    # the actual event that fired is sent as the argument.  You can
    # use this to obtain details about the event.
    #
    # Try press, release, click and press-and-hold in the examples.
    # --------------------------------------------------------------------
    root.bind_all('<KeyPress>', lambda event: pressed_a_key(event))
    root.bind_all('<KeyRelease>', lambda event: released_a_key(event))

    # --------------------------------------------------------------------
    # To bind a particular key, simply specify the key (see below).
    #
    # WARNING: If you bind multiple functions to the same widget and
    # event, various things can happen (see your instructor or the link
    # in the comment at the top of this module if you need details).
    #
    # For an ordinary 102-key PC-style keyboard, the special keys are
    # Cancel (the Break key), BackSpace, Tab, Return(the Enter key),
    # Shift_L (any Shift key), Control_L (any Control key),
    # Alt_L (any Alt key), Pause, Caps_Lock, Escape, Prior (Page Up),
    # Next (Page Down), End, Home, Left, Up, Right, Down, Print, Insert,
    # Delete, F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12,
    # Num_Lock, and Scroll_Lock.
    # For other key names, see Section 30.5 in the document referenced
    # at the top of this module, and also perhaps Table 7.1 of
    #   www.pythonware.com/library/tkinter/introduction/events-and-bindings.htm
    # --------------------------------------------------------------------------
    root.bind_all('<Key-L>', lambda event: go_left(event))
    root.bind_all('<Key-R>', lambda event: go_right(event))
    root.bind_all('<Key-r>', lambda event: go_right(event))
    root.bind_all('<Key-space>', lambda event: spin(event))

    root.mainloop()


def pressed_a_key(event):
    # Notice how you can find out the key that was pressed.
    print('You pressed the', event.keysym, 'key')


def released_a_key(event):
    print('You released the', event.keysym, 'key')


def go_left(event):
    print('You pressed the ' + event.keysym + ' key: ', end='')
    print('Go left!')


def go_left_button():
    print('You clicked the Left button: ', end='')
    print('Go left!')


def go_right(event=None):
    # Fancier version that allows EITHER key OR button presses.
    # The former provides the event, the latter does not.
    # It is UN-likely that you will want this fancier version.
    # Instead, use the SIMPLER version per   go_left.
    if event is None:
        print('Button press: ', end='')
    else:
        print('You pressed the ' + event.keysym + ' key: ', end='')
    print('Go right!')


def spin(event=None):
    # Fancier version, see comment in   go_right.
    if event is None:
        print('Button press: ', end='')
    else:
        print('You pressed the ' + event.keysym + ' key: ', end='')
    print('Spin!')


"""
Example showing for tkinter and ttk how to:
  -- 1. BIND callback functions (event-handlers) to Events.
  -- 2. RESPOND to Events.
  -- 3. Associate a WIDGET with the EVENT (and its callback function).
In particular, this example shows how to bind the RETURN Event
to different Entry boxes.
There is LOTS more you can do with Events beyond what is shown here.
See the previous module for more, and for all (or at least most) of the
details, see Section 30 of:
  tkinterReference-NewMexicoTech.pdf
in the Graphics section of the Resources web page for this course.
That document is also available in html form at:
  http://infohost.nmt.edu/tcc/help/pubs/tkinter/events.html
Authors: David Mutchler and his colleagues
         at Rose-Hulman Institute of Technology.
"""

import tkinter
from tkinter import ttk


class Data(object):
    def __init__(self):
        self.number = 0
        self.entry_box1 = None
        self.entry_box2 = None
        self.number_label = None


def main6():
    data = Data()

    root = tkinter.Tk()

    main_frame = ttk.Frame(root, padding=20)
    main_frame.grid()

    intro = 'This example shows how keys can be associated\n' \
            + 'with widgets.  The widget must have the "focus"\n' \
            + 'for its event to fire.\n\n' \
            + 'In this example, the <Return> (Enter key) event\n' \
            + 'is associated with each of the 2 Entry boxes,\n' \
            + 'and the u and d keys and mouse press are associated\n' \
            + 'with the button.\n\n' \
            + 'Try the u and d keys, with and without the button having\n' \
            + 'the focus.  Try entering numbers in the Entry boxes\n' \
            + 'with and without pressing the Enter key.\n'
    intro_label = ttk.Label(main_frame, text=intro)
    intro_label.grid()

    number_text = 'The number is {}'.format(data.number)
    number_label = ttk.Label(main_frame, text=number_text)
    number_label.grid()
    data.number_label = number_label

    # --------------------------------------------------------------------
    # In the previous module, you saw   bind_all   which binds the Event
    # to ALL the widgets on the root.  If you want the callback to occur
    # only when a certain Widget has the "focus" (and the Event occurs),
    # use   bind   (not bind_all), per the following examples:
    # --------------------------------------------------------------------

    entry1 = ttk.Entry(main_frame, width=4)
    entry1.grid()
    entry1.bind('<Return>', lambda event: callback1(event, data))
    data.entry_box1 = entry1

    entry2 = ttk.Entry(main_frame, width=4)
    entry2.grid()
    entry2.bind('<Return>', lambda event: callback2(event, data))
    data.entry_box2 = entry2

    # --------------------------------------------------------------------
    # You can bind Events to Buttons (and any other Widget).  So the
    # first   button.bind   below shows an alternative to ['command'].
    # --------------------------------------------------------------------

    button_text = 'Use the TAB key to give me the "focus",'
    button_text = button_text + '\n then press the u or d key'
    button = ttk.Button(main_frame, text=button_text)
    button.grid()

    button.bind('<Button-1>', lambda event: callback3(event, data))
    button.bind('<Key-u>', lambda event: callback3(event, data))
    button.bind('<Key-d>', lambda event: callback3(event, data))

    root.mainloop()


def callback1(event, data):
    """
    Increases the number in the given Data object by the value
    of the Entry box bound to the given Event.
    """
    widget = event.widget
    number_in_entry_box = int(widget.get())
    print('This is callback1, which uses Widget: ' + str(widget))
    data.number = data.number + number_in_entry_box

    print('  The number is now ' + str(data.number))
    data.number_label['text'] = 'The number is {}'.format(data.number)


def callback2(event, data):
    """
    Decreases the number in the given Data object by the value
    of the Entry box bound to the given Event.
    """
    widget = event.widget
    number_in_entry_box = int(widget.get())
    print('This is callback2, which uses Widget: ' + str(widget))
    data.number = data.number - number_in_entry_box

    print('  The number is now ' + str(data.number))
    data.number_label['text'] = 'The number is {}'.format(data.number)


def callback3(event, data):
    """
    Increments or decrements the number in the given Data object
    depending on the given Event.
    """
    print('hello')
    if event.type == '2':  # 2 is the KEY type in Windows, it seems
        if event.keysym == 'u':
            print('u key was pressed while the button had focus')
            data.number = data.number + 1
        elif event.keysym == 'd':
            print('d key was pressed while the button had focus')
            data.number = data.number - 1
        else:
            print('Unexpected - key ' + event.keysym + ' was pressed.')
    elif event.type == '4':  # 4 is the BUTTON type in Windows, it seems
        print('button was pressed')
        data.number = data.number + 1  # So mouse press is same as u key.
    else:
        print('Unexpected - event type ' + event.type + ' occurred.')

    print('  The number is now ' + str(data.number))
    data.number_label['text'] = 'The number is {}'.format(data.number)


"""
Example showing for tkinter and ttk how to:
  -- 1. Make a menubar with menu's
  -- 2. Put menu items on the menu's.
  -- 3. Establish callback functions for the menu items, that is,
        functions that are called when a menu item is selected.
Authors: David Mutchler and his colleagues
         at Rose-Hulman Institute of Technology.
"""

import tkinter
from tkinter import ttk


class Data(object):
    def __init__(self):
        self.number = 0
        self.number_label = None


def main7():
    data = Data()

    root = tkinter.Tk()

    main_frame = ttk.Frame(root, padding=50)
    main_frame.grid()

    label_text = 'The number is ' + str(data.number)
    label = ttk.Label(main_frame, text=label_text)
    label.grid()
    data.number_label = label

    # The default is for menus to be "tear-off" -- they can be dragged
    # off the menubar.  Use whichever style best suits your GUI.
    root.option_add('*tearOff', False)

    # Step 1:  Make the menu bar
    menubar = tkinter.Menu(root)
    root['menu'] = menubar

    # Step 2:  Make the pull-down menu's on the menu bar.
    change_menu = tkinter.Menu(menubar)
    menubar.add_cascade(menu=change_menu, label='ChangeIt')

    show_menu = tkinter.Menu(menubar)
    menubar.add_cascade(menu=show_menu, label='ShowIt')

    # Step 3:  Make menu items for each menu on the menu bar.
    # Bind callbacks using lambda, as we have seen elsewhere,
    # but this time with a    command=...   optional argument supplied.
    change_menu.add_command(label='Increase the number',
                            command=lambda: increase_number(data, 1))

    change_menu.add_command(label='Decrease the number',
                            command=lambda: increase_number(data, -1))

    show_menu.add_command(label='Show it in red',
                          command=lambda: show(data, 'red'))

    show_menu.add_command(label='Show it in yellow',
                          command=lambda: show(data, 'yellow'))

    root.mainloop()


def increase_number(data, amount):
    """
    Increases the number in the given Data object by the given amount
    and updates the Label in the given Data object that displays
    the number.
    """
    data.number = data.number + amount
    new_text = 'The number is {}'.format(data.number)
    data.number_label['text'] = new_text


def show(data, color):
    new_text = 'The number is {}'.format(data.number)
    data.number_label['text'] = new_text
    data.number_label['background'] = color


"""
Example showing for tkinter and ttk:
  -- ttk.Checkbutton
  -- ttk.Radiobutton
  -- Using tkinter's StringVar, IntVar, DoubleVar to track changes
Authors: David Mutchler and his colleagues
         at Rose-Hulman Institute of Technology.
"""

import tkinter
from tkinter import ttk
import time


def main8():
    # Thus usual root and main Frame.
    root = tkinter.Tk()
    mainframe = ttk.Frame(root, padding=20)
    mainframe.grid()

    # Checkbutton's and Radiobutton's have their own labels.
    checkbutton = ttk.Checkbutton(mainframe, text='Robots rule!')

    # Radiobutton's. We often put them onto a sub-frame,
    # to group them visually.  The 'value' identifies which is selected.
    radio_frame = ttk.Frame(mainframe, borderwidth=10, relief='groove')
    radio1 = ttk.Radiobutton(radio_frame, text='Peter Pevensie',
                             value='peter')
    radio2 = ttk.Radiobutton(radio_frame, text='Susan Pevensie',
                             value='susan')
    radio3 = ttk.Radiobutton(radio_frame, text='Edmund Pevensie',
                             value='edmund')
    radio4 = ttk.Radiobutton(radio_frame, text='Lucy Pevensie',
                             value='lucy')

    # This Button will show how it can interact with other widgets.
    button = ttk.Button(mainframe, text='Reset the other widgets')

    # Checkbutton's and Radiobutton's can have an "observer" variable
    # that is bound to the state of the Checkbutton / Radiobutton.
    checkbutton_observer = tkinter.StringVar()
    checkbutton['variable'] = checkbutton_observer

    radio_observer = tkinter.StringVar()
    for radio in [radio1, radio2, radio3, radio4]:
        radio['variable'] = radio_observer  # They all need the SAME observer

    # Bind callbacks using 'command' and lambda, as we have seen elsewhere.
    checkbutton['command'] = lambda: checkbutton_changed(checkbutton_observer)

    for radio in [radio1, radio2, radio3, radio4]:
        radio['command'] = lambda: radiobutton_changed(radio_observer)

    button['command'] = lambda: button_pressed(checkbutton_observer,
                                               radio_observer)

    # Layout the widgets (here, in a row with padding between them).
    # You can see more on layout in a subsequent example.
    c = 0
    for widget in [checkbutton, radio_frame, button]:
        widget.grid(row=0, column=c, padx=20)
        c = c + 1

    for radio in [radio1, radio2, radio3, radio4]:
        radio.grid(sticky='w')

    root.mainloop()


def checkbutton_changed(checkbutton_observer):
    print('The checkbutton changed to', checkbutton_observer.get())


def radiobutton_changed(radiobutton_observer):
    print('The radiobutton changed to', radiobutton_observer.get())


def button_pressed(checkbutton_observer, radiobutton_observer):
    print('After 2 seconds, I will toggle the Checkbutton')
    print('and reset the radiobutton to Peter\'s.')
    time.sleep(2)

    if checkbutton_observer.get() == '1':
        checkbutton_observer.set('0')
    else:
        checkbutton_observer.set('1')

    radiobutton_observer.set('peter')

import tkinter as tk


def main9():

    ws = Tk() # create a window
    ws.title('my window') # define window title
    ws.geometry('200x200') # define window size

    # create a label
    l = Label(ws, bg='green', width=20, text='') 
    l.pack()

    counter = 0

    # Create menu bar
    def do_job():
        global counter
        l.config(text=f'Do {str(counter)}')
        counter += 1

    menubar = tk.Menu(ws)

    # --------------- file menu ------------------
    filemenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='File', menu=filemenu)

    filemenu.add_command(label='New', command=do_job)
    filemenu.add_command(label='Open', command=do_job)
    filemenu.add_command(label='Save', command=do_job)
    filemenu.add_command(label='Print', command=do_job)
    filemenu.add_separator()
    filemenu.add_command(label='Exit', command=ws.quit)

    # --------------- edit menu ------------------
    editmenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Edit', menu=editmenu)

    editmenu.add_command(label='Cut', command=do_job)
    editmenu.add_command(label='Copy', command=do_job)
    editmenu.add_command(label='Paste', command=do_job)
    editmenu.add_separator()

    # --------------- sub menu ------------------
    submenu = tk.Menu(filemenu, tearoff=0)
    filemenu.add_cascade(label='Import', menu=submenu, underline=0) 
    submenu.add_command(label='Submenu1', command=do_job)

    # Show menubar on window
    ws.config(menu=menubar)

    ws.mainloop()



# ----------------------------------------------------------------------
# Calls  main  to start the ball rolling.
# ----------------------------------------------------------------------
main4()
