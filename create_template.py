from datetime import time
import json
import os
import pandas as pd


def parse_time(time_parameter):
    parsed = "PT"
    if time_parameter["Days"] > 0:
        parsed += str(time_parameter["Days"]) + "D"
    if time_parameter["Hours"] > 0:
        parsed += str(time_parameter["Hours"]) + "H"
    if time_parameter["Minutes"] > 0:
        parsed += str(time_parameter["Minutes"]) + "M"
    return parsed

    


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
                    "serializedData": json.dumps(workbook_by_name[workbook], indent=4),
                    "version": "1.0",
                    "sourceId": "[variables('_workbook-source')]",
                    "category": "sentinel"
                }
            }
        resources.append(workbook_template)


    # Add Alerts to template
    with open(alerts_file_path, 'rb') as data_file:
        alerts = json.load(data_file)  # load the json file

    alert_by_name = {}
    for element in alerts:
        name = element.get("DisplayName")
        alert_by_name[name] = element

    alerts_num = range(1, len(alert_by_name)+1)
    for alert, i in zip(alert_by_name,alerts_num):
        analytic_param = {
                "type": "string",
                "defaultValue": "[newGuid()]",
                "minLength": 1,
                "metadata": {
                    "description": "Unique id for the scheduled alert rule"
                }
            }
        param["analytic" + str(i) + "-id"] = analytic_param
        queryFrequency = parse_time(alert_by_name[alert]["QueryFrequency"])
        queryPeriod = parse_time(alert_by_name[alert]["QueryPeriod"])
        suppressionDuration = parse_time(alert_by_name[alert]["SuppressionDuration"])
        if alert_by_name[alert]["TriggerOperator"] == 0:
            triggerOperator = "GreaterThan"
        else:
            triggerOperator = "EqualTo"
        alert_template = {
                "type": "Microsoft.OperationalInsights/workspaces/providers/alertRules",
                "name": "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',parameters('analytic" + str(i) +"-id'))]",
                "apiVersion": "2020-01-01",
                "kind": "Scheduled",
                "location": "[parameters('workspace-location')]",
                "properties": {
                    "description": alert_by_name[alert]["Description"],
                    "displayName": alert,
                    "enabled":  False,
                    "query": alert_by_name[alert]["Query"],
                    "queryFrequency": queryFrequency,
                    "queryPeriod": queryPeriod,
                    "severity": alert_by_name[alert]["Severity"],
                    "suppressionDuration": suppressionDuration,
                    "suppressionEnabled": alert_by_name[alert]["SuppressionEnabled"],
                    "triggerOperator": triggerOperator,
                    "triggerThreshold": alert_by_name[alert]["TriggerThreshold"],
                }
            }
        if alert_by_name[alert]["Tactics"] is not None:
            alert_template["properties"]["tactics"] = alert_by_name[alert]["Tactics"]
        resources.append(alert_template)

    
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
        param["watchlist" + str(i) + "-id"] = wl_param
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
            for i in range(len(headers)):
                if i != 0:
                    watch_as_content += ","
                watch_as_content += str(row[i])
            watch_as_content += "\n"

        watchlist_template = {
                "type": "Microsoft.OperationalInsights/workspaces/providers/Watchlists",
                "name": "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/','" + watchlist + "')]",
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
