"""
This file contains the main window necessary for running the program

Title: Diet and Nutrient Tracking
Author: Seth Barber
For: Swamphacks VIII

Credits:
main.py: *Trick* regarding a persistent variable using a list shown in ZyBooks Intro to Programming

Credits:
DRI values: https://www.nal.usda.gov/sites/default/files/fnic_uploads/recommended_intakes_individuals.pdf
AMDR values:Understanding Nutrition, 15th Edition, by Whitney and Rolfes, Cengage.
EER function: https://globalrph.com/medcalcs/estimated-energy-requirement-eer-equation/ c/o Dr. Juan Andrade
CSV info: Python 3.7 Documentation
List trick: Programming Fundamentals 1, ZyBooks, for my COP3502C class

"""

from tkinter import *
import initial_setup
from meal_maker import MealMaker
from food_statistics import AllNutrients
from settings import SettingsFrame


class MainWindow(Frame):
    def __init__(self, master, user_var, **kwargs):
        """
        The main window for the program

        :param master: The parent widget
        :param user_var: The StringVar used for the user's name
        :param kwargs: Keyword arguments for Frame
        """
        super(MainWindow, self).__init__(master, **kwargs)
        self.user_var = user_var

        self.meal_making_frame = MealMaker(self, user_var)
        self.food_stats_frame = AllNutrients(self, user_var)
        self.settings_frame = SettingsFrame(self)

        self.home_frame = Frame(self)
        self.home_frame.grid(sticky=NSEW, row=0, column=0)

        btn_width, btn_height = 25, 30
        font = ("Constantia", 15)

        # Images (so they are not garbage collected
        self.settings_button = PhotoImage(file="./settings_button.png")
        self.statistic_button = PhotoImage(file="./statistic_button.png", master=self)
        self.add_meal_button = PhotoImage(file="./add_meal_button.png", master=self)

        # Buttons
        Button(self.home_frame, image=self.add_meal_button, command=self.add_meal,
               width=self.add_meal_button.width(),
               height=self.add_meal_button.height()).pack(expand=YES, fill=BOTH, side=LEFT)
        Button(self.home_frame, image=self.statistic_button, command=self.get_stats,
               width=self.statistic_button.width(),
               height=self.statistic_button.height()).pack(side=LEFT)
        Button(self.home_frame, image=self.settings_button, command=self.open_settings,
               width=self.settings_button.width(),
               height=self.settings_button.height()).pack(side=LEFT)

    # The following functions show the various windows
    def add_meal(self):
        self.meal_making_frame.grid(row=0, column=0)
        self.meal_making_frame.tkraise()

    def get_stats(self):
        self.food_stats_frame.grid(row=0, column=0)
        self.food_stats_frame.tkraise()

    def open_settings(self):
        self.settings_frame.grid(row=0, column=0)
        self.settings_frame.tkraise()

    def make_sticky(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


class SignInWindow(Tk):
    def __init__(self, user_as_list):
        """
        Window for signing in
        :param user_as_list: List holding user. Trick learned from zyBooks
        """
        super(SignInWindow, self).__init__()
        subheading = ("Cambria", 16)

        self.configure(bg="light blue")
        self.user_as_list = user_as_list

        self.welcome = PhotoImage(file="./welcome_diatea.png", master=self)
        Label(self, image=self.welcome, width=self.welcome.width(), height=self.welcome.height()).grid()
        Label(self, text="Please enter your username: ", bg="light blue", font=subheading).grid(sticky="nsew")
        self.ent = Entry(self, bg="white", font=subheading)
        self.ent.grid()
        Button(self, text="Submit", command=self.sign_in, bg="light green", font=subheading).grid()

    def sign_in(self):
        self.user_as_list[0] = self.ent.get()
        self.destroy()


if __name__ == '__main__':
    # First, check if user has ever set up
    user = [None, ]                                     # Temporarily store user name in a list (trick from zyBooks)
    was_set_up = initial_setup.handle_table_setup()     # Will set up the databases if necessary
    if not was_set_up:                                  # If it was not set up, create a user
        initial_setup.GetBasicInformation(user).wait_window()

    if user[0] is None:   # That is, a user was already created
        SignInWindow(user).wait_window()
    if user[0] is None:
        quit()

    root = Tk()
    user_variable = StringVar(root, value=user[0], name="global_user")
    root.title("Track your Food!")
    frame = MainWindow(root, user_variable)
    frame.pack(expand=YES, fill=BOTH)
    mainloop()
