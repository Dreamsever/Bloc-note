from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    todos = db.relationship('TodoList', backref='owner', lazy=True)

class TodoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    tasks = db.Column(db.Text)  # JSON-encoded string
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home_page.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)
        user = User(email=email, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please log in.")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('new_page'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route("/list/<int:list_id>")
@login_required
def view_list(list_id):
    todolist = TodoList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    tasks = json.loads(todolist.tasks)
    return render_template("view_list.html", title=todolist.title, list_id=list_id, tasks=tasks)

@app.route("/update_task/<int:list_id>", methods=["POST"])
@login_required
def update_task(list_id):
    data = request.get_json()
    index = data.get("index")
    done = data.get("done")

    todolist = TodoList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    tasks = json.loads(todolist.tasks)
    if 0 <= index < len(tasks):
        tasks[index]["done"] = done
        todolist.tasks = json.dumps(tasks)
        db.session.commit()

    return jsonify(success=True)

@app.route("/delete_list/<int:list_id>", methods=["POST"])
@login_required
def delete_list(list_id):
    todolist = TodoList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    db.session.delete(todolist)
    db.session.commit()
    return jsonify(success=True)

@app.route("/reorder_tasks/<int:list_id>", methods=["POST"])
@login_required
def reorder_tasks(list_id):
    data = request.get_json()
    tasks = data.get("tasks", [])
    todolist = TodoList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    todolist.tasks = json.dumps(tasks)
    print(todolist)
    db.session.commit()

    return jsonify(success=True)

@app.route('/fix_tasks_format')
@login_required
def fix_tasks_format():
    fixed_count = 0
    lists = TodoList.query.filter_by(user_id=current_user.id).all()

    for lst in lists:
        try:
            raw_tasks = json.loads(lst.tasks)

            # If it's a list of strings instead of dicts
            if isinstance(raw_tasks, list) and all(isinstance(task, str) for task in raw_tasks):
                fixed_tasks = [{"text": task, "done": False} for task in raw_tasks]
                lst.tasks = json.dumps(fixed_tasks)
                db.session.commit()
                fixed_count += 1

        except Exception as e:
            return f"Error fixing list {lst.id}: {e}", 500

@app.route('/new_page')
@login_required
def new_page():
    return render_template('new_page.html')

@app.route("/save_tasks", methods=["POST"])
@login_required
def save_tasks():
    data = request.get_json()
    title = data.get("title")
    tasks = data.get("tasks")
    print(tasks)

    if not title or not tasks:
        return jsonify({"success": False, "error": "Missing data"}), 400

    todolist = TodoList(title=title, tasks=json.dumps(tasks), user_id=current_user.id)
    db.session.add(todolist)
    db.session.commit()

    return jsonify({"success": True})

@app.route('/saved_lists')
@login_required
def saved_lists():
    user_lists = TodoList.query.filter_by(user_id=current_user.id).all()
    todolists = [
        {"id": lst.id, "title": lst.title, "tasks": json.loads(lst.tasks)}
        for lst in user_lists
    ]
    return render_template("saved_lists.html", todolists=todolists)


# Optional: custom 404 page
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
