import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
from typing import List, Optional, Dict, Any
from .base_loader import BaseLoader

class YFinanceLoader(BaseLoader):
    """Loader class for downloading and managing data from Yahoo Finance."""
    
    def __init__(self, data_dir: str = "data/raw", **kwargs):
        super().__init__(**kwargs)
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.config.update({
            'data_dir': data_dir,
            'default_interval': '1d',
            'default_lookback_days': 3*365
        })
    
    def clean_ticker(self, ticker: str) -> str:
        """Clean ticker symbol for use in filenames."""
        return ticker.replace("=", "").replace("^", "").replace("/", "-").replace(":", "-")
    
    def get_file_path(self, ticker: str) -> str:
        """Get the file path for a ticker's data."""
        safe_ticker = self.clean_ticker(ticker)
        return os.path.join(self.data_dir, f"{safe_ticker}.parquet")
    
    def load(self, file_path: str) -> pd.DataFrame:
        """Load data from a parquet file.
        
        Args:
            file_path (str): Path to the parquet file
            
        Returns:
            pd.DataFrame: Loaded data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is invalid
        """
        if not self.validate_file(file_path):
            raise FileNotFoundError(f"File not found or not accessible: {file_path}")
        
        try:
            return pd.read_parquet(file_path)
        except Exception as e:
            raise ValueError(f"Failed to load parquet file {file_path}: {str(e)}")
    
    def download_and_save(self, 
                         ticker: str, 
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         interval: Optional[str] = None) -> bool:
        """Download and save data for a single ticker."""
        try:
            if start_date is None:
                start_date = datetime.today() - timedelta(days=self.config['default_lookback_days'])
            if end_date is None:
                end_date = datetime.today()
            if interval is None:
                interval = self.config['default_interval']
                
            df = yf.download(ticker, start=start_date, end=end_date, interval=interval)
            if df.empty:
                print(f"⚠️ No data for {ticker}")
                return False
                
            df["Original_Ticker"] = ticker
            save_path = self.get_file_path(ticker)
            df.to_parquet(save_path)
            print(f"✅ Saved {ticker} as {save_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download {ticker}: {e}")
            return False
    
    def load_data(self, ticker: str) -> Optional[pd.DataFrame]:
        """Load data for a ticker from the saved parquet file."""
        try:
            file_path = self.get_file_path(ticker)
            return self.load(file_path)
        except Exception as e:
            print(f"❌ Failed to load data for {ticker}: {e}")
            return None
    
    def download_multiple(self, 
                         tickers: List[str],
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         interval: Optional[str] = None) -> None:
        """Download and save data for multiple tickers."""
        for ticker in tickers:
            self.download_and_save(ticker, start_date, end_date, interval) 