from tkinter import *
import datetime
import sqlite3


class MealMaker(Frame):
    def __init__(self, master, user_var, **kwargs):
        """
        Create a Frame that allows the user to add meals to their history

        :param master: The parent widget
        :param StringVar user_var: The user who ate the meal.
        :param kwargs: Keyword arguments associated with Frame
        """
        super(MealMaker, self).__init__(master, **kwargs)              # Call the superclass constructor
        self.connection = sqlite3.connect("user_information.sqlite")   # Connect to the database
        self.cursor = self.connection.cursor()                         # Create a cursor for the database.
        self.user_var = user_var                                       # The user who ate the meal.

        bg_color = "#A0CE17"
        self.configure(bg=bg_color)

        # The following query is for inserting a meal
        self.insert_meal_query = """
        INSERT INTO Meals (
            UserID, DayEaten, Meal, Calories, TotalFat, SatFat, TransFat, Cholesterol, 
            Sodium, CarbTotal, DietaryFiber, TotalSugars, AddedSugars, Protein, 
            VitaminD, Calcium, Iron, Potassium
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # The following list holds the names of the nutrients for display and their units
        self.type_and_measure = [("Calories/Serving", 'Cal.'), ("Total Fat", 'g'), ("Saturated Fat", 'g'),
                                 ("Trans Fat", 'g'), ("Cholesterol", 'mg'), ("Sodium", 'mg'),
                                 ("Total Carbohydrate", 'g'), ("Dietary Fiber", 'g'), ("Total Sugars", 'g'),
                                 ("Added Sugars", 'g'), ("Protein", 'g'), ("Vitamin D", 'mcg'), ("Calcium", 'mg'),
                                 ("Iron", 'mg'), ("Potassium", 'mg')]

        self.current_meal = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]   # Holds currently entered meal
        self.current_meal_labels = []                                       # Hold the labels displaying nutrient
        self.ordered_entries = []                                           # Will hold the entries for a food item

        heading_font = ("Cambria", 18)
        subheading = ("Cambria", 16)
        smaller_font = ("Garamond", 15)

        self.meal_list = ["Breakfast", "Lunch", "Supper", "Other"]          # Allowed meals

        # User chooses which meal this is
        Label(self, text="Enter a Meal", font=("Old English Text MT", 50)).grid(row=0, columnspan=2)

        # Allow user to select which meal it is: Breakfast, Lunch, Supper, or Other
        select_meal_frame = Frame(self)                            # Frame to hold it
        select_meal_frame.grid(row=1, columnspan=2, sticky="nsew")
        self.which_meal = StringVar(select_meal_frame, value='S', name="use_meal")  # A StringVar for the meal

        Label(select_meal_frame, text="Which Meal is This? ",
              font=heading_font).grid(row=0, columnspan=len(self.meal_list), sticky='w')
        # Create and pack the radio buttons
        for i in range(len(self.meal_list)):
            Radiobutton(select_meal_frame, text=self.meal_list[i], font=smaller_font,
                        value=self.meal_list[i][0], variable="use_meal").grid(row=1, column=i+1)

        # The frame for holding the food item.
        self.food_frame = Frame(self)
        self.food_frame.grid(row=2, column=0)

        # Now, allow the user to enter the serving size and the amount the user ate.
        serving_frame = Frame(self.food_frame)
        serving_frame.pack()

        # Serving size and amount eaten
        Label(serving_frame, text="Please enter the serving size and the amount you ate:",
              font=subheading).grid()

        inner_frame = Frame(serving_frame)
        inner_frame.grid(padx=20, sticky='w')
        Label(inner_frame, text="Serving Size: ", font=smaller_font).grid(row=0, column=0, sticky='w')
        self.serving_size = Entry(inner_frame, font=smaller_font)
        self.serving_size.grid(row=0, column=1, sticky='w')
        Label(inner_frame, text="Amount you ate: ", font=smaller_font).grid(row=1, column=0, sticky='w')
        self.amount_eaten = Entry(inner_frame, font=smaller_font)
        self.amount_eaten.grid(row=1, column=1, sticky='w')

        # Allow the user to enter energy and nutrient information
        self.nutrients_frame = Frame(self.food_frame)
        self.nutrients_frame.pack(fill=BOTH)

        # Calorie and nutrient information
        Label(self.nutrients_frame, text="Please enter Calorie and nutrition info:",
              font=subheading).grid(sticky='w')

        entering_frame = Frame(self.nutrients_frame)        # For aesthetic purposes
        entering_frame.grid(sticky='nsew', padx=30)
        for i in range(len(self.type_and_measure)):
            Label(entering_frame, text=self.type_and_measure[i][0],
                  font=smaller_font).grid(row=i + 1, column=0, sticky='w')
            inner_frame = Frame(entering_frame)
            ent = Entry(inner_frame, font=smaller_font)
            ent.pack(side=LEFT, expand=YES, fill=X)
            self.ordered_entries.append(ent)
            Label(inner_frame, text=self.type_and_measure[i][1], font=smaller_font).pack(side=LEFT)
            inner_frame.grid(row=i + 1, column=1, sticky='w')

        # Now, frame for holding the data for the meal:
        self.meal_frame = Frame(self)
        self.meal_frame.grid(row=2, column=1, sticky='nw', padx=40)
        Label(self.meal_frame, text="Total so far:", font=heading_font).grid(row=0, columnspan=2)
        for i in range(len(self.type_and_measure)):
            name = self.type_and_measure[i][0]
            if i == 0:
                name = "Calories"
            Label(self.meal_frame, text=name + ": ", font=smaller_font).grid(row=i + 1, column=0, sticky='w')
            amount_label = Label(self.meal_frame, text=str(self.current_meal[i]) + ' ' + self.type_and_measure[i][1])
            amount_label.configure(font=smaller_font)
            amount_label.grid(row=i + 1, column=1, sticky='w')
            self.current_meal_labels.append(amount_label)

        # Action Frame (buttons for adding meal item and finishing the meal)
        actions_frame = Frame(self)
        actions_frame.grid(column=0, sticky='w', padx=20)
        Button(actions_frame, text="Add Food to Meal", command=self.add_a_food_to_meal, font=subheading).pack(side=LEFT)
        Button(actions_frame, text="Finish Meal", command=self.finish_meal, font=subheading).pack(side=LEFT)
        Button(actions_frame, text="Cancel And Leave", command=self.cancel, font=subheading).pack(side=LEFT)

        # Now, set the background color in all of main's children
        children = self.winfo_children()
        while len(children) > 0:
            new_children = []
            for child in children:
                if isinstance(child, Frame):
                    new_children.extend(child.winfo_children())
                if isinstance(child, Entry):
                    child.configure(bg="#F0FAD3")
                    continue
                if isinstance(child, Button):
                    child.configure(bg="#88AE13")
                    continue
                child.configure(bg=bg_color)
            children = new_children

    def get_user_id(self):
        self.cursor.execute("SELECT id FROM UserInfo WHERE UserName = ?;", (self.user_var.get(),))
        fetched = self.cursor.fetchone()
        return fetched[0]

    def clear_meal(self):
        for i in range(len(self.current_meal)):
            self.current_meal[i] = 0

        for label in self.current_meal_labels:
            label.configure(text="")

        self.serving_size.delete(0, END)
        self.amount_eaten.delete(0, END)

        for entry in self.ordered_entries:
            entry.delete(0, END)

        self.minimize()

    def add_a_meal_for_user(self, user_name, meal, kcal, total_fat, sat_fat,
                            trans_fat, cholesterol, sodium, carb_total, fiber, total_sugars,
                            added_sugars, protein, vitamin_d, calcium, iron, potassium):
        """
        Insert a meal into the table

        :param user_name: The user who ate the meal's name
        :param meal: A letter signifying which meal: B (breakfast), L (lunch), S (supper), O (other)
        :param kcal: The number of Calories consumed in the meal.       (kcal)
        :param total_fat: The total amount of fat consumed.             (grams)
        :param sat_fat: The total amount of saturated fat consumed.     (grams)
        :param trans_fat: The total amount of trans fat consumed.       (grams)
        :param cholesterol: The total amount cholesterol consumed.      (milligrams)
        :param sodium: The total amount of sodium consumed.             (milligrams)
        :param carb_total: The total amount of carbohydrate consumed.   (grams)
        :param fiber: The amount of dietary fiber consumed.             (grams)
        :param total_sugars: The total number of sugars consumed.       (grams)
        :param added_sugars: The total number of added sugars consumed. (grams)
        :param protein: The total amount of protein consumed.           (grams)
        :param vitamin_d: The total amount of vitamin D consumed.       (micrograms)
        :param calcium: The total amount of calcium consumed            (milligrams)
        :param iron: The total amount of iron consumed                  (milligrams)
        :param potassium: The total amount of potassium consumed        (milligrams)
        :return:
        """
        user_id = self.get_user_id()
        day_eaten = datetime.date.today()
        self.cursor.execute(self.insert_meal_query, (user_id, day_eaten, meal, kcal, total_fat, sat_fat,
                            trans_fat, cholesterol, sodium, carb_total, fiber, total_sugars,
                            added_sugars, protein, vitamin_d, calcium, iron, potassium))
        self.connection.commit()

    def finish_meal(self):
        self.type_and_measure = [("Calories/Serving", 'Cal.'), ("Total Fat", 'g'), ("Saturated Fat", 'g'),
                                 ("Trans Fat", 'g'), ("Cholesterol", 'mg'), ("Sodium", 'mg'),
                                 ("Total Carbohydrate", 'g'), ("Dietary Fiber", 'g'), ("Total Sugars", 'g'),
                                 ("Added Sugars", 'g'), ("Protein", 'g'), ("Vitamin D", 'mcg'), ("Calcium", 'mg'),
                                 ("Iron", 'mg'), ("Potassium", 'mg')]
        meal = self.which_meal.get()   # B, L, S, O, for Breakfast, Lunch, Supper, or Other

        # The factor adjusts for when more or less than the serving size was eaten.
        factor = int(self.amount_eaten.get()) / int(self.serving_size.get())

        # Create an argument list for add_a_meal_for_user(...)
        argument_list = [self.user_var.get(), meal]
        for entry in self.ordered_entries:
            argument_list.append(float(entry.get()) * factor)

        # Unpack argument_list and call add_a_meal_for_user
        self.add_a_meal_for_user(*argument_list)
        self.connection.commit()                          # Commit the change

        # Now, by default, clear out the current meal
        self.clear_meal()
        self.minimize()

    def add_a_food_to_meal(self):
        for i in range(len(self.ordered_entries)):
            self.current_meal[i] += float(self.ordered_entries[i].get())
            self.current_meal_labels[i].configure(text=str(self.current_meal[i]) + ' ' + self.type_and_measure[i][1])
        print(self.current_meal)
        self.update()

    def minimize(self):
        self.pack_forget()
        self.grid_forget()

    def cancel(self):
        self.clear_meal()
        self.minimize()



if __name__ == "__main__":
    root = Tk()
    mmake = MealMaker(root, StringVar(value="Seth"))
    mmake.pack()
    mainloop()
