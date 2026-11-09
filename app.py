"""
app.py — the scam-checking chatbot interface
============================================
This is E1's part of COMP4431: everything the elderly user sees and touches.

How it works, in order:
    Screen 1  the user pastes a message and presses one big button
    Screen 2  the app shows a risk level, why, what to do, and who to call

All the wording lives in response_templates.py.
All the "detection" lives in fake_analyzer.py, which is a placeholder.

Run it with:
    python -m streamlit run app.py
"""

import streamlit as st

import response_templates as rt
import speech
from fake_analyzer import EXAMPLES, AnalysisError, analyze

# ---------------------------------------------------------------------------
# Page setup. "centered" keeps one column of text, which is what N6 asks for.
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Scam check",
    page_icon="🛡️",
    layout="centered",
)

# ---------------------------------------------------------------------------
# The only custom CSS in the app, and it does one job: make the buttons taller
# than Streamlit's default, because N3 requires at least 48px of finger room.
# Everything else (colours, font size, rounded corners) is set in
# .streamlit/config.toml, which is the supported way to theme Streamlit.
# ---------------------------------------------------------------------------
st.html(
    """
    <style>
      .st-key-check_button button,
      .st-key-again_button button {
          min-height: 68px;
          font-size: 1.15rem;
          font-weight: 700;
      }
      .st-key-example_0 button,
      .st-key-example_1 button,
      .st-key-example_2 button {
          min-height: 56px;
      }
    </style>
    """
)

# ---------------------------------------------------------------------------
# Session state: which screen we are on. Keeping the result here means the
# page can be refreshed without losing the verdict.
# ---------------------------------------------------------------------------
if "result" not in st.session_state:
    st.session_state["result"] = None

# Screenshot helper: opening the app with ?demo=high (or medium / low) starts on
# that verdict instead of the empty form. Used for slides and the report.
# It is applied once per session, so "Check another message" still works after.
_demo_level = st.query_params.get("demo", "")
if (
    st.session_state["result"] is None
    and _demo_level in ("high", "medium", "low")
    and not st.session_state.get("demo_applied")
):
    _index = {"high": 0, "medium": 1, "low": 2}[_demo_level]
    st.session_state["result"] = analyze(EXAMPLES[_index][1])
    st.session_state["demo_applied"] = True

# ---------------------------------------------------------------------------
# Header. It is identical on both screens so the user never feels lost.
# ---------------------------------------------------------------------------
st.title("Is this message a scam?")
st.markdown(rt.PRIVACY_NOTICE)
st.divider()


# ===========================================================================
# SCREEN 1 — ask for the message
# ===========================================================================
if st.session_state["result"] is None:

    message = st.text_area(
        "Paste the message here",
        key="message_box",
        height=200,
        placeholder=(
            "For example: a text message about a parcel, "
            "or an email saying your bank account is blocked."
        ),
    )

    check_pressed = st.button(
        "Check this message",
        type="primary",
        width="stretch",
        key="check_button",
        icon=":material/search:",
    )

    if check_pressed:
        if not message.strip():
            # Gentle, not a red error. An empty box is not a mistake worth shouting about.
            st.warning(
                "Please paste or type the message first.",
                icon=":material/edit_note:",
            )
        else:
            try:
                st.session_state["result"] = analyze(message)
                st.rerun()
            except AnalysisError:
                st.error(
                    "We could not check this message right now. "
                    "Please call the Anti-Scam Helpline on 18222.",
                    icon=":material/phone_in_talk:",
                    title="Sorry — something went wrong",
                )

    st.caption("No message to hand? Try one of these.")
    example_columns = st.columns(3)
    for index, (label, text) in enumerate(EXAMPLES):
        with example_columns[index]:
            if st.button(label, width="stretch", key=f"example_{index}"):
                try:
                    st.session_state["result"] = analyze(text)
                    st.rerun()
                except AnalysisError:
                    st.error(
                        "We could not check this message right now. "
                        "Please call the Anti-Scam Helpline on 18222."
                    )


# ===========================================================================
# SCREEN 2 — the verdict
# ===========================================================================
else:
    result = st.session_state["result"]
    level = str(result.get("risk_level", "medium")).lower()
    template = rt.template_for(level)

    # The verdict banner: one coloured block, one sentence, no jargon.
    alert = {"high": st.error, "medium": st.warning, "low": st.success}.get(
        level, st.warning
    )
    alert(
        template["body"],
        title=f"{template['icon']} {template['headline']}",
    )

    # Voice output (F5). The player is the native Streamlit one, so there is
    # nothing to break: if this computer has no speech voice, the warning is
    # still readable and we say so plainly instead of showing a dead button.
    st.subheader("Hear it read aloud")
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

    # Why we think so. Maximum three short reasons.
    with st.container(border=True):
        st.subheader("Why we think so")
        for reason in rt.plain_reasons(result.get("matched_patterns")):
            st.markdown(f"- {reason}")

    # What to do now. Numbered, because the order matters.
    st.subheader("What to do now")
    for number, step in enumerate(template["steps"], start=1):
        st.markdown(f"**{number}.** {step}")

    # Who to call. A phone icon and a tap target, not a wall of text.
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

    st.divider()

    if st.button(
        "Check another message",
        width="stretch",
        key="again_button",
        icon=":material/refresh:",
    ):
        st.session_state["result"] = None
        st.session_state.pop("message_box", None)  # clears the text box as well
        st.rerun()


# ---------------------------------------------------------------------------
# Footer: the honest limit of what this tool can do (requirement T3).
# ---------------------------------------------------------------------------
st.caption(rt.FOOTER)
st.caption(
    "🔧 Demo version: the answers on this screen are placeholders until the "
    "team's analysis service is connected."
)
