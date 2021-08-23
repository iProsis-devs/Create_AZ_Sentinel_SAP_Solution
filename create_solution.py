import create_template as ct
import create_ui_definition as cud
import Alerts.fix_id_script as fis
import shutil
import os
from termcolor import colored

# Constants
directory = "Solution"
zip_file_name = "sap1.2.20.zip"
zip_file = os.getcwd() + "\\" + directory + "\\" + zip_file_name

print(colored("Starting to create Azure Sentinel SAP Solution.", "blue"))
# Remove Alerts ID(Imported Workspace)
fis.fix_id()

# Create mainTemplate.json File
ct.create_template_process()
print(colored("Finished creating mainTemplate.json", "blue"))
# Create createUiDefinition.json File
cud.create_ui_defintion_process()
print(colored("Finished creating createUiDefinition.json", "blue"))

zip_file = os.getcwd() + "\\" + zip_file_name

# Remove old zip file
try:
    os.remove(zip_file)
except FileNotFoundError:
    print(colored("Zip File Not Found", "red"))

# Create a ZIP File from mainTemplate.json and createUiDefenition.json
shutil.make_archive("sap1.2.20", 'zip', directory)
print(colored("Finished creating "+zip_file, "blue"))
