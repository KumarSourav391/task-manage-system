from flask import Blueprint, request, jsonify
from extensions import db
from models.task import Task
from schemas.task_schema import TaskSchema
from utils.jwt import token_required, admin_required

task_bp = Blueprint('task_bp', __name__)

@task_bp.route('/tasks', methods=['GET'])
@token_required
def get_tasks(current_user):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    completed = request.args.get('completed')

    query = Task.query if current_user['role'] == 'admin' else Task.query.filter_by(user_id=current_user['id'])
    if completed is not None:
        query = query.filter_by(completed=(completed.lower() == 'true'))
    tasks = query.paginate(page=page, per_page=per_page, error_out=False)
    return TaskSchema(many=True).jsonify(tasks.items)

@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
@token_required
def get_task(current_user, task_id):
    task = Task.query.get_or_404(task_id)
    if current_user['role'] != 'admin' and task.user_id != current_user['id']:
        return jsonify({"message": "Unauthorized"}), 403
    return TaskSchema().jsonify(task)

@task_bp.route('/tasks', methods=['POST'])
@token_required
def create_task(current_user):
    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({"message": "Title is required"}), 400
    if len(data['title'].strip()) < 1:
        return jsonify({"message": "Title cannot be empty"}), 400
    task = Task(
        title=data['title'].strip(),
        description=data.get('description', '').strip(),
        user_id=current_user['id']
    )
    db.session.add(task)
    db.session.commit()
    return TaskSchema().jsonify(task), 201

@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@admin_required
def update_task(current_user, task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), 400
    if 'title' in data and len(data['title'].strip()) < 1:
        return jsonify({"message": "Title cannot be empty"}), 400
    task.title = data.get('title', task.title).strip() if data.get('title') else task.title
    task.description = data.get('description', task.description).strip() if 'description' in data else task.description
    task.completed = data.get('completed', task.completed)
    db.session.commit()
    return TaskSchema().jsonify(task)

@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@admin_required
def delete_task(current_user, task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"})