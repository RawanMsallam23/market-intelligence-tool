# Simple Market Intelligence – Phase 1

A simple Streamlit app that searches Google Play and lets a client compare 2–4 competitors using their public app store ratings.

## Setup (Windows / VS Code)

1. Open this project folder (the folder containing `app.py`) in VS Code.
2. In the terminal, run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If PowerShell blocks activation, run the following directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Current functionality

- Search Google Play by keyword (English or Arabic; configurable country storefront).
- Add a missing app via its Google Play link or app ID.
- Display the app icon, developer, and rating.
- Select 2–4 apps, plot their app-store rating comparison, and download a CSV file.

## Not yet implemented

Review scraping (150–300 reviews per app), sentiment analysis, word frequency, SQLite, Excel, Gemini. These belong to the next phases of the full assignment.

**Note:** A Google Play storefront locale is **not** proof of the geographic location of reviewers or local delivery coverage.
