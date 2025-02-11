import gspread
from oauth2client.service_account import ServiceAccountCredentials

class GoogleSheetsManager:
    def __init__(self, secrets):
        # Parse secrets
        credentials_dict = {
            "type": secrets["type"],
            "project_id": secrets["project_id"],
            "private_key_id": secrets["private_key_id"],
            "private_key": secrets["private_key"].replace("\\n", "\n"),
            "client_email": secrets["client_email"],
            "client_id": secrets["client_id"],
            "auth_uri": secrets["auth_uri"],
            "token_uri": secrets["token_uri"],
            "auth_provider_x509_cert_url": secrets["auth_provider_x509_cert_url"],
            "client_x509_cert_url": secrets["client_x509_cert_url"]
        }

        # Setup gspread client
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        self.client = gspread.authorize(creds)

    def get_sheet(self, sheet_name):
        """Open a Google Sheet by name."""
        return self.client.open(sheet_name).sheet1

    def update_cell(self, sheet, row, col, value):
        """Update a single cell."""
        sheet.update_cell(row, col, value)

    def update_multiple_cells(self, sheet, updates):
        """Batch update multiple cells."""
        for row, col, value in updates:
            sheet.update_cell(row, col, value)
