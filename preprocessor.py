import pandas as pd


def preprocess(df, region_df):
    # Filter Summer Olympics only
    df = df[df["Season"] == "Summer"].copy()

    # Merge with regions
    df = df.merge(region_df, on="NOC", how="left")

    # Drop duplicates
    df.drop_duplicates(inplace=True)

    # One-hot encode medals; ensure numeric ints
    medal_dummies = pd.get_dummies(df["Medal"], dtype=int)

    df = pd.concat([df, medal_dummies], axis=1)

    # Ensure columns exist even if dataset slice misses some medal types
    for col in ["Gold", "Silver", "Bronze"]:
        if col not in df.columns:
            df[col] = 0

    return df
