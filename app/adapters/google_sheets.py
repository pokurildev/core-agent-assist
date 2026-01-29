import asyncio
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from app.core.config import settings
from app.core.logger import logger

class GoogleSheetsManager:
    """
    Adapter for Google Sheets interactions.
    Uses asyncio.to_thread to run blocking Google API calls in a separate thread.
    """
    def __init__(self):
        self.credentials_json = settings.GOOGLE_CREDENTIALS_JSON
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    def _get_service(self):
        if not self.credentials_json:
            raise ValueError("GOOGLE_CREDENTIALS_JSON is not set")
        
        creds_dict = json.loads(self.credentials_json)
        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=self.scopes
        )
        return build("sheets", "v4", credentials=creds)

    def _append_row_sync(self, spreadsheet_id: str, range_name: str, row_values: list):
        try:
            service = self._get_service()
            body = {"values": [row_values]}
            
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()
            logger.info(f"Row appended to {spreadsheet_id} at {range_name}")
            return "Success"
        except Exception as e:
            logger.error(f"Google Sheets API Error: {e}")
            raise e

    async def append_row(self, spreadsheet_id: str, range_name: str, row_values: list) -> str:
        """
        Asynchronously append a row to Google Sheets.
        """
        try:
           result = await asyncio.to_thread(
               self._append_row_sync, spreadsheet_id, range_name, row_values
           )
           return result
        except Exception as e:
            return f"Error appending row: {str(e)}"

    def _read_sheet_sync(self, spreadsheet_id: str, range_name: str):
        try:
            service = self._get_service()
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id, range=range_name
            ).execute()
            rows = result.get("values", [])
            return rows
        except Exception as e:
            logger.error(f"Google Sheets Read Error: {e}")
            return []

    async def read_leads(self, spreadsheet_id: str, range_name: str) -> list[dict]:
        """
        Fetch leads from Google Sheets and format as list of dicts.
        ASSUMPTION: Columns are [Name, Phone, Notes]
        """
        try:
            rows = await asyncio.to_thread(
                self._read_sheet_sync, spreadsheet_id, range_name
            )
            leads = []
            for i, row in enumerate(rows):
                # Skip header if it exists (optional check, simple logic for now)
                # Let's assume raw data for now or check if row looks like header
                
                # Check for minimum columns to avoid index errors
                name = row[0] if len(row) > 0 else "Unknown"
                phone = row[1] if len(row) > 1 else ""
                notes = row[2] if len(row) > 2 else ""
                
                # Basic ID generation
                leads.append({
                    "id": f"lead-{i}",
                    "customer_name": name,
                    "phone": phone,
                    "notes": notes,
                    "status": "new", # Default status
                    "created_at": "N/A" # Sheets doesn't have timestamp unless we add it
                })
            return leads
        except Exception as e:
            logger.error(f"Error reading leads: {e}")
            return []

# Singleton instance or create on demand
sheets_manager = GoogleSheetsManager()
