# Pathways — AI accessibility navigation assistant

A polished Streamlit prototype for exploring accessible routes at a sample venue. Visitors can choose a start and destination, personalize a route using mobility and sensory preferences, and review clear, step-by-step directions.

## Run locally

Requires Python 3.9 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit (usually `http://localhost:8501`).

## What is included

- Route planning across six sample venue locations.
- Preference-aware routing for step-free paths, stairs, steep slopes, and quieter paths.
- Estimated travel time and distance, route overview, and plain-language directions.
- A venue directory with example accessibility information.
- Privacy, accessibility, and prototype-safety notes in the app.

## Scope and limitations

This is a self-contained prototype, not a live navigation service. The route recommendation is calculated locally using the sample pathway graph and selected preferences; it does not call an external AI model. There is no GPS, live map, or real-time information about closures, elevators, weather, or crowd levels. Replace the sample venue data in `app.py` with verified local data before using this for real-world navigation.
