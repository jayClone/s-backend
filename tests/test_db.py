import pytest
from api.db import db, client, session
import os

def test_mongodb_connection():
    if os.getenv('DB_TYPE') in ['mongodb', 'both']:
        assert client is not None
        assert db is not None
        # Test connection by performing a simple operation
        result = db.command('ping')
        assert result['ok'] == 1

def test_mysql_connection():
    if os.getenv('DB_TYPE') in ['mysql', 'both']:
        assert session is not None
        # Test connection by performing a simple query
        try:
            session.execute('SELECT 1')
            assert True
        except:
            pytest.fail("MySQL connection failed") 