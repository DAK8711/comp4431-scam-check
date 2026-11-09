"""
response_templates.py
=====================
E1's core deliverable: the exact words the user sees.

Rules this file obeys (see UX_GUIDELINES.md):
  - Plain English. No jargon. "fake message", never "phishing" / "social engineering".
  - Short sentences, one idea per line.
  - Calm tone, never alarmist, never blaming.
  - Every risk level ends with something to DO.
  - Never says "100% safe".
  - Never asks for personal information.

There is exactly ONE place to change the wording of the app: this file.
"""

# ---------------------------------------------------------------------------
# 1. How we translate the backend's technical pattern names into plain English
# ---------------------------------------------------------------------------
# EarlyFat's API returns things like "bank_impersonation".
# The user must never see that. They see this instead.
# When Henry gives you his final category list, just add a line here.

PATTERN_PLAIN = {
    "urgency": "It says you must act fast, or something bad will happen.",
    "money request": "It asks you to send money.",
    "bank impersonation": "It pretends to be your bank.",
    "government impersonation": "It pretends to be from the government, police or customs.",
    "prize": "It says you have won a prize or a lottery.",
    "parcel": "It talks about a parcel or a delivery problem.",
    "job offer": "It offers you a job you did not apply for.",
    "investment": "It promises you quick or guaranteed money.",
    "romance": "It is from someone you have never met in person.",
    "tech support": "It says your phone or computer has a problem.",
    "account problem": "It says your account will be closed or blocked.",
    "password request": "It asks for a password, a code, or a PIN.",
    "crypto": "It asks you to pay or invest using cryptocurrency.",
    "link": "It contains a link you did not expect.",
}

# If the backend sends a pattern we have not translated yet, we fall back to
# this neutral sentence instead of showing a raw snake_case word to an elderly
# user.
FALLBACK_REASON = "It contains wording that scammers often use."

# ---------------------------------------------------------------------------
# 2. The three response templates
# ---------------------------------------------------------------------------
# headline : one short sentence, the whole verdict
# body     : at most two short sentences, the reassurance / context
# steps    : what to do next, in order. 3 items maximum.
#
# Colour and icon live in the app, not here (design change != wording change).

TEMPLATES = {
    "high": {
        "icon": "🛑",
        "headline": "This looks like a scam.",
        "body": (
            "Please do not reply, and do not click anything in it. "
            "Messages like this fool many careful people — you did the right thing by checking."
        ),
        "steps": [
            "Do not reply, and do not click any link.",
            "Do not send money, a password, or any code.",
            "Call your bank using the number on the back of your card.",
        ],
    },
    "medium": {
        "icon": "⚠️",
        "headline": "This message looks suspicious.",
        "body": (
            "Some of the wording is used by scammers. It might still be real, "
            "but please check before you do anything."
        ),
        "steps": [
            "Do not send money or personal details yet.",
            "Do not use the link in the message — open the official app or website instead.",
            "Ask someone you trust, or call your bank using the number on your card.",
        ],
    },
    "low": {
        "icon": "✅",
        "headline": "Nothing obviously dangerous here.",
        "body": (
            "We did not find the usual signs of a scam. That is not a promise that it is safe — "
            "no one can promise that."
        ),
        "steps": [
            "Still be careful with messages from people you do not know.",
            "Never share your password, your PIN, or a code sent to your phone.",
            "If you feel unsure, ask a family member or friend first.",
        ],
    },
}

# Safety net: if the backend sends something unexpected, we behave as if it is
# medium risk (ask the user to check) rather than as if it is safe.
DEFAULT_LEVEL = "medium"

# ---------------------------------------------------------------------------
# 3. Where to call
# ---------------------------------------------------------------------------
# Replace these with the real numbers your group decides to show.
# NOTE: a real bank hotline is deliberately NOT hardcoded, because showing a
# wrong bank number is itself a scam risk. We tell the user to use the number
# printed on their card.

CONTACTS = [
    {
        "label": "Anti-Scam Helpline (HK)",
        "number": "18222",
        "hint": "Free. Government helpline for suspected scams.",
        "kind": "call",
    },
    {
        "label": "Your bank",
        "number": "",
        "hint": "Call the number on the back of your bank card. Do not use a number from the message.",
        "kind": "note",
    },
    {
        "label": "Someone you trust",
        "number": "",
        "hint": "A family member or friend. It is always fine to ask for a second look.",
        "kind": "note",
    },
]

# ---------------------------------------------------------------------------
# 4. Fixed text used in several places
# ---------------------------------------------------------------------------

PRIVACY_NOTICE = (
    "**Your message is not saved.** "
    "We do not keep it, we do not share it, and we never ask for your name, "
    "password or bank details."
)

FOOTER = (
    "This is a guide to help you decide, not a guarantee. "
    "When in doubt, call your bank or the Anti-Scam Helpline on 18222."
)


def plain_reasons(matched_patterns, limit=3):
    """Turn backend pattern names into short plain-English reasons.

    matched_patterns : list of strings from the API, e.g. ["urgency", "prize"]
    limit            : we show at most 3 bullets, because X1 says no long lists.

    Returns a list of sentences, de-duplicated, never empty.
    """
    sentences = []
    for pattern in matched_patterns or []:
        key = str(pattern).strip().lower()
        sentence = PATTERN_PLAIN.get(key, FALLBACK_REASON)
        if sentence not in sentences:
            sentences.append(sentence)
        if len(sentences) >= limit:
            break

    if not sentences:
        sentences.append(FALLBACK_REASON)
    return sentences


def template_for(risk_level):
    """Return the template dict for a risk level, defaulting safely."""
    key = str(risk_level).strip().lower()
    return TEMPLATES.get(key, TEMPLATES[DEFAULT_LEVEL])
