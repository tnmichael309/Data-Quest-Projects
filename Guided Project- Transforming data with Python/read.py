import pandas as pd


def load_data():
    df = pd.read_csv("hn_stories.csv")
    df.columns = ["submission_time", "upvotes", "url", "headline",]
    return df

if __name__ == "__main__":
    # This will call load_data if you run the script from the command line.
    df = load_data()
    print(df.head(5))