class PercentChangeFeature:
    def __init__(self):
        self.name = "pct_change"

    def compute(self, df):
        return df["Close"].pct_change()
