# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""
CSV Data Connector for PEL Calibration.

Loads CSV data, validates types, handles missing values and outliers.
"""

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import yaml


class CSVConnector:
    """
    CSV data connector for PEL calibration.
    
    Features:
    - Load CSV files with configurable encoding
    - Map CSV columns to PEL parameters
    - Type conversion and validation
    - Missing value handling
    - Outlier detection and filtering
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize CSV connector.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config: Dict[str, Any] = {}
        if config_path:
            self.load_config(config_path)

    def load_config(self, config_path: Path) -> None:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def load_data(
        self,
        csv_path: Path,
        encoding: str = 'utf-8',
        delimiter: str = ',',
    ) -> pd.DataFrame:
        """
        Load CSV file into DataFrame.
        
        Args:
            csv_path: Path to CSV file
            encoding: Character encoding (default: utf-8)
            delimiter: Column delimiter (default: comma)
            
        Returns:
            DataFrame with loaded data
        """
        try:
            df = pd.read_csv(
                csv_path,
                encoding=encoding,
                delimiter=delimiter,
                skipinitialspace=True,
            )
            return df
        except Exception as e:
            raise ValueError(f"Failed to load CSV from {csv_path}: {e}")

    def map_columns(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, str],
    ) -> pd.DataFrame:
        """
        Map CSV columns to PEL parameter names.
        
        Args:
            df: Input DataFrame
            mapping: Dict mapping PEL param names to CSV column names
            
        Returns:
            DataFrame with renamed columns
        """
        # Validate that all mapped columns exist
        missing = [col for col in mapping.values() if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns in CSV: {missing}")
        
        # Create reverse mapping (CSV col -> PEL param)
        rename_map = {csv_col: pel_param for pel_param, csv_col in mapping.items()}
        
        # Select and rename columns
        return df[list(mapping.values())].rename(columns=rename_map)

    def convert_types(
        self,
        df: pd.DataFrame,
        type_map: Dict[str, str],
    ) -> pd.DataFrame:
        """
        Convert column types.
        
        Args:
            df: Input DataFrame
            type_map: Dict mapping column names to types (float, int, str, date)
            
        Returns:
            DataFrame with converted types
        """
        df = df.copy()
        
        for col, dtype in type_map.items():
            if col not in df.columns:
                continue
                
            try:
                if dtype == 'float':
                    df[col] = pd.to_numeric(df[col], errors='coerce').astype('float64')
                elif dtype == 'int':
                    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
                elif dtype == 'date':
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                elif dtype == 'str':
                    df[col] = df[col].astype(str)
            except Exception as e:
                raise ValueError(f"Failed to convert column '{col}' to {dtype}: {e}")
        
        return df

    def handle_missing_values(
        self,
        df: pd.DataFrame,
        strategy: str = 'drop',
        fill_value: Optional[float] = None,
    ) -> pd.DataFrame:
        """
        Handle missing values.
        
        Args:
            df: Input DataFrame
            strategy: 'drop', 'mean', 'median', 'forward_fill', or 'fill'
            fill_value: Value to use if strategy='fill'
            
        Returns:
            DataFrame with missing values handled
        """
        df = df.copy()
        
        if strategy == 'drop':
            df = df.dropna()
        elif strategy == 'mean':
            df = df.fillna(df.mean(numeric_only=True))
        elif strategy == 'median':
            df = df.fillna(df.median(numeric_only=True))
        elif strategy == 'forward_fill':
            df = df.ffill()
        elif strategy == 'fill' and fill_value is not None:
            df = df.fillna(fill_value)
        else:
            raise ValueError(f"Unknown missing value strategy: {strategy}")
        
        return df

    def detect_outliers(
        self,
        df: pd.DataFrame,
        column: str,
        method: str = 'iqr',
        threshold: float = 3.0,
    ) -> pd.Series:
        """
        Detect outliers in a column.
        
        Args:
            df: Input DataFrame
            column: Column name to check
            method: 'iqr' or 'zscore'
            threshold: Threshold for outlier detection
            
        Returns:
            Boolean Series indicating outliers
        """
        data = df[column].dropna()
        
        if method == 'iqr':
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - threshold * IQR
            upper = Q3 + threshold * IQR
            return (df[column] < lower) | (df[column] > upper)
        
        elif method == 'zscore':
            mean = data.mean()
            std = data.std()
            z_scores = np.abs((df[column] - mean) / std)
            return z_scores > threshold
        
        else:
            raise ValueError(f"Unknown outlier detection method: {method}")

    def filter_outliers(
        self,
        df: pd.DataFrame,
        column: str,
        method: str = 'iqr',
        threshold: float = 3.0,
    ) -> pd.DataFrame:
        """
        Remove outliers from DataFrame.
        
        Args:
            df: Input DataFrame
            column: Column name to filter
            method: 'iqr' or 'zscore'
            threshold: Threshold for outlier detection
            
        Returns:
            DataFrame with outliers removed
        """
        outliers = self.detect_outliers(df, column, method, threshold)
        return df[~outliers].copy()

    def load_and_prepare(
        self,
        csv_path: Path,
        config: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        """
        Full pipeline: load, map, convert, clean.
        
        Args:
            csv_path: Path to CSV file
            config: Configuration dict (overrides loaded config)
            
        Returns:
            Cleaned and prepared DataFrame
        """
        cfg = config or self.config
        
        # Load data
        df = self.load_data(
            csv_path,
            encoding=cfg.get('encoding', 'utf-8'),
            delimiter=cfg.get('delimiter', ','),
        )
        
        # Map columns
        if 'column_mapping' in cfg:
            df = self.map_columns(df, cfg['column_mapping'])
        
        # Convert types
        if 'type_mapping' in cfg:
            df = self.convert_types(df, cfg['type_mapping'])
        
        # Handle missing values
        if 'missing_values' in cfg:
            mv_cfg = cfg['missing_values']
            df = self.handle_missing_values(
                df,
                strategy=mv_cfg.get('strategy', 'drop'),
                fill_value=mv_cfg.get('fill_value'),
            )
        
        # Filter outliers
        if 'outlier_filtering' in cfg:
            for col_cfg in cfg['outlier_filtering']:
                df = self.filter_outliers(
                    df,
                    column=col_cfg['column'],
                    method=col_cfg.get('method', 'iqr'),
                    threshold=col_cfg.get('threshold', 3.0),
                )
        
        return df

    def extract_column(self, df: pd.DataFrame, column: str) -> np.ndarray:
        """
        Extract a single column as numpy array.
        
        Args:
            df: Input DataFrame
            column: Column name
            
        Returns:
            Numpy array of values
        """
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame")
        
        return df[column].dropna().values
