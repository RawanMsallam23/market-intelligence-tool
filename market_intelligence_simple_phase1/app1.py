import streamlit as st
import pandas as pd
import plotly.express as px
from market_ai import analyze_reviews, analyze_all_complaints
from google_play_scraper import search, app, reviews, Sort
from urllib.parse import urlparse, parse_qs
from market_engine import save_apps, save_reviews, create_excel_report



st.set_page_config(page_title="Competitor Analysis", layout="wide")
st.title("Google Play Competitor Analysis")
st.write("Search for apps, compare 2–4 competitors, and analyze customer reviews.")

# Keep results when Streamlit refreshes the page
if "apps" not in st.session_state:
    st.session_state.apps = []

# 2. Search Google Play
keyword = st.text_input("Search for apps", "delivery")
col1, col2 = st.columns(2)
with col1:
    language = st.selectbox("Language", ["en", "ar"])
with col2:
    country = st.selectbox("Store country", ["ps", "us", "jo", "sa"])

if st.button("Search Google Play"):
    if not keyword.strip():
        st.warning("Please enter a search keyword.")
    else:
        try:
            found = search(keyword, lang=language, country=country, n_hits=18)
            st.session_state.apps = found
            for item in found:
                if item.get("appId"):
                    st.session_state[f"pick_{item['appId']}"] = False
        except Exception as error:
            st.error(f"Search failed: {error}")

# 3. Add an app that did not appear in the search
with st.expander("Add an app using its Google Play link"):
    app_link = st.text_input("Google Play link or App ID")
    if st.button("Add app"):
        try:
            app_id = app_link.strip()
            if app_id.startswith(("https://", "http://")):
                link = urlparse(app_id)
                if link.hostname not in ("play.google.com", "www.play.google.com"):
                    raise ValueError("Please enter a Google Play link.")
                app_id = parse_qs(link.query).get("id", [""])[0]
            if not app_id:
                raise ValueError("Enter a valid App ID or Google Play link.")
            details = app(app_id, lang=language, country=country)
            ids = [item.get("appId") for item in st.session_state.apps]
            if app_id not in ids:
                st.session_state.apps.append(details)
                st.success("App added successfully.")
            else:
                st.info("This app is already in the list.")
        except Exception as error:
            st.error(f"Could not add the app: {error}")

