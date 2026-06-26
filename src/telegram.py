import os
import httpx
from .models import Lead, AIAnalysis

PRIORITY_EMOJI = {
    "Высокий": "🔴",
    "Средний": "🟡",
    "Низкий": "🟢",
}


def _base_url() -> str:
    return f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}"


async def send_lead_notification(chat_id: int, lead_id: str, lead: Lead, analysis: AIAnalysis) -> int:
    priority_label = f"{PRIORITY_EMOJI.get(analysis.priority, '')} {analysis.priority}"

    text = (
        f"🔔 Новая заявка\n\n"
        f"👤 Имя: {lead.name}\n"
        f"📧 Email: {lead.email}\n"
        f"📱 Телефон: {lead.phone or '—'}\n\n"
        f"🏷 Тип клиента: {analysis.client_type}\n"
        f"⚡️ Приоритет: {priority_label}\n\n"
        f"🤖 AI резюме: {analysis.summary}\n\n"
        f"💬 Сообщение:\n{lead.message}"
    )

    keyboard = {
        "inline_keyboard": [[
            {"text": "✅ Принять", "callback_data": f"accept:{lead_id}"},
            {"text": "❌ Отклонить", "callback_data": f"reject:{lead_id}"},
        ]]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{_base_url()}/sendMessage",
            json={"chat_id": chat_id, "text": text, "reply_markup": keyboard},
            timeout=15,
        )
        response.raise_for_status()

    return response.json()["result"]["message_id"]


async def edit_message_after_decision(chat_id: int, message_id: int, decision: str, manager_name: str) -> None:
    if decision == "accepted":
        text = f"✅ Принято — {manager_name}\nЗапись сохранена в Google Sheets."
    else:
        text = f"❌ Отклонено — {manager_name}\nЗапись сохранена в Google Sheets со статусом Rejected."

    async with httpx.AsyncClient() as client:
        await client.post(
            f"{_base_url()}/editMessageText",
            json={"chat_id": chat_id, "message_id": message_id, "text": text},
            timeout=15,
        )


async def answer_callback(callback_id: str) -> None:
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{_base_url()}/answerCallbackQuery",
            json={"callback_query_id": callback_id},
            timeout=10,
        )
