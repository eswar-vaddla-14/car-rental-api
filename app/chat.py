from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import uuid
from app.escalation import needs_escalation
from google import genai
import os

chat_router = APIRouter()

# Context
CHAT_CONTEXT = {}

# State (BOT or HUMAN)
CHAT_STATE = {}

# Chat Request Model
class ChatRequest(BaseModel):
    user_id: str
    message: str
    chat_id: Optional[str] = None

# Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# User's message route (./chat/message)
@chat_router.post("/message")
async def chat_message(req: ChatRequest):

    if not req.chat_id:
        chat_id = str(uuid.uuid4())
        CHAT_CONTEXT[chat_id] = []
        CHAT_STATE[chat_id] = "BOT"
    else:
        chat_id = req.chat_id
        CHAT_CONTEXT.setdefault(chat_id, [])
        CHAT_STATE.setdefault(chat_id, "BOT")

    # Already escalated
    if CHAT_STATE[chat_id] == "HUMAN":
        return {
            "chat_id": chat_id,
            "reply": "This chat is handled by customer support.",
            "mode": "HUMAN",
            "escalated": True
        }

    # Storing user message
    CHAT_CONTEXT[chat_id].append({
        "role": "user",
        "content": req.message
    })

    if needs_escalation(req.message):
        CHAT_STATE[chat_id] = "HUMAN"
        return {
            "chat_id": chat_id,
            "reply": "This chat is forwarded to the customer support.",
            "mode": "HUMAN",
            "escalated": True
        }
    
    # Conversation context
    context_string = ""
    for chat in CHAT_CONTEXT[chat_id]:
        string = chat["role"]+": "+chat["content"]+"; "
        context_string += string

    # Prompt
    prompt = f'''
Company Overview: Rent N Rides

Rent N Rides is an international online car rental booking platform that allows users to search for, compare, and book rental vehicles worldwide. It is not a traditional rental garage, but a digital intermediary that connects customers with independent vehicle providers. 
rentnrides.com

📌 Legal & Corporate Identity

Operating Company: primooo Global Ltd (trading as Rent N Rides) 
rentnrides.com

Country of Registration: Malta (a member state of the EU) 
rentnrides.com

Company Type: Commercial intermediary / travel service platform 
rentnrides.com

Business Model: Online booking and reservation platform for car rentals and transportation services across global locations. 
rentnrides.com

📍 Headquarters & Legal Address

According to the official terms (Terms and Conditions hosted on the site):

primooo Global Ltd (Rent N Rides)
Level 2, The Business Centre
Triq il-Karmnu
LUQA LQA 1311
Malta 
rentnrides.com

This address is used for administrative and legal purposes (registered company details). 
rentnrides.com

📞 Customer Support & Contact

The Terms & Conditions also list dedicated support contact information:

✅ Email: support@rentnrides.eu
 
Rent N Ride

✅ Phone: +356 7797 9979 (Malta office, customer support hours Monday⁠–⁠Friday) 
Rent N Ride

This is distinct from local or regional office addresses; it’s the main support channel. 
Rent N Ride

🌍 Where It Operates

The platform is global in scope — not tied to just one country — and lets users book car and ground transportation rentals in many international destinations via partner providers. 
rentnrides.com

This means:

Locations: Worldwide cities and airports

Providers: Independent local vehicle rental companies

Service Scope: Cars, minivans, buses, luxury vehicles, private transfers, etc. 
rentnrides.com

Even though the business is based in Malta, the service is intended for use worldwide with local partners facilitating the actual rental. 
rentnrides.com

📦 Business Model (How It Works)
📌 Intermediary Marketplace

Rent N Rides does not own the cars or operate physical fleets. Instead:

You search for available vehicles on the site or app.

The platform connects you to independent rental providers.

You complete booking online; the platform may handle payment or forward details to the provider.

Your contract is ultimately with the provider, though support and payment handling may be facilitated by Rent N Rides. 
rentnrides.com

🔎 This means Rent N Rides is similar to other travel/booking marketplaces — like Booking.com or Kayak — but specifically for vehicle rentals. 
rentnrides.com

📜 Terms & Conditions Highlights

According to the site’s official legal terms:

🔹 Booking Terms

Governed by Maltese law. 
Rent N Ride

You agree to the provider’s terms once you book. 
Rent N Ride

Rent N Rides acts as a facilitator, not as the operational provider. 
Rent N Ride

🔹 Payments Process

Payments may be fully taken at booking or part-collected at pickup, depending on provider terms. 
Rent N Ride

Platform fees are included in the total price shown at checkout. 
Rent N Ride

🔹 Data & Privacy

Personal data (driver info, payment details) is collected for booking and compliance. 
Rent N Ride

Data shared with providers only as required to fulfill bookings. 
Rent N Ride

🔹 Liability

Rent N Rides is not liable for provider performance (e.g., car condition, delays). 
Rent N Ride

Liability caps at platform fees paid over the prior 12 months. 
Rent N Ride

🧠 Business Focus & Value Proposition

According to how the platform positions itself publicly:

✔️ Transparent pricing with no hidden fees
✔️ Quick online booking
✔️ 24/7 availability
✔️ Comprehensive insurance options offered through providers 
rentnrides.com

⚠️ Notes on Reviews & Presence

The platform is commercial and global, but independent third-party reviews are limited. It’s important to confirm provider reliability after booking.

It is distinct from similarly named local rental businesses (e.g., Rent n Rides in Mumbai unrelated to the Malta platform). 
Justdial

You are a chatbot for Rent n Rides car rental service.
Answer only questions related to:
- Car rentals
- Pricing
- Trips
- Booking process
- Vehicles and availability

If the question is outside this scope, don't respond.

Do not answer sensitive topics.
Be clear, polite, and short.

CONTEXT:
{context_string}

USER:
{req.message}
'''


    # Response from Gemini
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )

    bot_reply = response.text

    # Storing bot reply
    CHAT_CONTEXT[chat_id].append({
        "role": "assisstant",
        "content": bot_reply,
    })

    response = {
        "chat_id": chat_id,
        "reply": bot_reply,
        "mode": "BOT",
        "escalated": False,
        "detail": CHAT_CONTEXT[chat_id],
    }

    return response

