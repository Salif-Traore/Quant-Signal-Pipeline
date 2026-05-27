from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import pandas as pd

class BaseLoader(ABC):
    """Base class for all data loaders."""
    
    def __init__(self, **kwargs):
        """Initialize the loader with optional configuration parameters."""
        self.config = kwargs
    
    @abstractmethod
    def load(self, file_path: str) -> pd.DataFrame:
        """
        Load data from a file into a pandas DataFrame.
        
        Args:
            file_path (str): Path to the data file
            
        Returns:
            pd.DataFrame: Loaded data as a pandas DataFrame
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is invalid
        """
        pass
    
    def validate_file(self, file_path: str) -> bool:
        """
        Validate if the file exists and is accessible.
        
        Args:
            file_path (str): Path to the file to validate
            
        Returns:
            bool: True if file is valid, False otherwise
        """
        import os
        return os.path.isfile(file_path) and os.access(file_path, os.R_OK)
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration of the loader.
        
        Returns:
            Dict[str, Any]: Dictionary containing the loader's configuration
        """
        return self.config
