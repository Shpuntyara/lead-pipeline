import os
import asyncio
from datetime import datetime
from .models import Lead, AIAnalysis


def _append_row_sync(lead: Lead, analysis: AIAnalysis, status: str, manager_name: str) -> None:
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(
        os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json"),
        scopes=scopes,
    )
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(os.getenv("GOOGLE_SPREADSHEET_ID")).worksheet(
        os.getenv("GOOGLE_SHEET_NAME", "Leads")
    )
    sheet.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        lead.name,
        lead.email,
        lead.phone or "",
        lead.message,
        analysis.client_type,
        analysis.priority,
        analysis.summary,
        status,
        manager_name,
    ])


async def append_lead_row(lead: Lead, analysis: AIAnalysis, status: str, manager_name: str) -> None:
    await asyncio.to_thread(_append_row_sync, lead, analysis, status, manager_name)
