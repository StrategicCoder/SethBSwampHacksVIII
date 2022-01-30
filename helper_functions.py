"""

Various helper functions used during hte program.
Author: Seth Barber
Date January 29-30, 2022
Credits: Got equation for EER and physcial activity coefficints through Juah Andrade in way noted in about.txt


"""
import sqlite3


# Needed global variables for physical activity, provided by Dr. Juan Andrarde
physical_activity = [[1.0, 1.11, 1.25, 1.48],    # Male: sedentary, low active, active, very active
                     [1.0, 1.12, 1.27, 1.45]]    # Female: sedentary, low active, active, very active


def calculate_eer(male, age, activity, weight, height):
    """
    Calculate the estimated energy requirement (EER) based on the given parameters according to
    an equation provided by Juan Andrade

    :param bool male: Boolean flag for whether the individual is male
    :param int age: The age of the individual (in years)
    :param int activity: The activity level of the individual (0, 1, 2, 3, 4)
    :param float weight: The weight of the individual (in kilograms)
    :param float height: The height of the individual (in meters)
    :return: The EER (an integer)
    """
    global physical_activity
    eer = 0
    if male:
        print("weight: ", type(weight))
        print("height: ", type(height))
        print("the active: ", type(physical_activity[0][activity]))
        eer = 662
        eer = eer - 9.53 * age
        eer = eer + physical_activity[0][activity] * (15.91 * weight + 539.6 * height)
    else:
        eer = 354 - 6.91 * age + physical_activity[1][activity] * (9.36 * weight + 726 * height)
    return eer


def make_user(name, age, gender, weight, height, eer):
    """
    Add a user to the database

    :param name: The user's name
    :param age: The user's age
    :param gender: The user's gender
    :param weight: The user's weight
    :param height: The user's height
    :param eer: The user's EER
    :return:
    """

    # Connect to the user info database
    user_info_connection = sqlite3.connect("user_information.sqlite")
    user_info_cursor = user_info_connection.cursor()

    # Connect to the DRI database
    dri_connection = sqlite3.connect("dri.sqlite")
    dri_cursor = dri_connection.cursor()

    insert_statement = """
    INSERT INTO UserInfo (UserName, Age, Weight, Height, EER)
        VALUES (?, ?, ?, ?, ?)
    """

    # Add user
    user_info_cursor.execute(insert_statement, (name, age, weight, height, eer))

    # Get the user's id
    user_info_cursor.execute("SELECT id FROM UserInfo WHERE UserName = ?", (name, ))
    user_id = user_info_cursor.fetchone()[0]

    # Get various data from the DRI and insert it into the PersonalNutrition table for easier use
    ear_select = "SELECT [Vitamin D], [Calcium], [Iron] FROM EAR "
    rda_select = "SELECT [Sodium], [Vitamin D], [Calcium], [Iron], [Potassium] FROM RDAorAI "
    ul_select = "SELECT [Sodium], [Vitamin D], [Calcium], [Iron] FROM UL "
    where_clause = f"Where For = \"{gender}\" AND {age} >= StartAge AND {age} <= EndAge;"

    dri_cursor.execute(ear_select + where_clause)
    ear_values = dri_cursor.fetchone()
    dri_cursor.execute(rda_select + where_clause)
    rda_values = dri_cursor.fetchone()
    dri_cursor.execute(ul_select + where_clause)
    ul_values = dri_cursor.fetchone()

    mineral_dri = {"Sodium": (None, rda_values[0], ul_values[0]),
                   "Vitamin D": (ear_values[0], rda_values[1], ul_values[1]),
                   "Calcium":(ear_values[1], rda_values[2], ul_values[2]),
                   "Iron": (ear_values[2], rda_values[3], ul_values[3]),
                   "Potassium": (None, rda_values[4], None)}

    for key, values in mineral_dri.items():
        insert_statement = """
        INSERT INTO PersonalNutrition (UserID, Nutrient, EAR, RDA, UL)
            VALUES (?, ?, ?, ?, ?)
        """

        user_info_cursor.execute(insert_statement, (user_id, key, values[0], values[1], values[2]))

    # Commit and close
    user_info_connection.commit()
    user_info_connection.close()

    dri_connection.close()
