import pytest
from entrypoint import create_app
from extensions import db
from models.user import User

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })

    with app.app_context():
        db.drop_all()
        db.create_all()
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_register_missing_data(client):
    response = client.post('/api/register', json={})
    assert response.status_code == 400
    assert 'required' in response.get_json()['message']

def test_register_short_credentials(client):
    response = client.post('/api/register', json={
        'username': 'ab',
        'password': '123'
    })
    assert response.status_code == 400
    assert 'min' in response.get_json()['message']

def test_register_success(client):
    response = client.post('/api/register', json={
        'username': 'testuser',
        'password': 'testpass123'
    })
    assert response.status_code == 201
    assert response.get_json()['message'] == 'User registered'

def test_register_duplicate_user(client):
    client.post('/api/register', json={
        'username': 'duplicate',
        'password': 'password123'
    })
    response = client.post('/api/register', json={
        'username': 'duplicate',
        'password': 'password456'
    })
    assert response.status_code == 400
    assert 'already exists' in response.get_json()['message']

def test_login_missing_data(client):
    response = client.post('/api/login', json={})
    assert response.status_code == 400
    assert 'required' in response.get_json()['message']

def test_login_invalid_credentials(client):
    client.post('/api/register', json={
        'username': 'user',
        'password': 'password123'
    })
    response = client.post('/api/login', json={
        'username': 'user',
        'password': 'wrongpass'
    })
    assert response.status_code == 401
    assert 'Invalid credentials' in response.get_json()['message']

def test_login_success(client):
    client.post('/api/register', json={
        'username': 'loginuser',
        'password': 'password123'
    })
    response = client.post('/api/login', json={
        'username': 'loginuser',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'token' in response.get_json()

def test_password_hashing(client):
    with client.application.app_context():
        user = User(username='hashtest')
        user.set_password('mypassword')
        db.session.add(user)
        db.session.commit()
        
        # Password should be hashed, not plain text
        assert user.password != 'mypassword'
        assert user.check_password('mypassword') is True
        assert user.check_password('wrongpassword') is False