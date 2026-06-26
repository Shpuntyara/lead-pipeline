import os
import json
import httpx
from .models import Lead, AIAnalysis

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "nvidia/nemotron-3-super-120b-a12b:free"

SYSTEM_PROMPT = """Ты помощник по квалификации лидов. Проанализируй заявку и верни JSON строго в таком формате:
{
  "client_type": "Малый бизнес" | "Корпорат" | "Частное лицо",
  "priority": "Высокий" | "Средний" | "Низкий",
  "summary": "одна строка — суть запроса клиента"
}

Правила приоритета:
- Высокий: срочно, большой бюджет, корпорат
- Средний: конкретный запрос без спешки
- Низкий: размытый запрос, нет бюджета, просто интересуется"""


async def analyze_lead(lead: Lead) -> AIAnalysis:
    user_content = f"Имя: {lead.name}\nEmail: {lead.email}\nТелефон: {lead.phone or '—'}\nСообщение: {lead.message}"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
            },
            timeout=30,
        )
        response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"].strip()

    start = content.find("{")
    end = content.rfind("}") + 1
    data = json.loads(content[start:end])

    return AIAnalysis(**data)
