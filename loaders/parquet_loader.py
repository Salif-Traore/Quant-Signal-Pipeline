import pandas as pd
from .base_loader import BaseLoader

class ParquetLoader(BaseLoader):
    """Loader for Parquet files."""
    
    def load(self, file_path: str) -> pd.DataFrame:
        """
        Load parquet file into DataFrame.
        
        Args:
            file_path (str): Path to the parquet file
            
        Returns:
            pd.DataFrame: Loaded data as a pandas DataFrame
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not a valid parquet file
        """
        if not self.validate_file(file_path):
            raise FileNotFoundError(f"Parquet file not found or not accessible: {file_path}")
            
        try:
            return pd.read_parquet(file_path)
        except Exception as e:
            raise ValueError(f"Error loading parquet file: {str(e)}")
