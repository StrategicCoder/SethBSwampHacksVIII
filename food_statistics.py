from tkinter import *
import sqlite3
import datetime


# Data courtesy of Understanding Nutrition
amdr = [[45, 65],  # CHO
        [20, 35],  # Fat
        [10, 35]]  # Protein


class Histogrammer(Canvas):
    def __init__(self, master, **kwargs):
        """
        Superclass that allows for graphing

        :param master: The parent widget
        :param kwargs: keyword arguments associated with Canvas
        """
        super(Histogrammer, self).__init__(master, **kwargs)
        self.data = []
        self.labels = []
        self.colors = []

    def do_graph(self, bar_width=50, spacing=20, base=40, top=20):
        """
        Clears and draw the graph based on the class's data, labels, and colors lists and the
        parameters below

        :param bar_width: The width of the histogram bars
        :param spacing: The spacing between the bars
        :param base: The space between the bottom of the bar and the bottom of the Canvas
        :param top: The space between the top of the Canvas and the highest bar
        :return:
        """
        self.delete("all")
        curr_x = bar_width / 2 + spacing
        use_height = max(self.winfo_height(), self.winfo_reqheight())
        y_scale = (use_height - base - top) / max(self.data)
        for i in range(len(self.data)):
            self.create_text(curr_x, use_height - base + 5, text=self.labels[i])
            self.create_line(curr_x, use_height - base,
                             curr_x, use_height - self.data[i] * y_scale,
                             width=bar_width, fill=self.colors[i])
            self.create_text(curr_x, use_height - self.data[i] * y_scale - 10, text=round(self.data[i], 2))
            curr_x += bar_width + spacing


class ForMacronutrients(Histogrammer):
    def __init__(self, master, user_var, **kwargs):
        """
        Make the macronutrients histogram

        :param master: The parent widget
        :param StringVar user_name:
        """
        super(ForMacronutrients, self).__init__(master, **kwargs)
        self.connection = sqlite3.connect("user_information.sqlite")
        self.cursor = self.connection.cursor()
        self.user_var = user_var
        self.update_values()
        self.do_graph(50, 20)

    def update_values(self):
        # Get the user's id and their eer
        global amdr
        self.cursor.execute("SELECT id FROM UserInfo WHERE UserName = ?", (self.user_var.get(), ))
        user_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT EER FROM UserInfo WHERE id = ?", (user_id, ))
        eer = self.cursor.fetchone()[0]

        # Now, get the Macronutrients for the past week
        last_week = datetime.date.today() - datetime.timedelta(7)
        get_macro = """
        SELECT TotalFat, CarbTotal, Protein FROM Meals WHERE UserID = ? AND DayEaten <= ? AND DayEaten >= ?;
        """
        get_macro = """
                    SELECT SUM(TotalFat), SUM(CarbTotal), SUM(Protein) FROM Meals 
                        WHERE UserID = ? AND DayEaten <= ? AND DayEaten >= ?;
                    """

        self.cursor.execute(get_macro, (1, datetime.date.today(), last_week))

        # If no data, stop the attempt
        try:
            total_fat, total_carb, total_protein = self.cursor.fetchone()
        except TypeError:
            self.connection.close()
            return

        # Now, calculate the calories produced by each
        total_fat_cal = total_fat * 9    # Calculate kcal for the macronutrients
        total_carb_cal = total_carb * 4
        total_protein_cal = total_protein * 4
        total_calories = sum([total_fat_cal, total_carb_cal, total_protein_cal])

        # Get the percentages
        pct_fat = total_fat_cal / total_calories * 100
        pct_carb = total_carb_cal / total_calories * 100
        pct_protein = total_protein_cal / total_calories * 100
        pct_calories = total_calories / eer * 100

        # Make data and colors and labels
        self.data = [pct_calories, pct_carb, pct_fat, pct_protein]
        self.colors = [self.choose_cal_pct_color(pct_calories)]

        for i in range(1, len(self.data)):
            self.colors.append(choose_color_for_macronutrients(pct_carb, *amdr[i - 1]))

        self.labels = ["Calories", "Carb", "Fat", "Protein"]

    @staticmethod
    def choose_cal_pct_color(pct_calories):
        pct_red = abs(100 - pct_calories) / 100
        pct_green = 1 - pct_red
        return "#" + hex(int(255 * pct_red))[2:].zfill(2) + hex(int(255 * pct_green))[2:].zfill(2) + "00"


class ForMicronutrients(Histogrammer):
    def __init__(self, master, user_var, **kwargs):
        """
        Make the Macronutrients (carbohydrates, fats, and proteins) histogram

        :param master: The parent widget
        :param StringVar user_name:
        """
        global amdr
        super(ForMicronutrients, self).__init__(master, **kwargs)
        self.connection = sqlite3.connect("user_information.sqlite")
        self.cursor = self.connection.cursor()
        self.user_var = user_var
        self.update_values()
        self.do_graph(50, 20)

    def update_values(self):
        # Get the user's id and their eer
        self.cursor.execute("SELECT id FROM UserInfo WHERE UserName = ?", (self.user_var.get(), ))
        user_id = self.cursor.fetchone()[0]

        # Get the desired micronutrients for the past week
        last_week = datetime.date.today() - datetime.timedelta(7)
        get_micro = """
                    SELECT SUM(VitaminD), SUM(Sodium), SUM(Potassium), SUM(Iron) FROM Meals 
                        WHERE UserID = ? AND DayEaten <= ? AND DayEaten >= ?;
                    """

        self.cursor.execute(get_micro, (1, datetime.date.today(), last_week))

        # If no data, stop the attempt
        try:
            vitamin_d, sodium, potassium, iron = self.cursor.fetchone()
        except TypeError:
            self.connection.close()
            return

        self.data = [vitamin_d, sodium, potassium, iron]
        for i in range(len(self.data)):
            self.data[i] = self.data[i] / 7                 # Should be a weekly total

        self.colors = []
        # Now, calculate the colors for each of these
        self.labels = ["Vitamin D", "Sodium", "Potassium", "Iron"]
        for i in range(len(self.labels)):
            get_dris = f"""
                SELECT EAR, RDA, UL FROM PersonalNutrition WHERE Nutrient = \"{self.labels[i]}\" and UserID = ?
            """
            self.cursor.execute(get_dris, (user_id, ))
            ear, rda, ul = self.cursor.fetchone()
            self.colors.append(choose_color_for_micronutrients(self.data[i], ear, rda, ul))
            self.data[i] = self.data[i] / rda * 100


