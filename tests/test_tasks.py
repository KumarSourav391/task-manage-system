
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
        db.drop_all()   # Clean slate
        db.create_all()
        user = User(username="testuser", password="testpass", role="user")
        db.session.add(user)
        db.session.commit()
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def get_token(client):
    response = client.post('/api/login', json={'username': 'testuser', 'password': 'testpass'})
    return response.get_json()['token']

def test_register(client):
    response = client.post('/api/register', json={
        'username': 'newuser',
        'password': 'newpass',
        'role': 'user'
    })
    assert response.status_code == 201
    assert response.get_json()['message'] == 'User registered'

def test_login(client):
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 200
    assert 'token' in response.get_json()

def test_create_task(client):
    token = get_token(client)
    response = client.post('/api/tasks', json={
        'title': 'Test Task',
        'description': 'Test Description'
    }, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 201
    assert response.get_json()['title'] == 'Test Task'

def test_get_tasks(client):
    token = get_token(client)
    client.post('/api/tasks', json={
        'title': 'Get Task',
        'description': 'Task to get'
    }, headers={'Authorization': f'Bearer {token}'})
    response = client.get('/api/tasks', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
    assert len(response.get_json()) >= 1

def test_get_task_by_id(client):
    token = get_token(client)
    create_resp = client.post('/api/tasks', json={
        'title': 'Find Me',
        'description': 'Specific Task'
    }, headers={'Authorization': f'Bearer {token}'})
    task_id = create_resp.get_json()['id']
    response = client.get(f'/api/tasks/{task_id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.get_json()['title'] == 'Find Me'

def test_update_task(client):
    token = get_token(client)
    create_resp = client.post('/api/tasks', json={
        'title': 'Old Title'
    }, headers={'Authorization': f'Bearer {token}'})
    task_id = create_resp.get_json()['id']
    update_resp = client.put(f'/api/tasks/{task_id}', json={
        'title': 'Updated Title',
        'completed': True
    }, headers={'Authorization': f'Bearer {token}'})
    assert update_resp.status_code == 200
    assert update_resp.get_json()['title'] == 'Updated Title'
    assert update_resp.get_json()['completed'] is True

def test_delete_task(client):
    token = get_token(client)
    create_resp = client.post('/api/tasks', json={
        'title': 'To be deleted'
    }, headers={'Authorization': f'Bearer {token}'})
    task_id = create_resp.get_json()['id']
    delete_resp = client.delete(f'/api/tasks/{task_id}', headers={'Authorization': f'Bearer {token}'})
    assert delete_resp.status_code == 200
    assert delete_resp.get_json()['message'] == 'Task deleted'
