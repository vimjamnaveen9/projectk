import os
import json
import boto3
import psycopg2
from flask import Flask, jsonify, request
from botocore.exceptions import ClientError
import logging
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_credentials():
    """Get database credentials from AWS Secrets Manager"""
    secret_name = os.environ.get('DB_SECRET_NAME', '8byte-app-dev-db-password')
    region_name = os.environ.get('AWS_REGION', 'us-west-2')
    
    try:
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        secret = json.loads(get_secret_value_response['SecretString'])
        return secret
    except ClientError as e:
        logger.error(f"Error retrieving secret: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None

def get_db_connection():
    """Get database connection"""
    try:
        credentials = get_db_credentials()
        if not credentials:
            return None
            
        conn = psycopg2.connect(
            host=credentials['endpoint'].split(':')[0],
            port=credentials['port'],
            database=credentials['dbname'],
            user=credentials['username'],
            password=credentials['password'],
            connect_timeout=10
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

@app.route('/health')
def health_check():
    """Health check endpoint for ALB"""
    try:
        # Test database connection
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            cursor.close()
            conn.close()
            db_status = "healthy"
        else:
            db_status = "unhealthy"
            
        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/')
def index():
    """Main endpoint"""
    return jsonify({
        'message': 'Welcome to 8byte Application - Cloud Native DevOps Demo',
        'project': os.environ.get('PROJECT_NAME', '8byte-app'),
        'environment': os.environ.get('ENVIRONMENT', 'dev'),
        'status': 'running',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'features': [
            'AWS Infrastructure with Terraform',
            'CI/CD with GitHub Actions',
            'CloudWatch Monitoring',
            'Auto Scaling',
            'Load Balancing',
            'Secrets Management',
            'High Availability'
        ]
    })

@app.route('/api/info')
def app_info():
    """Application information endpoint"""
    return jsonify({
        'application': {
            'name': '8byte DevOps Demo',
            'version': '1.0.0',
            'description': 'Full-stack DevOps infrastructure demonstration'
        },
        'infrastructure': {
            'platform': 'AWS',
            'orchestration': 'Terraform',
            'deployment': 'GitHub Actions',
            'monitoring': 'CloudWatch',
            'database': 'PostgreSQL RDS',
            'compute': 'EC2 Auto Scaling'
        },
        'environment': {
            'name': os.environ.get('ENVIRONMENT', 'dev'),
            'region': os.environ.get('AWS_REGION', 'us-west-2')
        }
    })

@app.route('/api/metrics')
def metrics():
    """Application metrics endpoint"""
    return jsonify({
        'metrics': {
            'requests_total': 1,
            'uptime': '1h',
            'version': '1.0.0',
            'last_updated': datetime.utcnow().isoformat()
        },
        'database': {
            'status': 'connected' if get_db_connection() else 'disconnected'
        }
    })

@app.route('/api/database/test')
def test_database():
    """Test database connectivity"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'status': 'error',
                'message': 'Could not connect to database'
            }), 500
            
        cursor = conn.cursor()
        
        # Create a test table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_check (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50)
            )
        ''')
        
        # Insert a test record
        cursor.execute(
            "INSERT INTO health_check (status) VALUES (%s)",
            ('healthy',)
        )
        
        # Query recent records
        cursor.execute(
            "SELECT id, timestamp, status FROM health_check ORDER BY timestamp DESC LIMIT 5"
        )
        records = cursor.fetchall()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Database connection successful',
            'recent_checks': [
                {
                    'id': record[0],
                    'timestamp': record[1].isoformat(),
                    'status': record[2]
                } for record in records
            ]
        })
        
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Database test failed: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting 8byte application on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)