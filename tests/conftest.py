import pytest
from fastapi.testclient import TestClient
from server import app
from api.extensions.mail import MAIL
from unittest.mock import patch

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_mail():
    with patch.object(MAIL, 'sendHtmlMail') as mock:
        yield mock 