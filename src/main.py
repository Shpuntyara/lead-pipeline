import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

from .models import Lead, AIAnalysis
from .ai import analyze_lead
from .scheduler import get_on_duty_manager
from .telegram import send_lead_notification, edit_message_after_decision, answer_callback
from .sheets import append_lead_row

pending_leads: dict[str, dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Lead Pipeline started")
    yield


app = FastAPI(title="AI Lead Pipeline", lifespan=lifespan)


@app.post("/webhook")
async def receive_lead(request: Request):
    body = await request.json()
    lead = parse_tally_payload(body)

    analysis = await analyze_lead(lead)
    manager_chat_id, manager_name = get_on_duty_manager()
    lead_id = str(uuid.uuid4())[:8]

    message_id = await send_lead_notification(
        chat_id=manager_chat_id,
        lead_id=lead_id,
        lead=lead,
        analysis=analysis,
    )

    pending_leads[lead_id] = {
        "lead": lead,
        "analysis": analysis,
        "manager_chat_id": manager_chat_id,
        "manager_name": manager_name,
        "message_id": message_id,
    }

    return {"status": "ok", "lead_id": lead_id, "manager": manager_name}


@app.post("/bot-callback")
async def bot_callback(request: Request):
    body = await request.json()

    callback_query = body.get("callback_query")
    if not callback_query:
        return {"ok": True}

    data = callback_query.get("data", "")
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    callback_id = callback_query["id"]

    await answer_callback(callback_id)

    if ":" not in data:
        return {"ok": True}

    action, lead_id = data.split(":", 1)

    if lead_id not in pending_leads:
        return {"ok": True}

    stored = pending_leads.pop(lead_id)
    lead: Lead = stored["lead"]
    analysis: AIAnalysis = stored["analysis"]
    manager_name: str = stored["manager_name"]

    decision = "accepted" if action == "accept" else "rejected"
    status = "Accepted" if decision == "accepted" else "Rejected"

    await append_lead_row(lead, analysis, status, manager_name)
    await edit_message_after_decision(chat_id, message_id, decision, manager_name)

    return {"ok": True}


@app.get("/health")
async def health():
    return {"status": "ok", "pending_leads": len(pending_leads)}


def parse_tally_payload(body: dict) -> Lead:
    fields = body.get("data", {}).get("fields", [])
    data = {f["label"].lower(): f.get("value", "") for f in fields}

    return Lead(
        name=data.get("name", data.get("имя", "Unknown")),
        email=data.get("email", data.get("почта", "")),
        phone=data.get("phone", data.get("телефон")) or None,
        message=data.get("message", data.get("сообщение", data.get("вопрос", ""))),
    )
