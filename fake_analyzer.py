"""
fake_analyzer.py
================
!!! THIS FILE IS A STAND-IN. IT IS NOT THE SCAM DETECTOR. !!!

Henry builds the real pattern database and matching engine.
EarlyFat builds the real risk scoring and the API around it.

This file exists so the interface can be built and demonstrated BEFORE their
code exists. It returns made-up answers using a handful of keywords. It is
roughly 40 lines of real logic and it will be deleted (or bypassed) the day
EarlyFat's endpoint goes live.

To switch to the real API later:
    1. set USE_REAL_API = True below
    2. fill in API_URL
    3. nothing in app.py changes, because the return shape is identical

The agreed shape (see API_CONTRACT.md):
    {
        "risk_score": 0-100,
        "risk_level": "low" | "medium" | "high",
        "matched_patterns": ["urgency", "money request", ...],
        "explanation": "one short sentence"
    }
"""

import requests

# ---------------------------------------------------------------------------
# Switch this to True when EarlyFat's server is running.
# ---------------------------------------------------------------------------
USE_REAL_API = False
API_URL = "http://127.0.0.1:8000/analyze"
TIMEOUT_SECONDS = 3


class AnalysisError(Exception):
    """Raised when the message could not be checked at all."""


# ---------------------------------------------------------------------------
# The fake rules. Each entry is one thing scammers often do.
# "words" are plain lowercase fragments; if any of them appears in the
# message, that pattern counts as "found" and its weight is added to the score.
# These weights are made up, not validated. Do not quote them in the report.
# ---------------------------------------------------------------------------
SIGNALS = [
    {
        "pattern": "urgency",
        "weight": 25,
        "words": ["urgent", "immediately", "within 24 hours", "final notice",
                  "last warning", "act now", "expires today", "only today",
                  "asap", "suspended", "blocked", "hacked", "hack",
                  "within 1 hour", "emergency"],
    },
    {
        "pattern": "money request",
        "weight": 30,
        "words": ["transfer", "send money", "give me money", "send me money",
                  "pay now", "payment of", "wire", "remit", "deposit", "$",
                  "hkd", "refund fee", "redelivery fee", "money", "cash",
                  "gift card", "itunes card"],
    },
    {
        "pattern": "bank impersonation",
        "weight": 30,
        "words": ["hsbc", "hang seng", "bank of china", "standard chartered",
                  "dbs", "citibank", "your bank", "bank account", "atm card"],
    },
    {
        "pattern": "government impersonation",
        "weight": 40,
        "words": ["police", "customs", "immigration", "inland revenue",
                  "government", "court", "arrest", "warrant", "ird"],
    },
    {
        "pattern": "prize",
        "weight": 30,
        "words": ["you have won", "congratulations", "lucky draw", "prize",
                  "lottery", "jackpot", "winner", "claim your"],
    },
    {
        "pattern": "parcel",
        "weight": 15,
        "words": ["parcel", "delivery", "courier", "sf express", "package",
                  "shipment", "post office"],
    },
    {
        "pattern": "job offer",
        "weight": 15,
        "words": ["job offer", "work from home", "part-time job", "hiring",
                  "earn extra", "daily pay", "no experience needed"],
    },
    {
        "pattern": "investment",
        "weight": 25,
        "words": ["guaranteed return", "double your", "investment plan",
                  "high return", "profit guaranteed", "forex", "trading group"],
    },
    {
        "pattern": "romance",
        "weight": 15,
        "words": ["i love you", "my dear", "met you online", "lonely",
                  "soulmate", "send me a gift card"],
    },
    {
        "pattern": "tech support",
        "weight": 20,
        "words": ["virus", "your computer", "your phone is", "technical support",
                  "microsoft support", "remote access", "anydesk", "teamviewer"],
    },
    {
        "pattern": "account problem",
        "weight": 20,
        "words": ["account will be closed", "account suspended", "unusual activity",
                  "verify your account", "reactivate", "locked account",
                  "identity check", "confirm your identity"],
    },
    {
        "pattern": "password request",
        "weight": 30,
        "words": ["password", "one-time password", "otp", "pin number",
                  "verification code", "security code", "cvv"],
    },
    {
        "pattern": "crypto",
        "weight": 20,
        "words": ["bitcoin", "usdt", "crypto", "wallet address", "binance",
                  "ethereum"],
    },
    {
        "pattern": "link",
        "weight": 15,
        "words": ["http://", "https://", "bit.ly", ".top", ".xyz", "click here",
                  "click this link"],
    },
]

HIGH_AT = 65   # score at or above this is "high"
MEDIUM_AT = 25  # score at or above this is "medium"


def _score_with_fake_rules(message):
    """The placeholder logic. Returns a dict in the agreed shape."""
    text = message.lower()

    matched = []
    score = 0
    for signal in SIGNALS:
        if any(word in text for word in signal["words"]):
            matched.append(signal["pattern"])
            score += signal["weight"]

    score = min(score, 100)

    if score >= HIGH_AT:
        level = "high"
    elif score >= MEDIUM_AT:
        level = "medium"
    else:
        level = "low"

    if matched:
        explanation = f"This message shows {len(matched)} common signs of a scam."
    else:
        explanation = "We did not find the usual signs of a scam."

    return {
        "risk_score": score,
        "risk_level": level,
        "matched_patterns": matched,
        "explanation": explanation,
    }


def _call_real_api(message):
    """The real call, used once EarlyFat's server exists."""
    response = requests.post(
        API_URL,
        json={"message": message},
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def analyze(message):
    """Check one message and return the agreed dict.

    app.py only ever calls this function, so swapping the fake for the real
    API is a one-line change here and nothing else.
    """
    if USE_REAL_API:
        try:
            return _call_real_api(message)
        except Exception as error:
            # Never let a backend problem turn into a broken screen.
            raise AnalysisError("The checking service is not answering.") from error

    return _score_with_fake_rules(message)


# ---------------------------------------------------------------------------
# Three messages for the demo. The first should come out high risk,
# the second medium, the third low. These are the ones on the buttons.
# ---------------------------------------------------------------------------
EXAMPLES = [
    (
        "Bank text",
        "HSBC ALERT: A payment of $2,300 to an unknown account was detected. "
        "Your account will be SUSPENDED unless you confirm your identity now: "
        "http://hsbc-verify-secure.top/login",
    ),
    (
        "Parcel text",
        "Your parcel could not be delivered. Please pay the redelivery fee here: "
        "http://hk-post-fee.info/pay",
    ),
    (
        "From family",
        "Hi Mum, I'll pick up the shopping on my way home. Do you need anything "
        "from the shop? See you at 6.",
    ),
]


if __name__ == "__main__":
    # Quick self-check: run `python fake_analyzer.py` to see the three results.
    for label, text in EXAMPLES:
        result = analyze(text)
        print(f"{label:24} score={result['risk_score']:3}  level={result['risk_level']:6} "
              f"patterns={result['matched_patterns']}")
