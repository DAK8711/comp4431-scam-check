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
      .st-key-example_0 button,
      .st-key-example_1 button,
      .st-key-example_2 button {
          min-height: 56px;
      }
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
                "Hello. Are you worried about a message you received?\n\n"
                "Paste it below and I will look at it. "
                "You can also press one of the examples."
            ),
        }
    ]
    st.session_state["phase"] = "start"


def add(who, kind, **fields):
    """Append one bubble to the transcript."""
    st.session_state["chat"].append({"who": who, "kind": kind, **fields})


def draw_verdict(result, with_audio):
    """The verdict card. Same card as before, now inside a chat bubble."""
    level = str(result.get("risk_level", "medium")).lower()
    template = rt.template_for(level)

    alert = {"high": st.error, "medium": st.warning, "low": st.success}.get(
        level, st.warning
    )
    alert(template["body"], title=f"{template['icon']} {template['headline']}")

    with st.container(border=True):
        st.subheader("Why we think so")
        for reason in rt.plain_reasons(result.get("matched_patterns")):
            st.markdown(f"- {reason}")

    st.subheader("What to do now")
    for number, step in enumerate(template["steps"], start=1):
        st.markdown(f"**{number}.** {step}")

    st.subheader("Who to call")
    for contact in rt.CONTACTS:
        if contact["kind"] == "call":
            st.link_button(
                f"{contact['label']} — {contact['number']}",
                f"tel:{contact['number']}",
                icon=":material/call:",
                width="stretch",
            )
            st.caption(contact["hint"])
        else:
            with st.container(border=True):
                st.markdown(f"**{contact['label']}**")
                st.markdown(contact["hint"])

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
            st.caption("It starts on its own. Press play to hear it again.")
        else:
            st.caption(
                "This computer cannot read things aloud. "
                "The warning is written above, and you can also call 18222."
            )


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
    add(
        "assistant",
        "ask_after",
        text="Have you already replied to it, or sent any money?",
    )
    st.session_state["phase"] = "after"


def resolve_answer(entry, replied):
    """The user pressed Yes or No. Replace the question with their answer."""
    entry["kind"] = "answered"
    entry["text"] = (
        "Have you already replied to it, or sent any money?\n\n"
        f"**You answered:** {'Yes, I did' if replied else 'No, I have not'}"
    )
    add(
        "assistant",
        "text",
        text=rt.AFTER_REPLIED if replied else rt.AFTER_NOT_REPLIED,
    )
    st.session_state["phase"] = "done"


# ---------------------------------------------------------------------------
# Header — identical at every step, so the user never feels lost.
# ---------------------------------------------------------------------------
st.title("Is this message a scam?")
st.markdown(rt.PRIVACY_NOTICE)
st.divider()

# ---------------------------------------------------------------------------
# The conversation itself.
# ---------------------------------------------------------------------------
entries = st.session_state["chat"]
verdict_positions = [i for i, e in enumerate(entries) if e["kind"] == "verdict"]
ask_positions = [i for i, e in enumerate(entries) if e["kind"] == "ask_after"]
newest_verdict = verdict_positions[-1] if verdict_positions else -1
newest_ask = ask_positions[-1] if ask_positions else -1

for index, entry in enumerate(entries):
    avatar = "🛡️" if entry["who"] == "assistant" else "🙂"
    with st.chat_message(entry["who"], avatar=avatar):
        if entry["kind"] == "verdict":
            draw_verdict(entry["result"], with_audio=index == newest_verdict)
        elif entry["kind"] == "ask_after":
            st.markdown(entry["text"])
            # Only the newest unanswered question gets live buttons.
            if index == newest_ask and st.session_state["phase"] == "after":
                yes, no = st.columns(2)
                if no.button("No, I have not", key=f"reply_no_{index}", width="stretch"):
                    resolve_answer(entry, replied=False)
                    st.rerun()
                if yes.button("Yes, I did", key=f"reply_yes_{index}", width="stretch"):
                    resolve_answer(entry, replied=True)
                    st.rerun()
        else:
            st.markdown(entry["text"])

# Example buttons, only before the first check.
if st.session_state["phase"] == "start":
    st.caption("No message to hand? Try one of these.")
    example_columns = st.columns(3)
    for index, (label, text) in enumerate(EXAMPLES):
        with example_columns[index]:
            if st.button(label, width="stretch", key=f"example_{index}"):
                add("user", "text", text=text)
                check_message(text)
                st.rerun()

# ---------------------------------------------------------------------------
# Footer — the honest limit of the tool (requirement T3).
# ---------------------------------------------------------------------------
st.caption(rt.FOOTER)
st.caption(
    "🔧 Demo version: the answers on this screen are placeholders until the "
    "team's analysis service is connected."
)

# ---------------------------------------------------------------------------
# The input. One box, used for both a pasted message and a question.
# ---------------------------------------------------------------------------
typed = st.chat_input("Paste the message here, or ask a question")
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
