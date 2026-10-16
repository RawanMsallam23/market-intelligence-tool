import sqlite3
import pandas as pd
from io import BytesIO
from openpyxl.styles import Font, PatternFill, Alignment

DB_NAME = "competitor_intelligence.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS apps (
                app_id TEXT PRIMARY KEY,
                title TEXT,
                developer TEXT,
                rating REAL,
                category TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                review_id TEXT PRIMARY KEY,
                app_id TEXT,
                app_name TEXT,
                user_name TEXT,
                score INTEGER,
                content TEXT,
                review_date TEXT,
                sentiment TEXT
            )
        """)

def save_apps(selected):
    init_db()

    with sqlite3.connect(DB_NAME) as conn:
        for item in selected:
            conn.execute("""
                INSERT OR REPLACE INTO apps
                (app_id, title, developer, rating, category)
                VALUES (?, ?, ?, ?, ?)
            """, (
                item.get("appId"),
                item.get("title"),
                item.get("developer"),
                item.get("score"),
                item.get("genre") or "Not specified"
            ))
def save_reviews(rows):
     init_db()
     saved = 0

     with sqlite3.connect(DB_NAME) as conn:
        for review in rows:
            review_id = review.get("reviewId")
            if not review_id:
                continue

            score = review.get("score")
            sentiment = (
                "Positive" if score >= 4
                else "Neutral" if score == 3
                else "Negative"
            )

            conn.execute("""
                INSERT OR REPLACE INTO reviews
                (review_id, app_id, app_name, user_name,
                score, content, review_date, sentiment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                review_id,
                review.get("appId"),
                review.get("App"),
                review.get("userName"),
                score,
                review.get("content"),
                str(review.get("at")),
                sentiment
            ))
            saved += 1

     return saved
def create_excel_report(selected_ids=None):

    with sqlite3.connect(DB_NAME) as conn:

        competitors = pd.read_sql_query(
            'SELECT * FROM apps', conn
        )

        customer_reviews = pd.read_sql_query(
            'SELECT * FROM reviews', conn
        )

        sentiment_summary = pd.read_sql_query("""
            SELECT
                app_id AS "App ID",
                app_name AS App,
                COUNT(*) AS Total_Reviews,
                SUM(CASE WHEN sentiment = 'Positive' THEN 1 ELSE 0 END) AS Positive,
                SUM(CASE WHEN sentiment = 'Neutral' THEN 1 ELSE 0 END) AS Neutral,
                SUM(CASE WHEN sentiment = 'Negative' THEN 1 ELSE 0 END) AS Negative
            FROM reviews
            GROUP BY app_id, app_name
        """, conn)
        # Filter report by selected competitors
        if selected_ids is not None:
            competitors = competitors[
                competitors["app_id"].isin(selected_ids)
            ]

            customer_reviews = customer_reviews[
                customer_reviews["app_id"].isin(selected_ids)
            ]

            sentiment_summary = sentiment_summary[
                sentiment_summary["App ID"].isin(selected_ids)
            ]

        sentiment_summary = sentiment_summary.drop(columns=["App ID"])

        # Protect Excel from interpreting review text as formulas
        for column in ["content", "user_name", "app_name"]:
            customer_reviews[column] = customer_reviews[column].apply(
                lambda value: "'" + value
                if isinstance(value, str) and value.startswith("=")
                else value
            )

        output = BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:

            competitors.to_excel(
                writer, sheet_name="Competitors", index=False
            )

            customer_reviews.to_excel(
                writer, sheet_name="Customer Reviews", index=False
            )

            sentiment_summary.to_excel(
                writer, sheet_name="Sentiment Summary", index=False
            )
        # Format Excel sheets
        for sheet in writer.sheets.values():

            sheet.freeze_panes = "A2"
            sheet.auto_filter.ref = sheet.dimensions
            sheet.row_dimensions[1].height = 28

            # Style headers
            for cell in sheet[1]:
                cell.fill = PatternFill(
                    fill_type="solid",
                    fgColor="16213D"
                )
                cell.font = Font(
                    color="FFFFFF",
                    bold=True
                )
                cell.alignment = Alignment(
                    horizontal="center",
                    vertical="center"
                )

            # Adjust column widths
            for column in sheet.columns:
                letter = column[0].column_letter
                header = str(column[0].value).lower()

                max_width = max(
                    len(str(cell.value or ""))
                    for cell in column
                )

                sheet.column_dimensions[letter].width = (
                    48 if header == "content"
                    else min(max(max_width + 2, 14), 32)
                )

    return output.getvalue()
if __name__ == "__main__":
    init_db()
    print("Database created successfully!")