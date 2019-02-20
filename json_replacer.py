import os
import json
import string
from tkinter import filedialog, simpledialog
from tkinter import *


class CsvImporter(object):
    def __init__(self):
        self.csv_data = None
        self.languages = []

    def import_csv(self, csv_filename):
        with open(csv_filename, 'r') as file:
            self.csv_data = {}
            for key, line in enumerate(file):
                # Create list of line item.
                line_items = [x.strip() for x in line.split(',')]

                # Header row?
                if key == 0:
                    # Create dictionaries for each language, except the first.
                    self.languages = line_items[1:]
                    for language in self.languages:
                        self.csv_data[language] = {}

                else:
                    # Populate each language's dictionary.
                    for key, language in enumerate(self.languages):
                        try:
                            # Key from first column, value from next.
                            self.csv_data[language].update({
                                line_items[0]: line_items[key + 1]
                            })
                        except IndexError:
                            # Sometimes, no item is expected.
                            pass
        return self.csv_data


class JsonEditor(object):
    def import_json(self, json_filename):
        # Bring JSON in as an object.
        with open(json_filename) as file:
            json_data = json.load(file)
        return json_data

    def export_new_json(self, output_filename, json_data):
        # Save the JSON object as a file.
        f = open(output_filename, "w")
        json_data = json.dumps(json_data)
        f.write(json_data)
        f.close()
        return

    def update_json(self, input_json, target_key, target_value, update_value):
        # Duplicate input_json for modification.
        output_json = input_json

        if isinstance(input_json, dict):
            # Loop through dictionary, searching for target_key, target_value
            # and update output_json if there is an update_value
            for key, value in input_json.items():
                if key == target_key:
                    if target_value == value:
                        if update_value:
                            output_json[key] = update_value
                # If we run into a list or another dictionary, recurse.
                self.update_json(input_json[key], target_key, target_value, update_value)
        elif isinstance(input_json, list):
            # Loop through list, searching for lists and dictionaries.
            for entity in input_json:
                # Recurse through any new list or dictionary.
                self.update_json(entity, target_key, target_value, update_value)
        return output_json

if __name__ == '__main__':
    root = Tk()

    root.csv_filename = filedialog.askopenfilename(
        title="Select CSV file with translations",
        filetypes=(("CSV Files", "*.csv"),)
        )

    root.json_filename = filedialog.askopenfilename(
        title="Select master JSON file to build tranlated JSON files",
        filetypes=(("JSON Files","*.json"),("All Files", "*.*"))
    )

    target_key = simpledialog.askstring(
    "Input",
    "What is the target key for the values we are replacing?",
    initialvalue="title"
    )

    base_output_filename = simpledialog.askstring(
    "Input",
    "What would you like the base file to be named?"
    )

    # Import CSV.
    csv = CsvImporter()
    csv_data = csv.import_csv(root.csv_filename)

    # Import JSON.
    make_json = JsonEditor()

    # Make changes per language.
    for language in csv_data:
        # Edit JSON.
        input_json = make_json.import_json(root.json_filename)
        for key, value in csv_data[language].items():
            updated_json = make_json.update_json(input_json, target_key, key, value)

        # Create filename per language.
        language_filename = base_output_filename + "_" + language + ".json"
        made_json = make_json.export_new_json(language_filename, updated_json)

    # Finished.
    print("Success!")
