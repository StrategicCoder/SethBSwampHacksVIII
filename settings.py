"""

Settings (currently just an about me)

"""
from tkinter import *


class SettingsFrame(Frame):
    def __init__(self, master, **kwargs):
        """
        Make a window for settings. Currently displays the About Me

        :param master: The parent widget
        :param kwargs: Keyword arguments associated with Frame
        """
        super(SettingsFrame, self).__init__(master, **kwargs)

        subheading = ("Cambria", 16)

        bg_color = "#A0CE17"
        canvas_bg = "#F0FAD3"
        button_bg = "#88AE13"

        self.configure(bg=bg_color)

        Label(self, text="About", font=("Old English Text MT", 50), bg=bg_color).grid()

        # Text widget for holding about.txt
        text = Text(self, width=100, height=18, bg=canvas_bg, font=("Garamond", 15))
        fh = open("./about.txt", mode="r")
        text.insert(END, fh.read())
        fh.close()
        text.configure(state="disabled")
        text.grid()

        # Frame for holding commands
        action_frame = Frame(self, bg=bg_color)
        action_frame.grid()
        Button(action_frame, text="Leave", command=self.minimize, font=subheading, bg=button_bg).pack()

    def minimize(self):
        """
        Minimize the window

        :return:
        """
        self.pack_forget()
        self.grid_forget()
