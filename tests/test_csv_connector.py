# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""
Tests for CSV Data Connector.
"""

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

try:
    from runtime.calibration.csv_connector import CSVConnector
except ImportError:
    pytest.skip("calibration module not installed", allow_module_level=True)


class TestCSVConnector:
    """Test CSV data connector functionality."""

    @pytest.fixture
    def sample_csv(self, tmp_path):
        """Create a sample CSV file for testing."""
        data = {
            'month': ['2025-01', '2025-02', '2025-03', '2025-04'],
            'revenue': [1000, 1200, 1100, 1300],
            'churn_rate': [0.05, 0.06, 0.055, 0.065],
            'customer_count': [100, 105, 103, 108],
        }
        df = pd.DataFrame(data)
        csv_path = tmp_path / "test.csv"
        df.to_csv(csv_path, index=False)
        return csv_path

    @pytest.fixture
    def sample_config(self, tmp_path):
        """Create a sample configuration file."""
        config = {
            'encoding': 'utf-8',
            'delimiter': ',',
            'column_mapping': {
                'revenue': 'revenue',
                'churn': 'churn_rate',
            },
            'type_mapping': {
                'revenue': 'float',
                'churn': 'float',
            },
            'missing_values': {
                'strategy': 'drop',
            },
        }
        config_path = tmp_path / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        return config_path

    def test_load_csv(self, sample_csv):
        """Test basic CSV loading."""
        connector = CSVConnector()
        df = connector.load_data(sample_csv)
        
        assert len(df) == 4
        assert 'revenue' in df.columns
        assert 'churn_rate' in df.columns
        assert df['revenue'].iloc[0] == 1000

    def test_load_config(self, sample_config):
        """Test configuration loading from YAML."""
        connector = CSVConnector(sample_config)
        
        assert connector.config['encoding'] == 'utf-8'
        assert 'column_mapping' in connector.config

    def test_map_columns(self, sample_csv):
        """Test column mapping."""
        connector = CSVConnector()
        df = connector.load_data(sample_csv)
        
        mapping = {'rev': 'revenue', 'churn': 'churn_rate'}
        mapped_df = connector.map_columns(df, mapping)
        
        assert 'rev' in mapped_df.columns
        assert 'churn' in mapped_df.columns
        assert 'revenue' not in mapped_df.columns

    def test_map_columns_missing(self, sample_csv):
        """Test column mapping with missing columns."""
        connector = CSVConnector()
        df = connector.load_data(sample_csv)
        
        mapping = {'rev': 'nonexistent_column'}
        with pytest.raises(ValueError, match="Missing columns"):
            connector.map_columns(df, mapping)

    def test_convert_types(self, sample_csv):
        """Test type conversion."""
        connector = CSVConnector()
        df = connector.load_data(sample_csv)
        
        type_map = {'revenue': 'float', 'customer_count': 'int'}
        converted = connector.convert_types(df, type_map)
        
        assert converted['revenue'].dtype == np.float64
        assert converted['customer_count'].dtype == 'Int64'

    def test_handle_missing_values_drop(self, tmp_path):
        """Test missing value handling with drop strategy."""
        # Create CSV with missing values
        data = {
            'col1': [1, 2, np.nan, 4],
            'col2': [10, np.nan, 30, 40],
        }
        df = pd.DataFrame(data)
        csv_path = tmp_path / "missing.csv"
        df.to_csv(csv_path, index=False)
        
        connector = CSVConnector()
        loaded = connector.load_data(csv_path)
        cleaned = connector.handle_missing_values(loaded, strategy='drop')
        
        assert len(cleaned) == 2  # Only 2 complete rows

    def test_handle_missing_values_mean(self, tmp_path):
        """Test missing value handling with mean strategy."""
        data = {
            'col1': [1.0, 2.0, np.nan, 4.0],  # mean = 7/3 ≈ 2.33
        }
        df = pd.DataFrame(data)
        csv_path = tmp_path / "missing.csv"
        df.to_csv(csv_path, index=False)
        
        connector = CSVConnector()
        loaded = connector.load_data(csv_path)
        cleaned = connector.handle_missing_values(loaded, strategy='mean')
        
        assert not cleaned['col1'].isna().any()
        assert np.isclose(cleaned['col1'].iloc[2], 7/3)

    def test_detect_outliers_iqr(self, tmp_path):
        """Test outlier detection with IQR method."""
        # Create data with outliers
        data = {
            'values': [1, 2, 3, 4, 5, 100],  # 100 is an outlier
        }
        df = pd.DataFrame(data)
        
        connector = CSVConnector()
        outliers = connector.detect_outliers(df, 'values', method='iqr', threshold=1.5)
        
        assert outliers.iloc[-1] == True  # 100 should be detected
        assert outliers.iloc[0] == False  # 1 should not be detected

    def test_detect_outliers_zscore(self, tmp_path):
        """Test outlier detection with z-score method."""
        # Create data with outliers
        data = {
            'values': [10, 12, 11, 13, 12, 50],  # 50 is an outlier
        }
        df = pd.DataFrame(data)
        
        connector = CSVConnector()
        outliers = connector.detect_outliers(df, 'values', method='zscore', threshold=2.0)
        
        assert outliers.iloc[-1] == True  # 50 should be detected

    def test_filter_outliers(self, tmp_path):
        """Test outlier filtering."""
        data = {
            'values': [1, 2, 3, 4, 5, 100],
        }
        df = pd.DataFrame(data)
        
        connector = CSVConnector()
        filtered = connector.filter_outliers(df, 'values', method='iqr', threshold=1.5)
        
        assert len(filtered) == 5  # 100 removed
        assert filtered['values'].max() <= 5

    def test_extract_column(self, sample_csv):
        """Test column extraction as numpy array."""
        connector = CSVConnector()
        df = connector.load_data(sample_csv)
        
        revenue = connector.extract_column(df, 'revenue')
        
        assert isinstance(revenue, np.ndarray)
        assert len(revenue) == 4
        assert revenue[0] == 1000

    def test_extract_column_missing(self, sample_csv):
        """Test column extraction with missing column."""
        connector = CSVConnector()
        df = connector.load_data(sample_csv)
        
        with pytest.raises(ValueError, match="not found"):
            connector.extract_column(df, 'nonexistent')

    def test_load_and_prepare(self, sample_csv, tmp_path):
        """Test full pipeline."""
        config = {
            'encoding': 'utf-8',
            'delimiter': ',',
            'column_mapping': {
                'rev': 'revenue',
            },
            'type_mapping': {
                'rev': 'float',
            },
            'missing_values': {
                'strategy': 'drop',
            },
        }
        
        connector = CSVConnector()
        df = connector.load_and_prepare(sample_csv, config=config)
        
        assert 'rev' in df.columns
        assert df['rev'].dtype == np.float64

    def test_csv_with_different_delimiter(self, tmp_path):
        """Test CSV with semicolon delimiter."""
        data = "col1;col2\n1;2\n3;4\n"
        csv_path = tmp_path / "semicolon.csv"
        csv_path.write_text(data)
        
        connector = CSVConnector()
        df = connector.load_data(csv_path, delimiter=';')
        
        assert len(df) == 2
        assert 'col1' in df.columns
        assert 'col2' in df.columns

    def test_csv_with_encoding(self, tmp_path):
        """Test CSV with different encoding."""
        data = "name,value\nTest,123\n"
        csv_path = tmp_path / "encoded.csv"
        csv_path.write_bytes(data.encode('utf-8'))
        
        connector = CSVConnector()
        df = connector.load_data(csv_path, encoding='utf-8')
        
        assert len(df) == 1
        assert df['name'].iloc[0] == 'Test'

    def test_invalid_csv_path(self):
        """Test loading from invalid path."""
        connector = CSVConnector()
        
        with pytest.raises(ValueError, match="Failed to load"):
            connector.load_data(Path('/nonexistent/file.csv'))

    def test_missing_value_forward_fill(self, tmp_path):
        """Test forward fill missing value strategy."""
        data = {
            'col1': [1.0, np.nan, np.nan, 4.0],
        }
        df = pd.DataFrame(data)
        csv_path = tmp_path / "missing.csv"
        df.to_csv(csv_path, index=False)
        
        connector = CSVConnector()
        loaded = connector.load_data(csv_path)
        cleaned = connector.handle_missing_values(loaded, strategy='forward_fill')
        
        assert not cleaned['col1'].isna().any()
        assert cleaned['col1'].iloc[1] == 1.0  # Filled from previous
        assert cleaned['col1'].iloc[2] == 1.0

    def test_missing_value_fill_constant(self, tmp_path):
        """Test fill with constant value."""
        data = {
            'col1': [1.0, np.nan, 3.0],
        }
        df = pd.DataFrame(data)
        csv_path = tmp_path / "missing.csv"
        df.to_csv(csv_path, index=False)
        
        connector = CSVConnector()
        loaded = connector.load_data(csv_path)
        cleaned = connector.handle_missing_values(loaded, strategy='fill', fill_value=99.0)
        
        assert cleaned['col1'].iloc[1] == 99.0
