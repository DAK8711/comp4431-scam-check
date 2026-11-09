"""
app.py — the scam-checking chatbot
==================================
E1's part of COMP4431: everything the elderly user sees and touches.

It is a conversation, not a form:

    the assistant greets, the user pastes a message, the assistant shows a
    verdict card, then asks one follow-up question that changes the advice.

Where the pieces live:
    response_templates.py   every sentence of the verdict
    intents.py              the eight questions the assistant can answer
    fake_analyzer.py        the placeholder "detection" (to be replaced)
    speech.py               read-aloud

Run it with:
    python -m streamlit run app.py
"""

import streamlit as st

import intents
import response_templates as rt
import speech
from fake_analyzer import EXAMPLES, AnalysisError, analyze

st.set_page_config(
    page_title="Scam check",
    page_icon="🛡️",
    layout="centered",
)

# ---------------------------------------------------------------------------
# The only custom CSS: finger-sized buttons (N3). Everything else is themed in
# .streamlit/config.toml, which is the supported way to do it.
# ---------------------------------------------------------------------------
st.html(
    """
    <style>
      [class*="st-key-reply_"] button {
          min-height: 64px;
          font-weight: 600;
      }
    </style>
    """
)

# ---------------------------------------------------------------------------
# Session state: the whole conversation, and which step we are on.
# Storing the transcript means a page refresh does not lose the verdict.
# ---------------------------------------------------------------------------
if "chat" not in st.session_state:
    st.session_state["chat"] = [
        {
            "who": "assistant",
            "kind": "text",
            "text": (
                "Hello. Paste the message you are worried about, "
                "or press an example."
            ),
        }
    ]
    st.session_state["phase"] = "start"


def add(who, kind, **fields):
    """Append one bubble to the transcript."""
    st.session_state["chat"].append({"who": who, "kind": kind, **fields})


def draw_verdict(result, with_audio):
    """The verdict card, kept as short as it can be.

    On a phone every heading costs a third of a screen, so there are no
    subheadings here: the banner, the reasons, the steps and one call button.
    That is roughly 700px instead of the 1,300px the first version took.
    """
    level = str(result.get("risk_level", "medium")).lower()
    template = rt.template_for(level)

    alert = {"high": st.error, "medium": st.warning, "low": st.success}.get(
        level, st.warning
    )
    alert(template["body"], title=f"{template['icon']} {template['headline']}")

    reasons = rt.plain_reasons(result.get("matched_patterns"))
    st.markdown("\n".join(f"- {reason}" for reason in reasons))

    steps = "\n".join(
        f"**{number}.** {step}"
        for number, step in enumerate(template["steps"], start=1)
    )
    st.markdown(steps)

    st.link_button(
        "Call 18222 — Anti-Scam Helpline",
        "tel:18222",
        icon=":material/call:",
        width="stretch",
    )
    st.caption("Or call the number on the back of your bank card.")

    # Read-aloud, only on the newest verdict so old cards stay quiet in history.
    if with_audio:
        audio = speech.synthesize(speech.spoken_text(template))
        if audio:
            st.audio(
                audio,
                format="audio/wav",
                autoplay=True,
                alt="A spoken version of this warning",
            )
            st.caption("Press play to hear it again.")
        else:
            st.caption("Read-aloud is not available on this computer.")


def looks_like_question(text):
    """Cheap test used to decide between 'answer it' and 'check it'.

    A scam message almost never starts with "what" or ends with a question mark,
    so this one line keeps the two behaviours apart without any guessing.
    """
    lowered = text.strip().lower()
    starters = ("what", "why", "how", "who", "where", "when", "is ", "can ", "should", "do i", "does ")
    return lowered.endswith("?") or lowered.startswith(starters)


def check_message(text):
    """Run the (currently fake) analyser and put the verdict in the transcript."""
    try:
        result = analyze(text)
    except AnalysisError:
        add(
            "assistant",
            "text",
            text=(
                "I could not check that message right now. "
                "Please call the Anti-Scam Helpline on 18222."
            ),
        )
        st.session_state["phase"] = "done"
        return

    # Very short text with nothing suspicious in it is probably not a message.
    if len(text) < 25 and not result.get("matched_patterns"):
        add(
            "assistant",
            "text",
            text=(
                "I do not see a message there. "
                "Paste the message you received and I will check it."
            ),
        )
        return

    add("assistant", "verdict", result=result)
    st.session_state["phase"] = "after"


