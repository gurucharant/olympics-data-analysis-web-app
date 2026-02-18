import pandas as pd


def preprocess(df, region_df):
    # Keep Summer Olympics only
    df = df[df["Season"] == "Summer"].copy()

    # Merge region mapping
    df = df.merge(region_df, on="NOC", how="left")

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    # One-hot medals into columns
    medal_dummies = pd.get_dummies(df["Medal"], dtype=int)
    df = pd.concat([df, medal_dummies], axis=1)

    # Ensure medal columns always exist
    for col in ["Gold", "Silver", "Bronze"]:
        if col not in df.columns:
            df[col] = 0

    return df
