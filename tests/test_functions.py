import pytest
import os
import sqlite3
from unittest import mock
from project0 import extract_fields, create_db, drop_db, populate_db, status
from unittest.mock import patch, MagicMock
import shutil
import pandas as pd
import numpy as np
from app import generate_visualizations
from scipy.sparse import csr_matrix

# Test for extract_fields
def test_extract_fields():
    incidents = [
        "8/14/2024 15:00 2024-00058903 4023 24TH AVE NE Animal Vicious OK0140200",
        "8/14/2024 15:01 2024-00012210 500 E ROBINSON ST Sick Person 14005"
    ]
    expected_output = [
        ("15:00", "2024-00058903", "4023 24TH AVE NE", "Animal Vicious", "OK0140200"),
        ("15:01", "2024-00012210", "500 E ROBINSON ST", "Sick Person", "14005")
    ]
    assert extract_fields(incidents) == expected_output

# Test for create_db
def test_create_db():
    db_path = create_db()

    # Check if the database file is created
    assert os.path.exists(db_path)

    # Check if the 'incidents' table is created
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='incidents';")
    table = cursor.fetchone()
    conn.close()

    assert table is not None

# Test for populate_db
def test_populate_db():
    db_path = create_db()

    data = [
        [("15:00", "2024-00058903", "4023 24TH AVE NE", "Animal Vicious", "OK0140200")],
        [("15:01", "2024-00012210", "500 E ROBINSON ST", "Sick Person", "14005")]
    ]

    # Populate the database with data
    populate_db(db_path, data)

    # Check if the data is inserted correctly
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incidents")
    rows = cursor.fetchall()
    conn.close()

    assert len(rows) == 2
    assert rows[0] == ("15:00", "2024-00058903", "4023 24TH AVE NE", "Animal Vicious", "OK0140200")
    assert rows[1] == ("15:01", "2024-00012210", "500 E ROBINSON ST", "Sick Person", "14005")

# Test for status
def test_status():
    db_path = create_db()

    data = [
        [("15:00", "2024-00058903", "4023 24TH AVE NE", "Animal Vicious", "OK0140200")],
        [("15:01", "2024-00012210", "500 E ROBINSON ST", "Sick Person", "14005")]
    ]

    # Populate the database with data
    populate_db(db_path, data)

    # Capture the output of the status function
    collected_data = status(db_path)

    assert len(collected_data) > 0
    assert collected_data[0][0] == 'Animal Vicious' and collected_data[0][1] == 1
    assert collected_data[1][0] == 'Sick Person' and collected_data[1][1] == 1


@pytest.fixture
def mock_app_config():
    """Fixture to mock app config."""
    return {'STATIC_FOLDER': 'test_static'}

@pytest.fixture
def sample_data():
    """Fixture to provide sample data for testing."""
    X = csr_matrix(np.random.rand(10, 5))  # Random feature matrix
    df = pd.DataFrame({
        'Incident': [f'Incident_{i}' for i in range(10)],
        'Count': np.random.randint(1, 20, size=10)
    })
    collected_data = [[f'Incident_{i}', np.random.randint(1, 20)] for i in range(10)]
    return X, df, collected_data

@patch('app.render_template')
def test_generate_visualizations(mock_render_template, sample_data):
    """Test the generate_visualizations function."""

    # Test the function
    X, df, collected_data = sample_data
    result = generate_visualizations(X, df, collected_data)

    # Assertions
    mock_render_template.assert_called_once_with(
        'visualizations.html',
        bar_path='images/bar.png',
        wordcloud_path='images/wordcloud.png',
        dendrogram_path='images/dendrogram.png'
    )
