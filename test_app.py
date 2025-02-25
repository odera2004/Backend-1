import pytest
from unittest.mock import patch
from app import app, db
from flask_mail import Message


@pytest.fixture
def client():
    """Fixture to set up a test client."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # In-memory database for testing
    app.config["MAIL_SUPPRESS_SEND"] = True  # Prevent actual emails from being sent

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


def test_home(client):
    """Test if the home route is working and mock email sending."""
    with patch("flask_mail.Mail.send") as mock_send:  # Mock email sending
        response = client.get("/")
        
        assert response.status_code == 200
        assert "Message sent successfully!" in response.get_data(as_text=True) or "An error occurred" in response.get_data(as_text=True)
        
        mock_send.assert_called_once()  # Ensure the email send function was called
