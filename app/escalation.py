SENSITIVE_KEYWORDS = [
    "refund",
    "payment",
    "complaint",
    "cancel",
    "legal",
    "policy",
    "human",
    "customer support",
    "agent",
    "talk to human"
]

def needs_escalation(message: str) -> bool:
    message = message.lower()
    return any(keyword in message for keyword in SENSITIVE_KEYWORDS)