class AllNutrients(Frame):
    def __init__(self, master, user_var, **kwargs):
        super(AllNutrients, self).__init__(master, **kwargs)
        Label(self, text="The Nutrients", font=("Old English Text MT", 50)).grid(row=0, columnspan=2)
        heading_font = ("Cambria", 18)

        canvas_bg = "#F0FAD3"
        button_bg = "#88AE13"
        bg_color = "#A0CE17"

        subheading = ("Cambria", 16)

        self.user_var = user_var
        self.configure(bg=bg_color)

        macro_frame = Frame(self, bg=bg_color)
        macro_frame.grid(row=0, column=0)
        Label(macro_frame, text="Macronutrients: % Calorie", font=heading_font, bg=bg_color).pack()
        self.macro_graph = ForMacronutrients(macro_frame, self.user_var, height=500, width=300, bg=canvas_bg)
        self.macro_graph.pack()

        micro_frame = Frame(self, bg=bg_color)
        micro_frame.grid(row=0, column=1)
        Label(micro_frame, text="Micronutrients: % RDA", font=heading_font, bg=bg_color).pack()
        self.micro_graph = ForMicronutrients(micro_frame, self.user_var, height=500, width=300, bg=canvas_bg)
        self.micro_graph.pack()

        action_frame = Frame(self, bg=bg_color)
        action_frame.grid(columnspan=2)
        Button(action_frame, text="Leave", command=self.minimize,
               bg=button_bg, font=subheading).pack(side=LEFT)
        Button(action_frame, text="Refresh", command=self.update_and_graph(),
               bg=button_bg, font=subheading).pack(side=LEFT)

    def update_and_graph(self):
        self.macro_graph.update_values()
        self.micro_graph.update_values()
        self.macro_graph.do_graph()
        self.micro_graph.do_graph()

    def minimize(self):
        self.pack_forget()
        self.grid_forget()


def choose_color_for_macronutrients(actual_value, low_amdr, high_amdr):
    """
    Provide a color between red and green for coloring the macronutrients

    :param actual_value: The actual percentage of calories sourced from the macronurtrient
    :param low_amdr: The low end for the AMDR
    :param high_amdr: The high end for the AMDR
    :return: Hexadecimal color
    """
    if actual_value < low_amdr or actual_value > high_amdr:
        return "#FF0000"

    pct_red = min(abs(actual_value - low_amdr), abs(actual_value - high_amdr)) / (high_amdr - low_amdr)
    pct_green = 1 - pct_red
    return "#" + hex(int(255 * pct_red))[2:].zfill(2) + hex(int(255 * pct_green))[2:].zfill(2) + "00"


def choose_color_for_micronutrients(actual_value, ear, rda, ul):
    """
    Chooses a display color for vitamins and minerals with a given EAR, RDA, and UL

    :param actual_value: The actual intake
    :param ear: The EAR (satisfies 50% of people)
    :param rda: The RDA (satisfies about 98% of people)
    :param ul: The UL (Highest possible consumption without toxicity)
    :return: Hexadecimal color
    """
    if ear is None:   # If no EAR is specified, assume it is zero
        ear = 0

    if ul is None and actual_value > rda:  # If no UL is specified, assume nonexistent
        return "#00FF00"

    elif ul is None and actual_value < rda:  # Do this to avoid an error about ul being None
        to_ear = abs(actual_value - ear)
        to_rda = abs(actual_value - rda)

        scaled_to_ear = to_ear / (to_ear + to_rda)
        scaled_to_rda = to_rda / (to_ear + to_rda)

        red = hex(int(255 * scaled_to_ear))[2:]
        green = hex(int(255 * scaled_to_rda))[2:]

        return "#" + red.zfill(2) + green.zfill(2) + "00"

    if ul is not None and actual_value < ear or actual_value > ul:  # If the value is *out of bounds*, return red
        return "#FF0000"

    elif actual_value < rda:    # Between EAR and RDA
        to_ear = abs(actual_value - ear)
        to_rda = abs(actual_value - rda)

        scaled_to_ear = to_ear / (to_ear + to_rda)
        scaled_to_rda = to_rda / (to_ear + to_rda)

        red = hex(int(255 * scaled_to_ear))[2:]
        green = hex(int(255 * scaled_to_rda))[2:]

    else:                                      # Between RDA and UL
        to_ear = abs(actual_value - ear)
        to_rda = abs(actual_value - rda)

        scaled_to_ear = to_ear / (to_ear + to_rda)
        scaled_to_rda = to_rda / (to_ear + to_rda)

        red = hex(int(255 * scaled_to_ear))[2:]
        green = hex(int(255 * scaled_to_rda))[2:]

    return "#" + red.zfill(2) + green.zfill(2) + "00"
