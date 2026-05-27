from abc import ABC, abstractmethod
import pandas as pd

class BaseFeature(ABC):
    @abstractmethod
    def apply(self, df: pd.DataFrame) -> pd.Series:
        pass

class TwelveMonthReturnFeature(BaseFeature):
    name = "excess_12m_return"

    def apply(self, df: pd.DataFrame) -> pd.Series:
        if len(df) < 252:
            return pd.Series([float("nan")] * len(df), index=df.index)

        twelve_month_return = df["Close"].pct_change(periods=252)
        mean_return = twelve_month_return.mean(skipna=True)
        excess_return = twelve_month_return - mean_return
        return excess_return
