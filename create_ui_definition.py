import json
import os


def create_ui_defintion_process():
    # Constants
    alerts_source_file_name = "\Alerts\Scheduled_no_id.json"
    ui_def_file_name = "\createUiDefinition.json"
    ab_path = os.getcwd()
    wb_directory = "Workbooks"
    wb_desc_path = "Watchlists\\WatchlistsDesc.json"
    solution_directory = "\\Solution\\"
    alerts_file_path = ab_path + alerts_source_file_name
    ui_def_path = ab_path + ui_def_file_name
    fixed_output_file_path = ab_path + solution_directory + ui_def_file_name

    # Load Base File
    with open(ui_def_path, 'rb') as data_file:
        ui_def = json.load(data_file)  # load the json file'

    workbooks = []
    for file in os.listdir(wb_directory):
        workbooks.append(file[:len(file)-5])

    wb_len = range(1, len(workbooks)+1)

    alert_by_name = {}
    with open(alerts_file_path, 'rb') as data_file:
        alerts = json.load(data_file)  # load the json file

    for element in alerts:
        name = element.get("DisplayName")
        alert_by_name[name] = element.get("Description")

    alert_len = range(1, len(alerts)+1)

    # Load Base File
    with open(wb_desc_path, 'rb') as data_file:
        desc_by_watchlist = json.load(data_file)  # load the json file
    
    wl_len = range(1, len(desc_by_watchlist)+1)

    # Edit the relevant section
    params = ui_def.get("parameters")
    outputs = params.get("outputs")
    steps = params.get("steps")
    for step in steps:
        if step.get("name") == "workbooks":
            elements = step.get("elements")
            for workbook, i in zip(workbooks, wb_len):
                wb_elements =  {
                                "name": "workbook"+str(i),
                                "type": "Microsoft.Common.Section",
                                "label": workbook,
                                "elements": [
                                    {
                                        "name": "workbook"+str(i)+"-text",
                                        "type": "Microsoft.Common.TextBlock",
                                        "options": {
                                            "text": "The Azure Sentinel SAP application layer Logs connector is integral part of Azure Sentinel Continuous Threat Monitoring for SAP Solution."
                                        }
                                    },
                                    {
                                        "name": "workbook"+str(i)+"-name",
                                        "type": "Microsoft.Common.TextBox",
                                        "label": "Display Name",
                                        "defaultValue": workbook,
                                        "toolTip": "Display name for the workbook.",
                                        "constraints": {
                                            "required": True,
                                            "regex": "[a-z0-9A-Z]{1,256}$",
                                            "validationMessage": "Please enter a workbook name"
                                        }
                                    }
                                ]
                            }
                elements.append(wb_elements)
        if step.get("name") == "analytics":
            elements = step.get("elements")
            for alert, i in zip(alert_by_name ,alert_len):
                alert_element = {
                        "name": "analytic"+str(i),
                        "type": "Microsoft.Common.Section",
                        "label": alert,
                        "elements": [
                            {
                                "name": "analytic"+str(i)+"-text",
                                "type": "Microsoft.Common.TextBlock",
                                "options": {
                                    "text": alert_by_name[alert]
                                }
                            }
                        ]
                    }
                elements.append(alert_element)
        if step.get("name") == "watchlists":
            elements = step.get("elements")
            for watchlist, i in zip(desc_by_watchlist ,wl_len):
                watchlist_element = {
                        "name": "watchlist" + str(i),
                        "type": "Microsoft.Common.Section",
                        "label": watchlist,
                        "elements": [
                            {
                                "name": "watchlist"+str(i)+"-text",
                                "type": "Microsoft.Common.TextBlock",
                                "options": {
                                    "text": desc_by_watchlist[watchlist]
                                }
                            }
                        ]
                    }
                elements.append(watchlist_element)

    for i in wb_len:
        outputs["workbook"+str(i)+"-name"] = "[steps('workbooks').workbook"+str(i)+".workbook"+str(i)+"-name]"

    # Write to file
    with open(fixed_output_file_path, 'w') as f:
        json.dump(ui_def, f, indent=4)

        
        