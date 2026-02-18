import streamlit as st
import pandas as pd
from pathlib import Path

import preprocessor
import helper

import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns


# -----------------------------
# Robust file loading (fixes FileNotFoundError)
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent

@st.cache_data(show_spinner=False)
def load_data():
    df_ = pd.read_csv(BASE_DIR / "athlete_events.csv")
    region_df_ = pd.read_csv(BASE_DIR / "noc_regions.csv")
    df_ = preprocessor.preprocess(df_, region_df_)
    return df_

df = load_data()


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Olympics Analysis")

# Prefer local image if present; otherwise fall back to URL
local_logo_png = BASE_DIR / "Olympic_rings_without_rims.png"
if local_logo_png.exists():
    st.sidebar.image(str(local_logo_png))
else:
    st.sidebar.image(
        "https://e7.pngegg.com/pngimages/1020/402/png-clipart-2024-summer-olympics-brand-circle-area-olympic-rings-olympics-logo-text-sport.png"
    )

user_menu = st.sidebar.radio(
    "Select an Option",
    ("Medal Tally", "Overall Analysis", "Country-wise Analysis", "Athlete wise Analysis"),
)


# -----------------------------
# Medal Tally
# -----------------------------
if user_menu == "Medal Tally":
    st.sidebar.header("Medal Tally")
    years, country = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", country)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

    if selected_year == "Overall" and selected_country == "Overall":
        st.title("Overall Tally")
    elif selected_year != "Overall" and selected_country == "Overall":
        st.title(f"Medal Tally in {selected_year} Olympics")
    elif selected_year == "Overall" and selected_country != "Overall":
        st.title(f"{selected_country} overall performance")
    else:
        st.title(f"{selected_country} performance in {selected_year} Olympics")

    st.dataframe(medal_tally, use_container_width=True)


# -----------------------------
# Overall Analysis
# -----------------------------
if user_menu == "Overall Analysis":
    editions = df["Year"].nunique()
    cities = df["City"].nunique()
    sports = df["Sport"].nunique()
    events = df["Event"].nunique()
    athletes = df["Name"].nunique()
    nations = df["region"].nunique()

    st.title("Top Statistics")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Hosts")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Nations")
        st.title(nations)
    with col3:
        st.header("Athletes")
        st.title(athletes)

    nations_over_time = helper.data_over_time(df, "region")
    st.title("Participating Nations over the years")
    st.plotly_chart(px.line(nations_over_time, x="Edition", y="Count"), use_container_width=True)

    events_over_time = helper.data_over_time(df, "Event")
    st.title("Events over the years")
    st.plotly_chart(px.line(events_over_time, x="Edition", y="Count"), use_container_width=True)

    athlete_over_time = helper.data_over_time(df, "Name")
    st.title("Athletes over the years")
    st.plotly_chart(px.line(athlete_over_time, x="Edition", y="Count"), use_container_width=True)

    st.title("No. of Events over time (Every Sport)")
    fig, ax = plt.subplots(figsize=(20, 20))
    x = df.drop_duplicates(["Year", "Sport", "Event"])
    pt = x.pivot_table(index="Sport", columns="Year", values="Event", aggfunc="count").fillna(0).astype(int)
    ax = sns.heatmap(pt, annot=False)
    st.pyplot(fig)

    st.title("Most successful Athletes")
    sport_list = sorted(df["Sport"].dropna().unique().tolist())
    sport_list.insert(0, "Overall")

    selected_sport = st.selectbox("Select a Sport", sport_list)
    top_athletes = helper.most_successful(df, selected_sport)
    st.dataframe(top_athletes, use_container_width=True)


# -----------------------------
# Country-wise Analysis
# -----------------------------
if user_menu == "Country-wise Analysis":
    st.sidebar.title("Country-wise Analysis")

    country_list = sorted(df["region"].dropna().unique().tolist())
    selected_country = st.sidebar.selectbox("Select a Country", country_list)

    country_df = helper.yearwise_medal_tally(df, selected_country)
    st.title(f"{selected_country} Medal Tally over the years")
    st.plotly_chart(px.line(country_df, x="Year", y="Medal"), use_container_width=True)

    st.title(f"{selected_country} excels in the following sports")
    pt = helper.country_event_heatmap(df, selected_country)
    fig, ax = plt.subplots(figsize=(20, 20))
    ax = sns.heatmap(pt, annot=False)
    st.pyplot(fig)

    st.title(f"Top 10 athletes of {selected_country}")
    top10_df = helper.most_successful_countrywise(df, selected_country)
    st.dataframe(top10_df, use_container_width=True)


# -----------------------------
# Athlete wise Analysis
# -----------------------------
if user_menu == "Athlete wise Analysis":
    athlete_df = df.drop_duplicates(subset=["Name", "region"]).copy()

    # ---- FIX: remove plotly figure_factory distplot (no scipy needed)
    st.title("Distribution of Age (Overall vs Medalists)")
    temp = athlete_df.dropna(subset=["Age"]).copy()
    temp["MedalType"] = temp["Medal"].fillna("No Medal")
    temp = temp[temp["MedalType"].isin(["Gold", "Silver", "Bronze", "No Medal"])]

    fig = px.histogram(
        temp,
        x="Age",
        color="MedalType",
        nbins=30,
        barmode="overlay",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.title("Distribution of Age wrt Sports (Gold Medalists)")
    famous_sports = [
        "Basketball", "Judo", "Football", "Tug-Of-War", "Athletics", "Swimming",
        "Badminton", "Sailing", "Gymnastics", "Art Competitions", "Handball",
        "Weightlifting", "Wrestling", "Water Polo", "Hockey", "Rowing", "Fencing",
        "Shooting", "Boxing", "Taekwondo", "Cycling", "Diving", "Canoeing",
        "Tennis", "Golf", "Softball", "Archery", "Volleyball",
        "Synchronized Swimming", "Table Tennis", "Baseball", "Rhythmic Gymnastics",
        "Rugby Sevens", "Beach Volleyball", "Triathlon", "Rugby", "Polo", "Ice Hockey"
    ]

    gold = athlete_df[athlete_df["Medal"] == "Gold"].copy()
    gold = gold[gold["Sport"].isin(famous_sports)].dropna(subset=["Age"])

    fig = px.histogram(
        gold,
        x="Age",
        color="Sport",
        nbins=30,
        barmode="overlay",
    )
    st.plotly_chart(fig, use_container_width=True)

    sport_list = sorted(df["Sport"].dropna().unique().tolist())
    sport_list.insert(0, "Overall")

    st.title("Height Vs Weight")
    selected_sport = st.selectbox("Select a Sport", sport_list)
    temp_df = helper.weight_v_height(df, selected_sport)

    fig, ax = plt.subplots()
    sns.scatterplot(
        data=temp_df,
        x="Weight",
        y="Height",
        hue="Medal",
        style="Sex",
        s=60,
        ax=ax
    )
    st.pyplot(fig)

    st.title("Men Vs Women Participation Over the Years")
    final = helper.men_vs_women(df)
    fig = px.line(final, x="Year", y=["Male", "Female"])
    st.plotly_chart(fig, use_container_width=True)
