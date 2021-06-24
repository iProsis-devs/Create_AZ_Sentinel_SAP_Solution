import subprocess, sys
import os

# a Function to Run a Powershell Script that Imports Azure Sentinel Alerts
def import_alerts(subscription, resource_group, workspace):
    envs = "-subscriptionId '" + subscription + "' -resourceGroupName '" + resource_group + "' -workspaceName '" + workspace + "' -ruleExportPath '" + os.getcwd() + "/Alerts'"
    script_path = os.getcwd() + "\exportAzureSentinelRules.ps1"
    p = subprocess.Popen(["powershell.exe", 
                script_path, envs], 
                stdout=sys.stdout)
    p.communicate()