import json
import sys
from pathlib import Path
from termcolor import colored

def fix_id():
    try:
        source_file_name = "Alerts\\Scheduled.json"
        output_file_name = "Alerts\\Scheduled_no_id.json"
        source_file = Path(source_file_name)
        if not source_file_name.endswith(".json"):  # check that its a json file
            raise Exception(source_file_name)
        elif not output_file_name.endswith(".json"):  # check that its a json file
            raise Exception(output_file_name)
        elif not source_file.is_file():  # check that file exists
            raise FileNotFoundError(source_file_name)
    except FileNotFoundError as f:
        print(f, "not found")
        exit(0)
    except Exception as ex:  # if its not a json file, raise exception and print
        print(ex, "is not a json file")
        exit(0)

    with open(source_file_name, 'rb') as data_file:
        data = json.load(data_file)  # load the json file
        data = data.get("resources")

    for element in data:
        element.pop('id', None)  # if the key is "Id", pop it out

    with open(output_file_name, 'w') as data_file:  # create a new json file
        json.dump(data, data_file, indent=4)

    print(colored("Finished fixing ID for alerts.", "blue"))
