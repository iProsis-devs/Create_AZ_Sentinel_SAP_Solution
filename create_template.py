from datetime import time
import json
import os
import pandas as pd

def clean_nones(value):
    if isinstance(value, list):
        return [clean_nones(x) for x in value if x is not None]
    elif isinstance(value, dict):
        return {
            key: clean_nones(val)
            for key, val in value.items()
            if val is not None
        }
    else:
        return value

def create_template_process():
    # Constants
    alerts_source_file_name = "\Alerts\Scheduled_no_id.json"
    template_file_name = "\mainTemplate.json"
    wl_directory = "Watchlists"
    wb_desc_path = "Watchlists\\WatchlistsDesc.json"
    wb_directory = "Workbooks"
    solution_directory = "\\Solution\\"
    ab_path = os.getcwd()
    alerts_file_path = ab_path + alerts_source_file_name
    output_file_path = ab_path + template_file_name
    fixed_output_file_path = ab_path + solution_directory + template_file_name

    # Load Base File
    with open(output_file_path, 'rb') as data_file:
        template = json.load(data_file)  # load the json file

    param = template.get("parameters") # Get parameters section
    resources = template.get("resources") # Get resources section

    # Add Workbooks to template
    workbook_by_name = {}
    for file in os.listdir(wb_directory):
        path = wb_directory + "//" + file
        with open(path, 'rb') as data_file:
            workbook = json.load(data_file)  # load the json file
        workbook_by_name[file[:len(file)-5]] = workbook

    wb_num = range(1, len(workbook_by_name)+1)
    for workbook,i in zip(workbook_by_name,wb_num):
        workbook_id_param = {
                "type": "string",
                "defaultValue": "[newGuid()]",
                "minLength": 1,
                "metadata": {
                    "description": "Unique id for the workbook"
                }
            }
        workbook_name_param ={
                "type": "string",
                "defaultValue": workbook,
                "minLength": 1,
                "metadata": {
                    "description": "Name for the workbook"
                }
            }
        param["workbook" + str(i) + "-id"] = workbook_id_param
        param["workbook" + str(i) + "-name"] = workbook_name_param
        workbook_template =   {
                "type": "Microsoft.Insights/workbooks",
                "name": "[parameters('workbook"+str(i)+"-id')]",
                "location": "[parameters('workspace-location')]",
                "kind": "shared",
                "apiVersion": "2020-02-12",
                "properties": {
                    "displayName": "[concat('Preview - ',parameters('workbook"+str(i)+"-name'), ' - ', parameters('formattedTimeNow'))]",
                    "serializedData": json.dumps(clean_nones(workbook_by_name[workbook].copy()), indent=4),
                    "version": "1.0",
                    "sourceId": "[variables('_workbook-source')]",
                    "category": "sentinel"
                }
            }
        resources.append(workbook_template)


    # Add Alerts to template
    with open(alerts_file_path, 'rb') as data_file:
        alerts = json.load(data_file)  # load the json file



    alerts_num = range(1, len(alerts)+1)
    for alert, i in zip(alerts,alerts_num):
        analytic_param = {
                "type": "string",
                "defaultValue": "[newGuid()]",
                "minLength": 1,
                "metadata": {
                    "description": "Unique id for the scheduled alert rule"
                }
            }
        param[f"analytic{i}-id"] = analytic_param
        alert["name"] = f"[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',parameters('analytic{i}-id'))]"
        prop = alert.get("properties")
        elements_to_remove = []
        for element in prop:
            if prop[element] is None or prop[element] == []:
                elements_to_remove.append(element)
        for element in elements_to_remove:
            prop.pop(element)
        elements_to_remove = []
        group = prop["incidentConfiguration"]["groupingConfiguration"]
        for element in group:
            if group[element] is None or group[element] == []:
                elements_to_remove.append(element)
        for element in elements_to_remove:
            group.pop(element)
        resources.append(alert)

    
    # Load Base File
    with open(wb_desc_path, 'rb') as data_file:
        desc_by_watchlist = json.load(data_file)  # load the json file

    watchlists_by_name = {}
    for file in os.listdir(wl_directory):
        if file.endswith(".csv"):
            path = wl_directory + "//" + file
            watchlist = pd.read_csv(path)
            watchlists_by_name[file[:len(file)-4]] = watchlist

    wl_num = range(1, len(watchlists_by_name)+1)
    for watchlist, i in zip(watchlists_by_name, wl_num):
        wl_param = {
                "type": "string",
                "defaultValue": "[newGuid()]",
                "minLength": 1,
                "metadata": {
                    "description": "Unique id for a watchilst"
                }
            }
        param[f"watchlist{i}-id"] = wl_param
        headers = list(watchlists_by_name[watchlist])

        watch_as_content = ""
        first = True
        for header in headers:
            if first != True:
                watch_as_content += ","
            else:
                first = False
            watch_as_content += header
        watch_as_content += "\n"

        for index, row in watchlists_by_name[watchlist].iterrows():
            for z in range(len(headers)):
                if z != 0:
                    watch_as_content += ","
                watch_as_content += str(row[z])
            watch_as_content += "\n"

        watchlist_template = {
                "type": "Microsoft.OperationalInsights/workspaces/providers/Watchlists",
                "name": f"[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',parameters('watchlist{i}-id'))]",
                "apiVersion": "2021-03-01-preview",
                "properties": {
                    "description": desc_by_watchlist[watchlist],
                    "displayName": watchlist,
                    "source": "CSV",
                    "provider": "Microsoft",
                    "numberOfLinesToSkip": 0,
                    "itemsSearchKey":headers[0],
                    "rawContent": watch_as_content,
                    "contentType": "text/csv"
                }
            }

        resources.append(watchlist_template)
    # Write to file
    with open(fixed_output_file_path, 'w') as f:
        json.dump(template, f, indent=4)
