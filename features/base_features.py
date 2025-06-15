import pandas as pd

class PercentChangeFeature:
    def __init__(self, price_col='close'):
        self.price_col = price_col
    
    def calculate(self, df: pd.DataFrame) -> pd.Series:
        return df[self.price_col].pct_change()

