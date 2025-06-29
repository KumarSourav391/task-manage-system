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
        user = User(username="testuser", role="user")
        user.set_password("testpass")
        admin = User(username="admin", role="admin")
        admin.set_password("adminpass")
        db.session.add_all([user, admin])
        db.session.commit()
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def get_token(client, username="testuser", password="testpass"):
    response = client.post('/api/login', json={'username': username, 'password': password})
    return response.get_json()['token']

def test_register_validation(client):
    response = client.post('/api/register', json={'username': 'ab', 'password': '123'})
    assert response.status_code == 400
    assert 'min' in response.get_json()['message']

def test_register(client):
    response = client.post('/api/register', json={
        'username': 'newuser',
        'password': 'newpass123',
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

def test_create_task_validation(client):
    token = get_token(client)
    response = client.post('/api/tasks', json={}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 400
    assert 'required' in response.get_json()['message']

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
    client.post('/api/tasks', json={'title': 'Get Task'}, headers={'Authorization': f'Bearer {token}'})
    response = client.get('/api/tasks', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_update_task_admin_only(client):
    user_token = get_token(client)
    admin_token = get_token(client, "admin", "adminpass")
    
    create_resp = client.post('/api/tasks', json={'title': 'Old Title'}, headers={'Authorization': f'Bearer {user_token}'})
    task_id = create_resp.get_json()['id']
    
    # User cannot update
    update_resp = client.put(f'/api/tasks/{task_id}', json={'title': 'Updated'}, headers={'Authorization': f'Bearer {user_token}'})
    assert update_resp.status_code == 403
    
    # Admin can update
    update_resp = client.put(f'/api/tasks/{task_id}', json={'title': 'Admin Updated'}, headers={'Authorization': f'Bearer {admin_token}'})
    assert update_resp.status_code == 200
    assert update_resp.get_json()['title'] == 'Admin Updated'

def test_delete_task_admin_only(client):
    user_token = get_token(client)
    admin_token = get_token(client, "admin", "adminpass")
    
    create_resp = client.post('/api/tasks', json={'title': 'To Delete'}, headers={'Authorization': f'Bearer {user_token}'})
    task_id = create_resp.get_json()['id']
    
    # User cannot delete
    delete_resp = client.delete(f'/api/tasks/{task_id}', headers={'Authorization': f'Bearer {user_token}'})
    assert delete_resp.status_code == 403
    
    # Admin can delete
    delete_resp = client.delete(f'/api/tasks/{task_id}', headers={'Authorization': f'Bearer {admin_token}'})
    assert delete_resp.status_code == 200
