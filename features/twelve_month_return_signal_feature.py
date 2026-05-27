import pandas as pd

class TwelveMonthReturnSignalFeature:
    name = "signal_12m_return"

    def apply(self, df: pd.DataFrame) -> pd.Series:
        excess_return = df["excess_12m_return"]

        def signal_func(x):
            if x > 0:
                return 1
            elif x < 0:
                return -1
            else:
                return 0

        return excess_return.apply(signal_func)
