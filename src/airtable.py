import os
import httpx
from .models import Lead, AIAnalysis

AIRTABLE_API_TOKEN = os.getenv("AIRTABLE_API_TOKEN")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "Leads")


async def create_lead_record(
    lead: Lead,
    analysis: AIAnalysis,
    status: str,
    manager_name: str,
) -> str:
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

    fields = {
        "Name": lead.name,
        "Email": lead.email,
        "Phone": lead.phone or "",
        "Message": lead.message,
        "Client Type": analysis.client_type,
        "Priority": analysis.priority,
        "AI Summary": analysis.summary,
        "Status": status,
        "Manager": manager_name,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {AIRTABLE_API_TOKEN}",
                "Content-Type": "application/json",
            },
            json={"fields": fields},
            timeout=15,
        )
        response.raise_for_status()

    return response.json()["id"]
