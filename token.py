## 1.TO BEGIN, PLS HAVE YOUR PROJECT ON GCP TO SET CREDENTIALS--https://developers.google.com/search-ads/v2/first-app
## 2. MAKE SURE TO HAVE SUFFICIENT PERMISSION TO ACCESS DATA 

import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json
import requests
import pandas as pd

# 1.CREATE A PROJECT IN GAP AND GET CREDENTIAL FILE
# 2.GET RIGHT SCOPE (NOTE: YOU COULD USE TWO SCOPES TOGETHER IF NEEDED)

flow = InstalledAppFlow.from_client_secrets_file("credentials.json", 
                                                 scopes= ["https://www.googleapis.com/auth/dfareporting",
                                                         "https://www.googleapis.com/auth/doubleclicksearch"])
                                                  #scopes= ["https://www.googleapis.com/auth/dfareporting"])

# PORT NUMBER MAY NOT ALWAYS AVAILABLE, IF NOT TRY OTHER ONE
flow.run_local_server(port= 3000, prompt="consent")

credentials = flow.credentials
token = credentials.to_json()
# THIS STEP WOULD ASK YOU TO SELECT A GOOGLE ACCOUNT YOU WANT TO ACCESS API
print(token)


both_scopes= json.loads(token)
print(both_scopes) # COVNVERT TOKEN FILE AS DICT AS PYTHON ONLY ACCPET THIS FORMAT

with open('both_scopes.json', 'w') as f:
    json.dump(both_scopes, f, indent= 4,sort_keys=True)# DOWNLOAD TOKEN FILE TO THE SAME PATH SCRIPT RUNS
    
## END*************************************************************************************************************
