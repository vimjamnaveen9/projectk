import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_endpoint(client):
    """Test the main index endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'message' in data
    assert 'project' in data
    assert 'status' in data
    assert data['status'] == 'running'

def test_app_info_endpoint(client):
    """Test the application info endpoint."""
    response = client.get('/api/info')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'application' in data
    assert 'infrastructure' in data
    assert 'environment' in data
    assert data['application']['name'] == '8byte DevOps Demo'

def test_metrics_endpoint(client):
    """Test the metrics endpoint."""
    response = client.get('/api/metrics')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'metrics' in data
    assert 'database' in data

@patch('app.get_db_connection')
def test_health_check_healthy(mock_db_conn, client):
    """Test health check when database is healthy."""
    # Mock successful database connection
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db_conn.return_value = mock_conn
    
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['database'] == 'healthy'
    assert 'version' in data

@patch('app.get_db_connection')
def test_health_check_unhealthy(mock_db_conn, client):
    """Test health check when database is unhealthy."""
    # Mock failed database connection
    mock_db_conn.return_value = None
    
    response = client.get('/health')
    assert response.status_code == 200  # Still returns 200, but status is unhealthy
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['database'] == 'unhealthy'

@patch('app.get_db_connection')
def test_database_test_success(mock_db_conn, client):
    """Test database test endpoint with successful connection."""
    from datetime import datetime
    
    # Mock successful database operations
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        (1, datetime(2023, 1, 1, 12, 0, 0), 'healthy'),
        (2, datetime(2023, 1, 1, 12, 1, 0), 'healthy')
    ]
    mock_conn.cursor.return_value = mock_cursor
    mock_db_conn.return_value = mock_conn
    
    response = client.get('/api/database/test')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'recent_checks' in data

@patch('app.get_db_connection')
def test_database_test_failure(mock_db_conn, client):
    """Test database test endpoint with failed connection."""
    # Mock failed database connection
    mock_db_conn.return_value = None
    
    response = client.get('/api/database/test')
    assert response.status_code == 500
    
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'message' in data

@patch('app.boto3.session.Session')
def test_get_db_credentials_success(mock_session):
    """Test successful retrieval of database credentials."""
    from app import get_db_credentials
    
    # Mock AWS Secrets Manager response
    mock_client = MagicMock()
    mock_client.get_secret_value.return_value = {
        'SecretString': json.dumps({
            'username': 'testuser',
            'password': 'testpass',
            'endpoint': 'test.rds.amazonaws.com:5432',
            'port': 5432,
            'dbname': 'testdb'
        })
    }
    mock_session.return_value.client.return_value = mock_client
    
    with patch.dict(os.environ, {'DB_SECRET_NAME': 'test-secret', 'AWS_REGION': 'us-west-2'}):
        credentials = get_db_credentials()
    
    assert credentials is not None
    assert credentials['username'] == 'testuser'
    assert credentials['dbname'] == 'testdb'

def test_environment_variables():
    """Test that environment variables are properly handled."""
    # Test with environment variables set
    with patch.dict(os.environ, {'PROJECT_NAME': 'test-project', 'ENVIRONMENT': 'test'}):
        response = app.test_client().get('/')
        data = json.loads(response.data)
        assert data['project'] == 'test-project'
        assert data['environment'] == 'test'

if __name__ == '__main__':
    pytest.main([__file__])