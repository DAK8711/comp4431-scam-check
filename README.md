# Scam Check — frontend (COMP4431, E1)

A chatbot for elderly users: paste a suspicious message, get a plain-language risk
level, three reasons, three next steps, one follow-up question, and someone to call.

**Status:** working conversation. The risk answers are **fake** (keyword rules in
`fake_analyzer.py`) until the team's analysis service is connected.

## How the conversation goes

```
assistant  Hello. Are you worried about a message you received?
you        [paste the message]
assistant  Let me check that for you.  →  verdict card
assistant  Have you already replied to it, or sent any money?
you        [No, I have not]  or  [Yes, I did]
assistant  calm reminder      or  emergency script (call the bank now)
```

After that you can type questions like *"should I call the number?"*, *"I clicked the
link"*, *"what is 18222?"* — eight of them are answered from `intents.py`. Anything else
gets an honest "I am not sure, please call 18222" rather than an invented answer.

---

## Run it

You need Python 3.10+ and Streamlit. On this machine both are already installed.

```powershell
cd C:\Users\danie\Documents\deepseek-harness\default-workspace\comp4431
$py = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
& $py -m streamlit run app.py
```

The browser opens at `http://localhost:8501`. Stop the server with `Ctrl+C`.

If `python` works normally on your machine, this is enough:

```powershell
python -m streamlit run app.py
```

## Check it works

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" test_app.py
```

Six lines of `OK` means the app still behaves: privacy notice first, gentle empty-input
warning, three correct verdicts, and the "check another" reset. This is also your evidence
for the report's testing paragraph.

## Files

| File | What it is | Whose |
|---|---|---|
| `app.py` | the conversation, every bubble, every button | E1 |
| `intents.py` | the eight questions the assistant can answer | E1 |
| `response_templates.py` | all the wording — the only file to edit for copy changes | E1 |
| `.streamlit/config.toml` | theme: 22px text, colours, button radius | E1 |
| `UX_GUIDELINES.md` | the rules, numbered, citable in the report | E1 |
| `API_CONTRACT.md` | the JSON handshake with EarlyFat | E1 |
| `MEETING.md` | agenda and questions | E1 |
| `test_app.py` | automated checks, no browser needed | E1 |
| `speech.py` + `speech.ps1` | read-aloud using the voices built into Windows | E1 |
| `fake_analyzer.py` | **placeholder** keyword rules returning made-up answers | to be deleted |

## The three demo messages

The three buttons under the text box load these:

1. **A bank text** → high risk (urgency + money + impersonation)
2. **A parcel text** → medium risk
3. **A message from family** → low risk

## Screenshots

Open these four addresses and screenshot each one. `?demo=high` starts the app on that
verdict so you do not have to type anything.

```
http://localhost:8501/                empty form
http://localhost:8501/?demo=high      red verdict
http://localhost:8501/?demo=medium    amber verdict
http://localhost:8501/?demo=low       green verdict
```

On Windows: `Win + Shift + S` for a region shot, or `Alt + PrtScn` for the window.

## Connect the real backend later

In `fake_analyzer.py`:

```python
USE_REAL_API = True
API_URL = "http://127.0.0.1:8000/analyze"
```

Nothing else changes, because the return shape is fixed in `API_CONTRACT.md`.

## Voice output (F5)

Every verdict is spoken aloud, using the speech voices that ship with Windows. No API
key, no internet, no cost.

Test it on its own first — this prints a duration if it works:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" speech.py
```

- **Prints a duration** → voice is working. Delete the `spoken_test.wav` it leaves behind.
- **Prints "No speech available"** → the app still works; it shows a line telling the user
  to call 18222 instead of a dead play button. Tell me and I'll switch it to the browser's
  own speech engine.

What gets spoken is the verdict plus the first two instructions — about 8 seconds. Not the
whole screen: nobody listens to a 40-second reading.

## What is deliberately not built yet

- **Voice input** (F6) — `st.audio_input` records the user's voice, but turning that into
  text needs speech-to-text, which needs a key or a local model. That decision is next.
- **Language switch** (English / Chinese) — the demo is in English.
- Real detection of any kind.

## If something goes wrong

| Symptom | Cause | Fix |
|---|---|---|
| `streamlit: command not found` | Streamlit not installed for that Python | `python -m pip install streamlit` |
| `ModuleNotFoundError: streamlit` | wrong interpreter | use the full path shown above |
| App opens but fonts look wrong | offline, the Atkinson Hyperlegible font did not load | harmless, it falls back to a system font |
| Port already in use | another Streamlit is running | `python -m streamlit run app.py --server.port 8502` |

## Academic integrity

The fake analyser is a placeholder written by E1 and is clearly labelled as such in the
file itself. No teammate's detection or scoring work is reproduced here. If the course
requires disclosure of AI assistance, say so in the report: the interface, wording and
documents were drafted with AI assistance and reviewed by E1.
