"""
test_app.py — proves the conversation behaves, without opening a browser.

Run it with:
    python test_app.py

It uses Streamlit's own AppTest, which runs app.py in-process and lets us press
buttons and type into the chat box. Every "OK" line maps to a rule in
UX_GUIDELINES.md or a requirement in the brief.
"""

import os

from streamlit.testing.v1 import AppTest

APP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")

BANK = "HSBC ALERT: A payment of $2,300 was detected. Confirm your identity now: http://hsbc-verify.top"


def fresh():
    app = AppTest.from_file(APP, default_timeout=30)
    app.run()
    assert not app.exception, [e.value for e in app.exception]
    return app


def texts(app):
    """Everything the app is currently showing as text (any element type)."""
    parts = []
    for group in (app.markdown, app.subheader, app.caption, app.text, app.title):
        parts.extend(item.value for item in group)
    return " ".join(parts)


def press(app, key):
    for button in app.button:
        if button.key == key:
            button.click().run()
            return app
    raise AssertionError(f"no button with key {key}")


def press_prefix(app, prefix):
    """The Yes/No buttons are keyed by their position, so match the prefix."""
    for button in app.button:
        if button.key and button.key.startswith(prefix):
            button.click().run()
            return app
    raise AssertionError(f"no button starting with {prefix}")


def say(app, message):
    app.chat_input[0].set_value(message).run()
    return app


def check_screen_one():
    app = fresh()
    assert app.title[0].value == "Is this message a scam?"
    assert len(app.chat_input) == 1, "there should be one chat box"
    assert "not saved" in texts(app), "privacy notice must be visible first"
    assert "Hello" in texts(app), "the assistant should greet the user"
    print("  OK  greeting, privacy notice, one chat box")


def check_empty_input_guard():
    app = fresh()
    say(app, "hi")
    assert "do not see a message there" in texts(app)
    print("  OK  short nonsense gets a helpful nudge, not a fake verdict")


def check_message_verdict():
    app = fresh()
    say(app, BANK)
    assert app.error, "a bank scam should produce the red verdict"
    assert "Why we think so" in texts(app)
    assert "What to do now" in texts(app)
    assert "already replied" in texts(app), "the follow-up question must appear"
    print("  OK  pasted message → verdict card → follow-up question")


def check_follow_up_no():
    app = fresh()
    say(app, BANK)
    press_prefix(app, "reply_no_")
    assert "You answered" in texts(app)
    assert "Do not reply to it" in texts(app)
    print("  OK  answering 'No' gives the calm reminder")


def check_follow_up_yes():
    app = fresh()
    say(app, BANK)
    press_prefix(app, "reply_yes_")
    assert "Please call your bank now" in texts(app)
    assert "18222" in texts(app)
    print("  OK  answering 'Yes' gives the emergency script")


def check_example_buttons():
    app = fresh()
    press(app, "example_0")
    assert app.error, "the bank example should be high risk"
    print("  OK  example button still works inside the chat")


def check_intents():
    app = fresh()
    say(app, BANK)
    app = say(app, "what is 18222")
    assert "Anti-Scam Helpline" in texts(app)
    app = say(app, "i clicked the link")
    assert "Close the page now" in texts(app)
    print("  OK  typed questions are answered from intents")


def check_unknown_question():
    app = fresh()
    say(app, BANK)
    say(app, "what is the weather in hong kong tomorrow")
    assert "not sure about that one" in texts(app)
    print("  OK  an unknown question gets an honest 'I do not know'")


def check_three_levels():
    app = fresh()
    press(app, "example_0")
    assert len(app.error) == 1
    app = fresh()
    press(app, "example_1")
    assert len(app.warning) == 1
    app = fresh()
    press(app, "example_2")
    assert len(app.success) == 1
    print("  OK  the three examples still hit red, amber and green")


def check_voice_or_honesty():
    app = fresh()
    press(app, "example_0")
    captions = " ".join(c.value for c in app.caption)
    assert ("Press play" in captions) or ("cannot read things aloud" in captions)
    print("  OK  read-aloud is offered, or the reason is stated plainly")


def main():
    print("Conversation")
    checks = [
        check_screen_one,
        check_empty_input_guard,
        check_message_verdict,
        check_follow_up_no,
        check_follow_up_yes,
        check_example_buttons,
        check_intents,
        check_unknown_question,
        check_three_levels,
        check_voice_or_honesty,
    ]
    for check in checks:
        check()
    print("\nAll checks passed.")


if __name__ == "__main__":
    main()

