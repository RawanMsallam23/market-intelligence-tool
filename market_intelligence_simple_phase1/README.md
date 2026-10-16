Market Intelligence & Competitor Analysis Tool

Project Overview

Market Intelligence & Competitor Analysis Tool is a Python-based web application built with Streamlit. It helps businesses research competing mobile applications on the Google Play Store, compare customer feedback, identify recurring complaints, and discover potential market opportunities.

The application combines Google Play data collection, sentiment classification, interactive visualizations, SQLite storage, Excel reporting, and Google Gemini AI analysis.

Key Features

1. Google Play Competitor Discovery

- Search applications by keyword, app name, or category.
- Choose the Google Play storefront country and language.
- Display application icons, developers, and ratings.
- Add applications manually using a Google Play link or App ID.
- Select between 2 and 4 competitors for analysis.

2. Customer Review Collection

- Retrieve up to 200 recent reviews per selected application, depending on availability.
- Extract review ratings, text, usernames, and timestamps.
- Prepare review data for comparison and analysis.

3. Sentiment Analysis

Classify customer reviews using their star ratings:

- Positive: 4–5 stars
- Neutral: 3 stars
- Negative: 1–2 stars

Sentiment categories are rating-based, rather than predictions from review text.

4. Interactive Dashboard

Use Plotly visualizations to display:

- Competitor rating comparisons.
- Sentiment distribution and percentages.
- Customer satisfaction by competitor.
- Most frequently used words in negative reviews.

The dashboard also includes interactive tables for reviewing customer complaints.

5. AI-Powered Market Gap Analysis

Integrate Google Gemini AI to analyze negative customer reviews.

The system processes reviews in chunks and generates an executive-level report highlighting:

- Recurring customer complaints and technical issues.
- Features explicitly requested by customers.
- Potential market gaps.
- Strategic product recommendations.

AI availability depends on the Gemini API service and account usage limits.

6. SQLite Database

Store competitor and customer review information in a local SQLite database:

"competitor_intelligence.db"

The database supports structured storage and avoids duplicate review IDs.

7. Excel Report Export

Generate and download a formatted Excel report containing three worksheets:

1. Competitors
2. Customer Reviews
3. Sentiment Summary

Reports can be filtered to include only the selected competitors.

Technologies Used

Technology| Purpose
Python| Core programming language
Streamlit| Interactive web interface
google-play-scraper| Google Play data collection
Pandas| Data processing and cleaning
Plotly| Interactive visualizations
SQLite| Relational data storage
OpenPyXL| Excel report generation and formatting
Google Gemini API| AI-powered customer feedback analysis

Installation and Local Setup

1. Clone the GitHub repository

git clone https://github.com/RawanMsallam23/market-intelligence-tool.git

2. Open the application directory

cd market-intelligence-tool\market_intelligence_simple_phase1

3. Create and activate a virtual environment

py -m venv .venv
.\.venv\Scripts\Activate.ps1

4. Install dependencies

python -m pip install -r requirements.txt

5. Configure Gemini API

Create a file named "secrets.toml" inside a ".streamlit" directory.

Add:

GEMINI_API_KEY = "YOUR_API_KEY"

Replace the placeholder with your own Gemini API key.

Never commit API keys or "secrets.toml" to GitHub.

6. Run the application

python -m streamlit run app1.py

Open the local URL provided by Streamlit, typically:

"http://localhost:8501"

Live Application

Streamlit Application:

https://rawan-market-intelligence.streamlit.app

GitHub Repository:

https://github.com/RawanMsallam23/market-intelligence-tool

Deployment

The application is deployed using Streamlit Community Cloud.

Deployment configuration:

- Repository: "RawanMsallam23/market-intelligence-tool"
- Branch: "main"
- Main file: "market_intelligence_simple_phase1/app1.py"

The Gemini API key must be configured separately in Streamlit Cloud Secrets.

Important Notes and Limitations

- Google Play storefront settings do not establish the geographic locations of reviewers.
- The number of available reviews may vary between applications.
- Sentiment classification is based on star ratings.
- Gemini AI output should be reviewed and validated against original customer feedback.
- Gemini API requests are subject to quota limits and temporary service availability.
- SQLite data stored on Streamlit Community Cloud may not persist across application restarts.

Project Purpose

The project provides an accessible competitor intelligence solution for businesses preparing to develop or launch a mobile application.

By combining customer feedback analysis, competitor comparisons, and AI-generated insights, the system supports informed product planning and strategic decision-making.
