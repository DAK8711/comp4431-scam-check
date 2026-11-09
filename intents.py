"""
intents.py — the short list of questions the assistant can actually answer
======================================================================
A real chatbot understands anything. This one understands eight things, on
purpose.

Why: an elderly user asking "is my bank really calling?" needs a correct answer,
not a fluent guess. Everything outside these eight questions gets an honest
"I am not sure — please call 18222" instead of an invented reply.

This is E1's file. It contains no scam detection: it only decides how to *talk*
about a verdict that something else produced.
"""

# Each intent: the phrases that trigger it, and the reply.
# Matching is a simple lowercase "does the message contain this phrase" test,
# which is boring, predictable, and therefore easy to defend in a viva.

INTENTS = [
    {
        "name": "call_the_number",
        "phrases": [
            "call the number", "should i call", "can i call", "phone them",
            "call them back", "ring them",
        ],
        "reply": (
            "Please do not use any phone number that was inside the message. "
            "Scammers put their own number there. "
            "Call your bank using the number printed on the back of your card, "
            "or call 18222."
        ),
    },
    {
        "name": "is_bank_calling",
        "phrases": [
            "is my bank calling", "bank called me", "bank rang me",
            "really from my bank", "is it really my bank",
        ],
        "reply": (
            "Your bank will never ask for your password or a code by message or phone. "
            "If you are not sure, hang up and call the number on your card."
        ),
    },
    {
        "name": "clicked_link",
        "phrases": [
            "i clicked", "clicked the link", "opened the link", "opened the website",
            "i pressed the link",
        ],
        "reply": (
            "Do not worry — this happens to many people. "
            "Close the page now. Do not type anything into it. "
            "If you entered a password or a card number, call your bank straight away "
            "and tell them what happened."
        ),
    },
    {
        "name": "sent_details",
        "phrases": [
            "i gave my password", "i entered my password", "i gave them my card",
            "i sent the money", "i transferred", "i paid", "i gave them the code",
            "i told them the code",
        ],
        "reply": (
            "Please act now, and do not feel foolish — these messages are built to fool people. "
            "Call your bank immediately and ask them to stop any payment. "
            "Then call 18222 to report it. Keep the message so it can be shown to them."
        ),
    },
    {
        "name": "what_is_18222",
        "phrases": [
            "what is 18222", "who is 18222", "anti-scam", "helpline", "report it",
            "where do i report",
        ],
        "reply": (
            "18222 is the Hong Kong Anti-Scam Helpline. It is free, and you can call it "
            "when you are not sure about a message. They will not ask for your password."
        ),
    },
    {
        "name": "is_it_safe",
        "phrases": [
            "is it safe", "so it is safe", "can i trust", "is it real",
            "am i safe",
        ],
        "reply": (
            "I cannot promise that a message is safe — nobody can. "
            "I can only tell you what the usual signs look like. "
            "If anything still feels wrong, trust that feeling and call 18222."
        ),
    },
    {
        "name": "what_can_you_do",
        "phrases": [
            "what can you do", "help me", "what do i do", "how does this work",
        ],
        "reply": (
            "I can check a message you received and tell you if it looks like a scam. "
            "Paste the message here and I will look at it. "
            "I can also tell you who to call."
        ),
    },
    {
        "name": "thanks",
        "phrases": ["thank you", "thanks", "ok thank", "bye"],
        "reply": (
            "You are welcome. You did the right thing by checking. "
            "If another message worries you, come back any time."
        ),
    },
]

# What the assistant says when it does not recognise the question.
# Honest, short, and it still gives the user something to do.
FALLBACK_REPLY = (
    "I am not sure about that one, and I do not want to guess. "
    "You can paste the message here and I will check it. "
    "For anything else, call the Anti-Scam Helpline on 18222."
)


def match(text):
    """Return the matching intent, or None. First phrase that appears wins."""
    lowered = text.lower()
    for intent in INTENTS:
        for phrase in intent["phrases"]:
            if phrase in lowered:
                return intent
    return None


def reply_for(text):
    """The reply for a message, falling back to the honest 'I do not know'."""
    intent = match(text)
    return intent["reply"] if intent else FALLBACK_REPLY
