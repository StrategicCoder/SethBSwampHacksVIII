"""

Rough and ready function for formatting text so that it can be made into a csv and
a function for converting the csv into sqlite. I would not reccommend running convert_to_tab_delimit

Credits: Based with ... csv clause off of an example found in the Python 3.7 Documentation

"""
import csv
import sqlite3


def convert_to_tab_delimit(header_string, input_string):
    # A *rough and ready* function for formatting.
    header_row = "For\tStartAge\tEndAge\t"
    unit_row = "Unit\ty\ty\t"
    header_string = header_string.replace("\n", " ").strip()
    header_string = header_string.replace("Life Stage Group", "").strip()   # Slightly format the life stage group
    header_string = header_string.replace(") ", ")\t").split("\t")
    for item in header_string:
        open_paren = item.find("(")
        close_paren = item.find(")")
        header = item[:open_paren].strip()
        unit = item[open_paren + 1 : close_paren]
        header_row += header + "\t"
        unit_row += unit + "\t"

    header_row = header_row.strip() + "\n"
    unit_row = unit_row.strip() + "\n"
    return_string = header_row + unit_row
    prefix = ""
    for line in input_string.split("\n"):
        if line.find(" ") == -1:
            prefix = line.strip()[:-1]          # Removes the plural
            continue

        if prefix != "":
            return_string += prefix + "\t"
        dash_pos = line.find("−")
        y_pos = line.find("y")
        if dash_pos != -1:
            return_string += line[:dash_pos].strip() + '\t' + line[dash_pos + 1: y_pos].strip() + '\t'
        else:
            gt_pos = return_string.find(">")
            return_string += line[gt_pos + 1: y_pos].strip() + '\t120\t'
        return_string += line[y_pos + 1:].strip().replace(' ', '\t') + '\n'
    return return_string


def make_dri_tables(files):
    """
    Create the sqlite DRI tables
    :param list[str] files: The files to add to the table
    :return:
    """
    connection = sqlite3.connect("dri.sqlite")
    cursor = connection.cursor()
    for file in files:
        table_name = file[:-4]
        create_statement = f"CREATE TABLE {table_name}("

        # Followed example in the Python Reference for the csv module
        with open(file, "r") as file_handle:
            reader = csv.reader(file_handle)
            counter = 0
            for row in reader:
                if counter == 0:
                    create_statement += '[' + row[0] + ']' + " TEXT, "
                    for i in range(1, len(row)):
                        create_statement += '[' + row[i] + ']' + " REAL"
                        if i == len(row) - 1:
                            create_statement += ")"
                        else:
                            create_statement += ", "
                    print(create_statement)
                    cursor.execute(create_statement)
                elif counter != 1:
                    insert_statement = f"INSERT INTO {table_name} VALUES (" + "?, " * (len(row) - 1) + "?)"
                    use = [item.strip() if item != "" else None for item in row]
                    cursor.execute(insert_statement, tuple(use))

                counter += 1
    connection.commit()
    connection.close()


if __name__ == '__main__':
    make_dri_tables(["EAR.csv", "RDAorAI.csv", "UL.csv"])
