# Event Fetching Script 
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Function to authenticate and connect to Google Sheets
def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    return client

# Function to fetch all events from Google Sheets
def get_event_data():
    client = authenticate_google_sheets()
    sheet = client.open("college event datas").sheet1

    events = sheet.get_all_records()  # Get all event rows as dictionaries
    return events

# Test fetching events
if __name__ == "__main__":
    event_data = get_event_data()
    print("Fetched Events:")
    for event in event_data:
        print(event)