# 4. Show apps and let the user select competitors
selected = []
if st.session_state.apps:
    st.subheader("Select competitors (2–4 apps)")
    for item in st.session_state.apps:
        app_id = item.get("appId")
        if not app_id:
            continue
        c1, c2, c3 = st.columns([1, 5, 2])
        with c1:
            if item.get("icon"):
                st.image(item["icon"], width=55)
        with c2:
            st.write(f"**{item.get('title') or app_id}**")
            st.caption(f"Developer: {item.get('developer') or 'N/A'} | Rating: {item.get('score') if item.get('score') is not None else 'N/A'}")
            st.markdown(f"[Open on Google Play](https://play.google.com/store/apps/details?id={app_id})")
        with c3:
            if st.checkbox("Compare", key=f"pick_{app_id}"):
                selected.append(item)

    st.write(f"Selected: {len(selected)} apps")

    # 5. Compare and download results
    if len(selected) > 4:
        st.error("Please select no more than 4 apps.")
    elif len(selected) >= 2:
        df = pd.DataFrame(selected)
        df["score"] = pd.to_numeric(df["score"], errors="coerce")
        if "genre" not in df.columns:
            df["genre"] = "Not specified"
        comparison = df[["title", "developer", "score", "genre", "appId"]].copy()
        comparison.columns = ["App", "Developer", "Rating", "Category", "App ID"]
        # Competitor Overview
        st.subheader("Competitor Overview")

        valid_ratings = comparison["Rating"].dropna()

        kpi1, kpi2, kpi3 = st.columns(3)

        with kpi1:
            st.metric("Selected Apps", len(selected))

        with kpi2:
            if not valid_ratings.empty:
                st.metric("Average Rating", f"{valid_ratings.mean():.2f} / 5")
            else:
                st.metric("Average Rating", "N/A")

        with kpi3:
            if not valid_ratings.empty:
                st.metric("Highest Rating", f"{valid_ratings.max():.2f} / 5")
            else:
                st.metric("Highest Rating", "N/A")

        # Competitor Ratings Comparison
        st.subheader("Competitor Ratings Comparison")

        chart_data = comparison.dropna(subset=["Rating"])
        chart_data = chart_data.sort_values("Rating")

        if not chart_data.empty:

            # Choose colors based on rating
            colors = []

            for rating in chart_data["Rating"]:
                if rating >= 4:
                    colors.append("#22C55E")  # Green
                elif rating >= 3:
                    colors.append("#F59E0B")  # Orange
                else:
                    colors.append("#EF4444")  # Red

            # Horizontal Bar Chart
            fig = px.bar(
                chart_data,
                x="Rating",
                y="App",
                orientation="h",
                text="Rating"
            )

            fig.update_traces(
                marker_color=colors,
                texttemplate="%{x:.2f} ★",
                textposition="inside",
                textfont_color="white"
            )

            fig.update_layout(
                xaxis_title="Rating (out of 5)",
                yaxis_title=None,
                xaxis=dict(
                    range=[0, 5],
                    dtick=1,
                    gridcolor="#E5E7EB"
                ),
                plot_bgcolor="white",
                showlegend=False,
                height=250,
                bargap=0.55
            )

            # st.plotly_chart(fig, use_container_width=True)
            left, middle, right = st.columns([1, 5, 1])

            with middle:
                st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("No ratings available.")

        # Detailed Competitor Comparison
        with st.expander("View Detailed Comparison Table"):

            st.dataframe(comparison, use_container_width=True)

            st.download_button(
                "Download CSV",
                comparison.to_csv(index=False).encode("utf-8-sig"),
                file_name="selected_competitors.csv",
                mime="text/csv"
            )

        # 6. Fetch recent customer reviews for the selected apps
        st.subheader("Customer reviews")
        selected_ids = tuple(sorted(item["appId"] for item in selected))
        review_key = (selected_ids, language, country)

        if st.button("Fetch Customer Reviews"):
            save_apps(selected)
            st.success("Selected competitors saved to SQLite!") 
            rows = []
            with st.spinner("Collecting customer reviews..."):
                for item in selected:
                    try:
                        app_reviews, _ = reviews(
                            item["appId"], lang=language, country=country,
                            sort=Sort.NEWEST, count=200
                        )
                        for review in app_reviews:
                            rows.append({
                                "App": item["title"],
                                "userName": review.get("userName"),
                                "score": review.get("score"),
                                "content": review.get("content"),
                                "at": review.get("at"),
                                "reviewId": review.get("reviewId"),
                                "appId": item["appId"],
                            })
                    except Exception as error:
                        st.warning(f"Reviews not available for {item['title']}: {error}")
            st.session_state.reviews_df = pd.DataFrame(rows)
            saved_count = save_reviews(rows)
            st.success(f"{saved_count} reviews saved to SQLite!")
            st.session_state.review_key = review_key

        # Keep the results visible when Streamlit reruns the page
        if st.session_state.get("review_key") == review_key:
            reviews_df = st.session_state.reviews_df
            if reviews_df.empty:
                st.warning("No reviews were returned for these apps.")
            else:
                st.write(f"Reviews collected: {len(reviews_df)}")
                # تجهيز عمود التقييم
                reviews_df = reviews_df.copy()

                reviews_df["score"] = pd.to_numeric(
                    reviews_df["score"], errors="coerce"
                )

                # حذف المراجعات التي لا تحتوي على تقييم صالح
                reviews_df = reviews_df.dropna(subset=["score"])

                # تصنيف المراجعات حسب عدد النجوم
                reviews_df["Sentiment"] = reviews_df["score"].apply(
                    lambda s: "Positive" if s >= 4 else (
                        "Neutral" if s == 3 else "Negative"
                    )
                )

                                # ألوان المشاعر
                colors = {
                    "Positive": "#1b974f",
                    "Neutral": "#ffa616",
                    "Negative": "#DF1903"
                }

               # Create tabs
                tab1, tab2 = st.tabs(["Sentiment Charts", "Customer Reviews"])

                with tab1:
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("Sentiment Distribution")

                        fig_bar = px.histogram(
                            reviews_df,
                            x="Sentiment",
                            color="Sentiment",
                            color_discrete_map=colors,
                            category_orders={
                                "Sentiment": ["Positive", "Neutral", "Negative"]
                            }
                        )

                        fig_bar.update_layout(
                            showlegend=False,
                            height=300,
                            xaxis_title=None,
                            yaxis_title="Number of Reviews"
                        )

                        st.plotly_chart(fig_bar, use_container_width=True)

                    with col2:
                        st.subheader("Sentiment Percentage")

                        fig_pie = px.pie(
                            reviews_df,
                            names="Sentiment",
                            hole=0.4,
                            color="Sentiment",
                            color_discrete_map=colors
                        )

                        fig_pie.update_layout(height=300)

                        st.plotly_chart(fig_pie, use_container_width=True)
                        
                        # Customer Satisfaction by Competitor
                    st.subheader("Customer Satisfaction by Competitor")

                    sentiment_comparison = (
                        reviews_df.groupby(["App", "Sentiment"])
                        .size()
                        .reset_index(name="Reviews")
                    )

                    # Calculate percentages
                    sentiment_comparison["Percentage"] = (
                        sentiment_comparison["Reviews"] /
                        sentiment_comparison.groupby("App")["Reviews"].transform("sum")
                    ) * 100

                    # Create comparison chart
                    fig_comparison = px.bar(
                        sentiment_comparison,
                        x="Percentage",
                        y="App",
                        color="Sentiment",
                        orientation="h",
                        barmode="stack",
                        text="Percentage",
                        color_discrete_map=colors,
                        category_orders={
                            "Sentiment": ["Positive", "Neutral", "Negative"]
                        },
                        hover_data=["Reviews"]
                    )

                    fig_comparison.update_traces(
                        texttemplate="%{x:.0f}%",
                        textposition="inside"
                    )

                    fig_comparison.update_layout(
                        height=320,
                        xaxis_range=[0, 100],
                        xaxis_title="Percentage of Reviews",
                        yaxis_title=None,
                        plot_bgcolor="white",
                        legend_title_text=""
                    )

                    st.plotly_chart(fig_comparison, use_container_width=True)
                           # Most Common Words in Negative Reviews
                    st.subheader("Most Common Words in Negative Reviews")

                    negative_df = reviews_df[reviews_df["Sentiment"] == "Negative"]

                    words = (
                        negative_df["content"]
                        .fillna("")
                        .str.lower()
                        .str.replace(r"[^\w\s]", " ", regex=True)
                        .str.split()
                        .explode()
                    )

                    # Remove common words
                    stop_words = [
                        "the", "and", "for", "this", "app",
                        "من", "في", "على", "هذا", "هذه", "كان", "بس"
                    ]

                    words = words[words.str.len() >= 3]
                    words = words[~words.isin(stop_words)]

                    top_words = words.value_counts().head(10)

                    # Most Common Words Chart
                    if not top_words.empty:

                        words_df = top_words.rename_axis("Word").reset_index(name="Count")

                        words_df = words_df.sort_values("Count")

                        fig_words = px.bar(
                            words_df,
                            x="Count",
                            y="Word",
                            orientation="h",
                            text="Count",
                            color_discrete_sequence=["#DF1903"]
                        )

                        fig_words.update_traces(
                            textposition="outside"
                        )

                        fig_words.update_layout(
                            height=350,
                            xaxis_title="Number of Mentions",
                            yaxis_title=None,
                            plot_bgcolor="white",
                            showlegend=False
                        )

                        st.plotly_chart(fig_words, use_container_width=True)

                    else:
                        st.info("No negative review words available.")
                        # Customer Pain Points
                    st.subheader("Customer Pain Points")

                    # Select negative reviews
                    complaints = reviews_df[reviews_df["score"] <= 2].copy()

                    # Remove reviews without text
                    complaints = complaints.dropna(subset=["content"])
                    complaints = complaints[complaints["content"].str.strip() != ""]

                    if not complaints.empty:

                        tab3, tab4 = st.tabs([
                            "Negative Reviews by Competitor",
                            "Customer Complaints"
                        ])

                        with tab3:
                            complaint_counts = complaints.groupby("App").size()

                            st.dataframe(
                                complaint_counts.reset_index(name="Negative Reviews"),
                                use_container_width=True,
                                hide_index=True
                            )

                        with tab4:
                            st.dataframe(
                                complaints[["App", "score", "content"]],
                                use_container_width=True,
                                hide_index=True
                            )
                            if st.button("Analyze Complaints with Gemini"):
                                try:
                                    with st.spinner("Gemini is analyzing all negative reviews..."):
                                        analysis = analyze_all_complaints(
                                            complaints,
                                            st.secrets["GEMINI_API_KEY"]
                                        )

                                    st.markdown(analysis)

                                except Exception as error:
                                    if "429" in str(error):
                                        st.warning("Gemini API quota reached. Please try again after the quota resets.")
                                    elif "503" in str(error):
                                        st.warning("Gemini is temporarily busy. Please try again later.")
                                    else:
                                        st.error("Gemini analysis failed. Please try again later.")

                    else:
                        st.info("No negative reviews with text available.")
                    with tab2:
                        st.subheader("Customer Reviews")

                        st.dataframe(reviews_df, use_container_width=True)

                        st.download_button(
                            "Download Reviews CSV",
                            reviews_df.to_csv(index=False).encode("utf-8-sig"),
                            file_name="competitor_reviews.csv",
                            mime="text/csv"
                        )
                        st.download_button(
                            label="Download Excel Report",
                            data=create_excel_report([item["appId"] for item in selected]),
                            file_name="competitor_intelligence_report.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
    else:
        st.info("Select at least 2 apps to see the comparison.")
else:
    st.info("Search for apps or add one from a Google Play link to begin.")

st.caption("Store country controls Google Play storefront results; it does not identify the reviewers' location.")
