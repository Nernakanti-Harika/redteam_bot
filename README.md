# Red Team Bot
Tests your OWN chatbot for weak spots: prompt injection, system-prompt leakage, jailbreaks,
sensitive data leakage, hallucination, toxicity and inconsistent refusals. Python 3.11.9.

## Setup
    python3.11 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    cp .env.example .env     # add GEMINI_API_KEY only if using Gemini targets
    streamlit run app.py

## Demo
1. Scan **Mock - weak** (high risk score).  2. Scan **Mock - hardened**.  3. Compare in "Before vs after".

## Structure
- `redteam/probes.py` probe library + mitigations (add your own probes here)
- `redteam/target.py` target bots (mock + Gemini); plug in your own by adding an `ask(prompt)` class
- `redteam/judge.py` rule-based pass/fail judge
- `redteam/runner.py` runs probes, summaries, risk score
- `app.py` Streamlit dashboard
