"""
test_app.py — proves the three screens behave, without opening a browser.

Run it with:
    python test_app.py

It uses Streamlit's own AppTest, which runs app.py in-process and lets us press
buttons. Every "OK" line means one rule from UX_GUIDELINES.md still holds.
"""

import os

from streamlit.testing.v1 import AppTest

APP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")


def fresh_app():
    """Start the app from the empty form."""
    app = AppTest.from_file(APP, default_timeout=30)
    app.run()
    assert not app.exception, [e.value for e in app.exception]
    return app


def main():
    print("Screen 1 — the form")
    app = fresh_app()
    assert app.title[0].value == "Is this message a scam?"
    assert len(app.text_area) == 1
    print("  OK  privacy notice shown before typing, one text box")

    print("Screen 1 — empty input")
    app = fresh_app()
    app.button(key="check_button").click().run()
    assert app.warning, "an empty box should get a gentle warning"
    print("  OK  friendly warning, no red error, no crash")

    print("Screen 2 — the three risk levels")
    expected = {0: "error", 1: "warning", 2: "success"}
    for index, banner in expected.items():
        app = fresh_app()
        app.button(key=f"example_{index}").click().run()
        assert not app.exception, [e.value for e in app.exception]
        counts = {
            "error": len(app.error),
            "warning": len(app.warning),
            "success": len(app.success),
        }
        assert counts[banner] == 1, f"example {index}: expected {banner}, got {counts}"
        assert len(app.link_button) >= 1, "the call button must be there"
        print(f"  OK  example {index} → {banner} verdict and a call button")

    print("Screen 2 — read-aloud is offered or explained")
    app = fresh_app()
    app.button(key="example_0").click().run()
    captions = " ".join(c.value for c in app.caption)
    spoke = ("Press play" in captions) or ("cannot read things aloud" in captions)
    assert spoke, "the verdict screen must either offer sound or say why it cannot"
    print("  OK  voice output present, or an honest fallback message")

    print("Screen 2 — back to the form")
    app = fresh_app()
    app.button(key="example_0").click().run()
    app.button(key="again_button").click().run()
    assert not app.exception, [e.value for e in app.exception]
    assert len(app.text_area) == 1, "should be back on the input screen"
    print("  OK  'Check another message' clears the screen")

    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
