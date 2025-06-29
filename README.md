# Task Manager System

## Features
- **JWT Authentication** with secure password hashing
- **Role-based Access Control** (Admin/User permissions)
- **Task CRUD Operations** with filtering and pagination
- **Input Validation** and error handling
- **SQLite Database** with proper relationships
- **Comprehensive Unit Tests**
- **Postman Collection** for API testing

## Role Permissions
- **Users**: Can create tasks, view own tasks
- **Admins**: Can update/delete any task, view all tasks

## API Endpoints
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `GET /api/tasks` - List tasks (with pagination/filtering)
- `POST /api/tasks` - Create task
- `GET /api/tasks/{id}` - Get specific task
- `PUT /api/tasks/{id}` - Update task (Admin only)
- `DELETE /api/tasks/{id}` - Delete task (Admin only)

## Setup
```bash
pip install -r requirements.txt
python app.py
```

## Testing
```bash
pytest tests/ -v
```

## API Documentation
Import `postman_collection.json` into Postman for complete API examples with authentication.
