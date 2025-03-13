from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime, timedelta
 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET'])
def get_todos():
    # Get the all of the todos
    query = Todo.query
    result = []

    # Check for completed tasks
    completed = request.args.get('completed')

    # Check for tasks 5 days into the future
    window = request.args.get('window', type=int)

    # Filters for completed todo tasks.
    if completed is not None:
        completed = completed.lower() == 'true'
        query = query.filter(Todo.completed == completed)

    # Filters for 5 days.
    if window is not None:
        current_date = datetime.now()
        future_date = current_date + timedelta(days=window)
        query = query.filter(Todo.deadline_at <= future_date)

    todos = query.all()

    for todo in todos:
        result.append(todo.to_dict())

    """Return the list of todo items"""
    return jsonify(result)

@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):

    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404

    """Return the details of a todo item"""
    return jsonify(todo.to_dict())

@api.route('/todos', methods=['POST'])
def create_todo():

    # Create a parameter for allowed fields
    allowed_parameters = {'title', 'description', 'completed', 'created_at', 'updated_at', 'deadline_at'}

    # Check for erroneous fields.
    if not set(request.json.keys()).issubset(allowed_parameters):
        print(set(request.json.keys()))
        return jsonify({'error': 'Erroneous field detected.'}), 400
    
    # Check for missing title
    if request.json.get('title') is None:
        return jsonify({'error': 'Title must not be missing'}), 400

    todo = Todo(
        title=request.json.get('title'),
        description=request.json.get('description'),
        completed=request.json.get('completed', False),
    )

    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))


    
    # Adds a new record to the database or will an update an existing record
    db.session.add(todo)

    # Commits the changes to the database
    # Must be called for the changes to be saved
    db.session.commit()

    print(todo.to_dict())

    """Create a new todo item and return the created item"""
    return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):

    todo = Todo.query.get(todo_id)
    if todo is None:
         return jsonify({'error': 'Todo not found'}), 404

    # Create a parameter for allowed fields
    allowed_parameters = {'title', 'description', 'completed', 'created_at', 'updated_at', 'deadline_at'}

    # Check for erroneous fields.
    if not set(request.json.keys()).issubset(allowed_parameters):
         return jsonify({'error': 'Erroneous field detected.'}), 400

    # Stop any ID change
    if 'id' in request.json:
        return jsonify({'error': 'You cannot change the ID.'}), 400
    
    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)
    db.session.commit()

    """Update a todo item and return the updated item"""
    return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):

    todo = Todo.query.get(todo_id)

    if todo is None:
         return jsonify({'error': 'Todo not found'}), 200

    db.session.delete(todo)
    db.session.commit()

    """Delete a todo item and return the deleted item"""
    return jsonify(todo.to_dict()), 200
 
