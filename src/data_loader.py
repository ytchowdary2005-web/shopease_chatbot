import pandas as pd


def load_faqs():
    df = pd.read_csv("data/shopease_faqs.csv")
    return df