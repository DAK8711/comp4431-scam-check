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
    "urgency": "it asks you to act fast",
    "money request": "it asks for money",
    "bank impersonation": "it pretends to be your bank",
    "government impersonation": "it pretends to be the police or government",
    "prize": "it says you have won something",
    "parcel": "it mentions a parcel",
    "job offer": "it offers a job you did not apply for",
    "investment": "it promises quick money",
    "romance": "it is from a stranger",
    "tech support": "it says your phone has a problem",
    "account problem": "it says your account will be blocked",
    "password request": "it asks for a password or code",
    "crypto": "it asks for cryptocurrency",
    "link": "it has a link",
}

# If the backend sends a pattern we have not translated yet, we fall back to
# this neutral phrase instead of showing a raw snake_case word to an elderly user.
FALLBACK_REASON = "it uses wording scammers often use"

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
        # One sentence. The reassurance moved into the steps, because on a phone
        # every extra line in the banner pushes the buttons off the screen.
        "body": "Do not reply, and do not click anything in it. You did the right thing by checking.",
        "steps": [
            "Do not reply, and do not click any link.",
            "Do not send money, a password, or any code.",
            "Call your bank using the number on the back of your card.",
        ],
    },
    "medium": {
        "icon": "⚠️",
        "headline": "This message looks suspicious.",
        "body": "Some of the wording is used by scammers. It might still be real.",
        "steps": [
            "Do not send money or personal details yet.",
            "Do not use the link in the message.",
            "Ask someone you trust, or call your bank.",
        ],
    },
    "low": {
        "icon": "✅",
        "headline": "Nothing obviously dangerous here.",
        "body": "We did not find the usual signs of a scam. That is not a promise that it is safe.",
        "steps": [
            "Still be careful with messages from strangers.",
            "Never share your password, your PIN, or a code.",
            "If you feel unsure, ask a family member first.",
        ],
    },
}

# Safety net: if the backend sends something unexpected, we behave as if it is
# medium risk (ask the user to check) rather than as if it is safe.
DEFAULT_LEVEL = "medium"

# ---------------------------------------------------------------------------
# 2b. The two replies to "have you already replied, or sent any money?"
# ---------------------------------------------------------------------------
# This second question matters more than the verdict itself. Someone who has
# already sent money needs different instructions from someone who is still
# deciding, and telling them both the same thing wastes the most valuable
# minutes of the whole incident.

AFTER_NOT_REPLIED = (
    "Good. Do not reply to it, and do not use any link or phone number inside it.\n\n"
    "If you want to be certain, call your bank on the number printed on the back "
    "of your card."
)

AFTER_REPLIED = (
    "**Please call your bank now.** Ask them to stop any payment, and tell them "
    "what you sent.\n\n"
    "1. Call the number on the back of your card.\n"
    "2. Keep the message. Do not delete it.\n"
    "3. Call 18222 to report it.\n\n"
    "This happens to many careful people. You did the right thing by checking."
)


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
    "We never ask for your name, password or bank details."
)

FOOTER = "A guide, not a guarantee. If in doubt, call 18222."


# The order the reasons are shown in. The most serious sign comes first, so the
# one line starts with "it pretends to be your bank" rather than "it has a link".
PRIORITY = [
    "bank impersonation",
    "government impersonation",
    "password request",
    "money request",
    "urgency",
    "prize",
    "investment",
    "tech support",
    "account problem",
    "parcel",
    "job offer",
    "romance",
    "crypto",
    "link",
]


def _rank(pattern):
    key = str(pattern).strip().lower()
    return PRIORITY.index(key) if key in PRIORITY else len(PRIORITY)


def plain_reasons(matched_patterns, limit=3):
    """Turn backend pattern names into short phrases, for one "Why:" line.

    This used to return full sentences, one per bullet, taking three lines of
    the screen. A person who thinks they have been scammed needs to know what to
    DO, not to read a diagnosis. So the reasons are now three-word phrases that
    fit on one line under the steps: "Why: it pretends to be your bank, it asks
    for money, it asks you to act fast."

    matched_patterns : list of strings from the API, e.g. ["urgency", "prize"]
    limit            : at most 3 phrases, so the line stays one line.

    Returns a list of phrases, de-duplicated, never empty.
    """
    phrases = []
    for pattern in sorted(matched_patterns or [], key=_rank):
        key = str(pattern).strip().lower()
        phrase = PATTERN_PLAIN.get(key, FALLBACK_REASON)
        if phrase not in phrases:
            phrases.append(phrase)
        if len(phrases) >= limit:
            break

    if not phrases:
        phrases.append(FALLBACK_REASON)
    return phrases


def template_for(risk_level):
    """Return the template dict for a risk level, defaulting safely."""
    key = str(risk_level).strip().lower()
    return TEMPLATES.get(key, TEMPLATES[DEFAULT_LEVEL])
