import json
import time
import os.path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pandas as pd


SCOPES = ["https://www.googleapis.com/auth/doubleclicksearch"] # YOU COULD SPECIFY THE SCOPE 

# 1. TOKEN FILE CAN BE ACHIEVED BY TOKEN.PY
# 2. CREDENTIAL NEEDS TO BE CREATED IN GAP
def get_creds():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=3000)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds  
    
    
def build_service(name, version, creds):
    return build(name, version, credentials=creds)

# SA360 ONLY SUPPORT ASYC METHOD TO GET REPORT, SO WE NEED TO DOWNLOAD IT TO GET ACTUAL DATA
def generate_report(
    service,
    agency_id,
    advertiser_id,
    report_type,
    columns,
    time_range,
    download_format,
    max_rows_per_file,
    statistics_currency
):
    request = service.reports().request(
        body={
            "reportScope": {
                "agencyId": '20700000001302897',
                "advertiserId": '21700000001688149'
            },
            "reportType": 'conversion',
            "columns": [
                { "columnName": "status"},
                { "columnName": "conversionId"},
                { "columnName": "advertiser" },
                { "columnName": "conversionRevenue"},
                { "columnName": "floodlightEventRequestString"}
                 ],
            "timeRange": {
      "startDate": "2021-08-15",
      "endDate": "2021-08-15"
            },
            "downloadFormat": 'csv',
            "maxRowsPerFile": 6000000,
            "statisticsCurrency": 'agency'
        }
    )
    json_data = request.execute()
    return json_data["id"]
    
# AS THE REPORT COULD BE QUITE LARGE, IT WOULD BE SPLITED AS FRAGMENT, EACH FRAGMENT HAS A ID AS THE PREVIOUS STEP SHOWS
    
def download_files(service, report_id, report_fragment):
    file_name = f"{report_id}-report-{report_fragment}.csv"
    with open(file_name, "w") as file:
        print(
            f"Downloading fragment #{report_fragment} from report #{report_id} to {file_name}"
        )
        request = service.reports().getFile(
            reportId=report_id, reportFragment=report_fragment
        )
        file.write(str(request.execute()))
        file.close()
        print("--- Done ---")


# TEST IF REPORT IS READY
def poll_report(service, report_id):
    for _ in range(10):
        try:
            request = service.reports().get(reportId=report_id)
            json_data = request.execute()
            if json_data["isReportReady"]:
                print("The report is ready!")
                for i in range(len(json_data["files"])):
                    print(f"Downloading fragment {str(i)} for report {report_id}")
                    download_files(service, report_id, str(i))
                return
            else:
                print("The report is not ready, trying again in 10 seconds...")
                time.sleep(10)
        except HttpError as e:
            error = json.loads(e.content)["error"]["errors"][0]
            print(f"HTTP code: {e.resp.status}")
            print(f"Error reason: {error['reason']}")
            break
            
def main():
    creds = get_creds()
    service = build_service("doubleclicksearch", "v2", creds)
    report_id = generate_report(
        service=service,
        agency_id="20700000001302897",
        advertiser_id="21700000001688149",
        report_type="conversion",
        columns=[
            {"columnName": "status"},
            {"columnName": "conversionId"},
            {"columnName": "advertiser"},
            {"columnName": "conversionRevenue"},
            {"columnName": "floodlightEventRequestString"}
        ],
        time_range={"startDate": "2021-08-15", "endDate": "2021-08-15"},
        download_format="csv",
        max_rows_per_file=6000000,
        statistics_currency="agency",
    )
    poll_report(service, report_id)

# THIS STEP WOULD PRINT OUT REPORT STATUS AND DOWNLOAD REPORT TO SAME PATH AS SCRIPT
    
if __name__ == "__main__":
    main()
    
## END*************************************************************************************
