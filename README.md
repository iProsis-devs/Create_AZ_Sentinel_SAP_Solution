# Create Azure Sentinel SAP Solution

Create Azure Sentinel SAP Solution for marketplace based on alerts, workbooks and watchlists.

Inputs:
1. Import alerts from azure sentinel workspace by subscription, resource group, workspace. (Script requests parameters while running)
2. Watchlists should manually added to the Watchlists folder. <br>
Also need to maintain Watchlists_desc.txt with key-value for Watchlist name and Watchlist description inside Watchlists folder.
3. Workbooks should manually added to the Workbooks folder.

Outputs:
1. In Solution folder: mainTemplate.json and createUiDefinition.json.
2. In Main folder: sap1.2.20.zip (Solution file for marketplace)

Instructions:
1. Run pip install -r requirements.txt to install relevant packages.
2. Run python create_solution.py