def resolve(replied):
    """The user pressed Yes or No. Put their answer into the conversation."""
    add("user", "text", text="Yes, I did" if replied else "No, I have not")
    add(
        "assistant",
        "text",
        text=rt.AFTER_REPLIED if replied else rt.AFTER_NOT_REPLIED,
    )
    st.session_state["phase"] = "done"


# The question that changes the advice. It sits just above the chat box, not
# inside the transcript, because on a phone a button inside the transcript can
# slide underneath the pinned input box and become impossible to tap.


# ---------------------------------------------------------------------------
# Header. The big title only appears on the opening screen: once the
# conversation has started it is 300px of scrolling on a phone and tells the
# user something they already know.
# ---------------------------------------------------------------------------
if st.session_state["phase"] == "start":
    st.title("Is this message a scam?")

st.markdown(rt.PRIVACY_NOTICE)

# ---------------------------------------------------------------------------
# The conversation itself.
# ---------------------------------------------------------------------------
entries = st.session_state["chat"]
verdict_positions = [i for i, e in enumerate(entries) if e["kind"] == "verdict"]
newest_verdict = verdict_positions[-1] if verdict_positions else -1

for index, entry in enumerate(entries):
    avatar = "🛡️" if entry["who"] == "assistant" else "🙂"
    with st.chat_message(entry["who"], avatar=avatar):
        if entry["kind"] == "verdict":
            if index == newest_verdict:
                draw_verdict(entry["result"], with_audio=True)
            else:
                # An older check is folded down to one line. Keeping three full
                # cards in the transcript is what made the page scroll forever.
                old = rt.template_for(entry["result"].get("risk_level"))
                st.markdown(f"{old['icon']} **{old['headline']}** _(checked earlier)_")
        else:
            st.markdown(entry["text"])

# The follow-up question, kept outside the transcript so it is always tappable.
if st.session_state["phase"] == "after":
    st.markdown("**Have you already replied to it, or sent any money?**")
    no_column, yes_column = st.columns(2)
    if no_column.button("No, I have not", key="reply_no", width="stretch"):
        resolve(replied=False)
        st.rerun()
    if yes_column.button("Yes, I did", key="reply_yes", width="stretch"):
        resolve(replied=True)
        st.rerun()

# Example shortcuts, only before the first check.
# These are pills rather than buttons on purpose: a pills widget is one compact
# row by design, so there is no custom CSS involved and nothing to break on a
# small screen.
if st.session_state["phase"] == "start":
    st.caption("No message to hand? Try one:")
    choice = st.pills(
        "Try an example",
        [label for label, _ in EXAMPLES],
        selection_mode="single",
        key="example_pick",
        label_visibility="collapsed",
        width="content",
    )
    if choice and choice != st.session_state.get("example_done"):
        st.session_state["example_done"] = choice
        example_text = next(text for label, text in EXAMPLES if label == choice)
        add("user", "text", text=example_text)
        check_message(example_text)
        st.rerun()

# ---------------------------------------------------------------------------
# Footer — two short lines instead of a paragraph (requirement T3).
# The demo label lives here rather than in response_templates.py so that a
# half-finished upload can never remove the sentence that keeps this honest.
# ---------------------------------------------------------------------------
st.caption(rt.FOOTER)
st.caption("🔧 Demo — placeholder answers.")

# Room for the pinned chat box. Without this, the last line of text sits under
# the input on a phone and gets clipped mid-sentence.
st.space(180)

# ---------------------------------------------------------------------------
# The input. One box, used for both a pasted message and a question.
# ---------------------------------------------------------------------------
typed = st.chat_input("Paste the message here")
if typed:
    typed = typed.strip()
    if typed:
        add("user", "text", text=typed)
        intent = intents.match(typed)
        if intent:
            add("assistant", "text", text=intent["reply"])
            if st.session_state["phase"] == "start":
                st.session_state["phase"] = "done"
        elif looks_like_question(typed):
            # A question we do not have an answer for. Say so, do not guess.
            add("assistant", "text", text=intents.FALLBACK_REPLY)
            if st.session_state["phase"] == "start":
                st.session_state["phase"] = "done"
        else:
            check_message(typed)
        st.rerun()
