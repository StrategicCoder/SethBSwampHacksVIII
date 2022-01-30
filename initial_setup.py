"""

Used for when the user is new.

"""
import sqlite3
from tkinter import *
import helper_functions


class GetBasicInformation(Tk):
    def __init__(self, user_as_list):
        """
        Create the first user for the program.

        :param list user_as_list: Allows the user to be assigned outside of a primitive (zyBooks)
        """
        super(GetBasicInformation, self).__init__()
        self.user_as_list = user_as_list

        heading_font = ("Cambria", 18)
        subheading = ("Cambria", 16)
        smaller_font = ("Garamond", 15)

        bg_color = "#A0CE17"
        canvas_bg = "#F0FAD3"
        button_bg = "#88AE13"

        self.configure(bg=bg_color)
        Label(self, text="Welcome to Dietia",
              font=("Old English Text MT", 50), bg=button_bg).grid(columnspan=2, ipadx=18)
        Label(self, text="We need some basic information about you.",
              bg=bg_color, font=heading_font).grid(columnspan=2)

        # Get name
        Label(self, text="What is your name?", bg=bg_color, font=smaller_font).grid(row=2, column=0)
        username = Entry(self, bg=canvas_bg, font=smaller_font)
        username.grid(row=2, column=1)

        # Get gender
        Label(self, text="What is your gender?", bg=bg_color, font=smaller_font).grid(row=3, column=0)
        gender = StringVar(self, value="Male", name="gender_var")
        rframe = Frame(self, bg=bg_color)
        rframe.grid(row=3, column=1)
        Radiobutton(rframe, value="Male", text="Male", variable=gender,
                    bg=bg_color, font=smaller_font).pack(side=LEFT)
        Radiobutton(rframe, value="Female", text="Female", variable=gender,
                    bg=bg_color, font=smaller_font).pack(side=LEFT)

        # Get age
        Label(self, text="How old are you (years)?", bg=bg_color, font=smaller_font).grid(row=5, column=0)
        age = Entry(self, bg=canvas_bg, font=smaller_font)
        age.grid(row=5, column=1)

        # Get weight
        Label(self, text="What is your weight (lbs)?", bg=bg_color, font=smaller_font).grid(row=6, column=0)
        weight = Entry(self, bg=canvas_bg, font=smaller_font)
        weight.grid(row=6, column=1)

        # Get height
        Label(self, text="What is your height in feet?", bg=bg_color, font=smaller_font).grid(row=7, column=0)
        height = Entry(self, bg=canvas_bg, font=smaller_font)
        height.grid(row=7, column=1)

        # Get physical activity
        Label(self, text="How would you rate your physical activity?", bg=bg_color,
              font=smaller_font).grid(row=8, columnspan=2, sticky='w')
        physical_activity = IntVar(self, value=0, name="activity_var")

        physics = ["Not active",
                   "A little active",
                   "Moderately active",
                   "Very active"]

        physics_frame = Frame(self, bg=bg_color)
        physics_frame.grid(columnspan=2, padx=40)
        for i in range(len(physics)):
            radio = Radiobutton(physics_frame, text=physics[i], value=i, variable="activity_var",
                                bg=bg_color, font=smaller_font)
            radio.grid(row=(i // 2), column=i % 2, sticky='w')

        self.ordered_entries = [username, gender, age, weight, height, physical_activity]

        # Submit
        Button(self, text="Done!", font=smaller_font,
               command=lambda: self.do_tasks(*[item.get() for item in self.ordered_entries]),
               bg=button_bg).grid(columnspan=2)

    def do_tasks(self, name, gender, age, weight, height, activity):
        # Calculate eer, and make user
        bool_gender = True if gender == "Male" else False
        age = int(age)
        weight = int(weight)
        activity = int(activity)
        height = float(height)

        eer = helper_functions.calculate_eer(bool_gender, age, activity, weight, height)
        helper_functions.make_user(name, age, gender, weight, height, eer)

        self.user_as_list[0] = name
        self.destroy()


def handle_table_setup():
    """
    This will set up the tables if they are not set up.

    :return: Boolean indicating whether tables were already set up.
    """
    was_set_up = True
    connection = sqlite3.connect("user_information.sqlite")
    cursor = connection.cursor()

    # If the meals table was not created, create it
    try:
        cursor.execute("SELECT COUNT(*) FROM Meals")
    except sqlite3.OperationalError:
        set_up_meals_table(cursor)

    # If personal nutrition not done
    try:
        cursor.execute("SELECT COUNT(*) FROM PersonalNutrition")
    except sqlite3.OperationalError:
        set_up_personal_nutrition(cursor)

    # If there were no users
    try:
        cursor.execute("SELECT COUNT(*) FROM UserInfo")
    except sqlite3.OperationalError:
        set_up_personal_table(cursor)
        was_set_up = False

    connection.commit()

    return was_set_up


def set_up_personal_table(cursor):
    command = """
    CREATE TABLE UserInfo (
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        UserName TEXT,
        Age INT,
        Weight REAL,
        Height REAL,
        EER INT
    )"""
    cursor.execute(command)


def set_up_meals_table(cursor):
    command = """
    CREATE TABLE Meals (
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        UserID INTEGER,
        DayEaten DATE,
        Meal TEXT,
        Calories INT,
        TotalFat INT,
        SatFat INT,
        TransFat INT,
        Cholesterol INT,
        Sodium INT,
        CarbTotal INT,
        DietaryFiber INT,
        TotalSugars INT,
        AddedSugars INT,
        Protein INT,
        VitaminD INT,
        Calcium INT,
        Iron INT,
        Potassium INT
    )
    """
    cursor.execute(command)


def set_up_personal_nutrition(cursor):
    command = """
    CREATE TABLE PersonalNutrition (
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        UserID Integer,
        Nutrient Text,
        EAR REAL,
        RDA REAL,
        UL REAL
    )
    """
    cursor.execute(command)
