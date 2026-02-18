import numpy as np
import pandas as pd


def _ensure_medal_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Guarantee Gold/Silver/Bronze columns exist to avoid KeyErrors."""
    for col in ["Gold", "Silver", "Bronze"]:
        if col not in df.columns:
            df[col] = 0
    return df


def fetch_medal_tally(df, year, country):
    df = _ensure_medal_columns(df.copy())

    medal_df = df.drop_duplicates(
        subset=["Team", "NOC", "Games", "Year", "City", "Sport", "Event", "Medal"]
    )

    if year == "Overall" and country == "Overall":
        temp_df = medal_df
        x = (
            temp_df.groupby("region")[["Gold", "Silver", "Bronze"]]
            .sum()
            .sort_values("Gold", ascending=False)
            .reset_index()
        )

    elif year == "Overall" and country != "Overall":
        temp_df = medal_df[medal_df["region"] == country]
        x = (
            temp_df.groupby("Year")[["Gold", "Silver", "Bronze"]]
            .sum()
            .sort_values("Year")
            .reset_index()
        )

    elif year != "Overall" and country == "Overall":
        y = int(year)
        temp_df = medal_df[medal_df["Year"] == y]
        x = (
            temp_df.groupby("region")[["Gold", "Silver", "Bronze"]]
            .sum()
            .sort_values("Gold", ascending=False)
            .reset_index()
        )

    else:
        y = int(year)
        temp_df = medal_df[(medal_df["Year"] == y) & (medal_df["region"] == country)]
        x = (
            temp_df.groupby("region")[["Gold", "Silver", "Bronze"]]
            .sum()
            .sort_values("Gold", ascending=False)
            .reset_index()
        )

    x["total"] = x["Gold"] + x["Silver"] + x["Bronze"]
    for c in ["Gold", "Silver", "Bronze", "total"]:
        x[c] = x[c].astype(int)

    return x


def country_year_list(df):
    years = sorted(df["Year"].dropna().unique().tolist())
    years.insert(0, "Overall")

    countries = np.unique(df["region"].dropna().values).tolist()
    countries.sort()
    countries.insert(0, "Overall")

    return years, countries


def data_over_time(df, col):
    # Count unique (Year, col) pairs per Year
    tmp = df.drop_duplicates(["Year", col])
    out = tmp.groupby("Year").size().reset_index(name="Count").sort_values("Year")
    out.rename(columns={"Year": "Edition"}, inplace=True)
    return out


def most_successful(df, sport):
    temp_df = df.dropna(subset=["Medal"]).copy()
    if sport != "Overall":
        temp_df = temp_df[temp_df["Sport"] == sport]

    top = temp_df["Name"].value_counts().head(15).reset_index()
    top.columns = ["Name", "Medals"]

    # add one representative Sport + region for each athlete
    meta = (
        df[["Name", "Sport", "region"]]
        .dropna(subset=["Name"])
        .drop_duplicates(subset=["Name"])
    )

    out = top.merge(meta, on="Name", how="left")
    return out


def yearwise_medal_tally(df, country):
    temp_df = df.dropna(subset=["Medal"]).copy()
    temp_df = temp_df.drop_duplicates(
        subset=["Team", "NOC", "Games", "Year", "City", "Sport", "Event", "Medal"]
    )

    new_df = temp_df[temp_df["region"] == country]
    final_df = new_df.groupby("Year")["Medal"].count().reset_index()
    return final_df


def country_event_heatmap(df, country):
    temp_df = df.dropna(subset=["Medal"]).copy()
    temp_df = temp_df.drop_duplicates(
        subset=["Team", "NOC", "Games", "Year", "City", "Sport", "Event", "Medal"]
    )

    new_df = temp_df[temp_df["region"] == country]
    pt = new_df.pivot_table(
        index="Sport", columns="Year", values="Medal", aggfunc="count"
    ).fillna(0)
    return pt


def most_successful_countrywise(df, country):
    # FIX: no 'index' merge; return predictable columns
    temp_df = df.dropna(subset=["Medal"]).copy()
    temp_df = temp_df[temp_df["region"] == country]

    top = temp_df["Name"].value_counts().head(10).reset_index()
    top.columns = ["Name", "Medals"]

    # attach a representative sport for display
    meta = (
        temp_df[["Name", "Sport"]]
        .dropna(subset=["Name"])
        .drop_duplicates(subset=["Name"])
    )

    out = top.merge(meta, on="Name", how="left")
    return out


def weight_v_height(df, sport):
    athlete_df = df.drop_duplicates(subset=["Name", "region"]).copy()
    athlete_df["Medal"] = athlete_df["Medal"].fillna("No Medal")

    if sport != "Overall":
        return athlete_df[athlete_df["Sport"] == sport]
    return athlete_df


def men_vs_women(df):
    athlete_df = df.drop_duplicates(subset=["Name", "region"]).copy()

    men = athlete_df[athlete_df["Sex"] == "M"].groupby("Year")["Name"].count().reset_index()
    women = athlete_df[athlete_df["Sex"] == "F"].groupby("Year")["Name"].count().reset_index()

    final = men.merge(women, on="Year", how="left")
    final.rename(columns={"Name_x": "Male", "Name_y": "Female"}, inplace=True)
    final["Female"] = final["Female"].fillna(0).astype(int)
    final["Male"] = final["Male"].fillna(0).astype(int)

    return final
