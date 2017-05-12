from flask import Flask
from flask import session, url_for,redirect, render_template,request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail,Message
from datetime import datetime
import enum

app = Flask(__name__)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config["MAIL_USERNAME"]='flaskmail11@gmail.com'
app.config["MAIL_PASSWORD"]='flask123456789'
app.config["MAIL_USE_SSL"]=True
mail=Mail(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://scott:test123@localhost/todolist'
app.config['SECRET_KEY'] = "Formation TP 12354"
db = SQLAlchemy(app)


class AccountType(enum.Enum):
    FREE = "free"
    PREMIUM = "Premium"

class User(db.Model):
    """Attributes for User."""
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(20), nullable = False)
    account = db.Column(db.Enum(AccountType), default=AccountType.FREE)
    join_date = db.Column(db.DateTime, default=datetime.now)
    confirmation=db.Column(db.String(20),nullable=False)

    def __init__(self,email,name,password,account = None,join_date = None,confirmation = None):
        super(User, self).__init__()
        self.email = email
        self.name = name;
        self.password = password
        if account is None:
            self.account = AccountType.FREE
        else:
            self.account = account
        if join_date is None:
            self.join_date = datetime.now()
        else:
            self.join_date = join_date
        if confirmation is None:
            self.confirmation= "false"
        else:
            self.confirmation = "true"

"""User class end."""

class Todo(db.Model):
    """Attributes for Todo."""
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(50))
    body = db.Column(db.String(255), unique = True)
    pub_date = db.Column(db.DateTime,default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('todos')) #todos a query ref for easier access

    def __init__(self, title,body, user):
        super(Todo, self).__init__()
        self.title = title
        self.body = body
        self.user = user

"""Todo class end."""

class Item(db.Model):
    """Attributes for Item."""
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(255), unique = True)
    pub_date = db.Column(db.DateTime,default=datetime.now)
    due_date = db.Column(db.DateTime)
    done =  db.Column(db.Boolean, default=False, nullable=False)

    todo_id = db.Column(db.Integer, db.ForeignKey('todo.id'))
    todo = db.relationship('Todo', backref=db.backref('items')) #items: a query ref for easier access

    def __init__(self, body, due_date, todo, done = False):
        super(Item, self).__init__()
        self.body = body
        self.pub_date = datetime.now()
        self.due_date = due_date
        self.done = done
        self.todo = todo


"""Item class end."""

@app.route('/')
def index():

    if session.get('logged_in'):
        user = User.query.filter_by(email = session['email']).first()
        todos = user.todos
        return render_template('index.html',todos =todos)
    else:
        return redirect(url_for('login'))



@app.route('/register', methods = ['GET'])
def register():
    return render_template('register.html')

@app.route('/login', methods = ['GET'])
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/user', methods = ['POST'])
def add_user():
    if request.form['password'] != request.form['confirm-password']:
        flash('Password don\'t match ')
        return redirect(url_for('register'))

    user = User(request.form['email'],request.form['name'],request.form['password'])
    db.session.add(user)
    db.session.commit()
    session['email'] = user.email
    session['name'] = user.name
    session['logged_in'] = True

    msg=Message(
        'Hello',
	sender='flaskmail1@gmail.com',
	recipients=[user.email])
    msg.body="localhost:5000/confirmation/"+user.email
    mail.send(msg)
    return redirect(url_for('index'))

@app.route('/find', methods = ['POST'])
def find_user():

    user = User.query.filter_by(email=username,password=password).first()
    if user is not None:
        session['email'] = request.form['email']
        session['logged_in'] = True
        return redirect(url_for('index'))
    flash('Wrong Credentials')
    return redirect(url_for('login'))

@app.route('/todo', methods = ['GET'])
def todo():

    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        return render_template('add_todo.html')

@app.route('/addTodo',methods= ['POST'])
def addTodo():
    user = User.query.filter_by(email = session['email']).first();
    title = request.form['title']
    body =  request.form['body']
    todo = Todo(title,body,user)
    db.session.add(todo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/todolist')
def todolist():
    todo_id = request.args.get('id')
    todo = Todo.query.filter_by(id = todo_id).first();
    items = todo.items
    return render_template('todolist.html',items =items, id = todo.id)

@app.route('/addItem',methods= ['POST'])
def addItem():
    todo_id =  request.form['id']
    todo = Todo.query.filter_by(id = todo_id).first();
    body =  request.form['text']
    date = request.form['dueDate']
    item = Item(body,date,todo)
    db.session.add(item)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/changeItem',methods= ['POST'])
def changeItem():
    item_id =  request.form['id']
    item = Item.query.filter_by(id = item_id).first();
    if(request.form['submit']=='done'):
        item.done = True
    else:
        db.session.delete(item)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/confirmation/<mail>')
def confirm(mail):
    user=User.query.filter_by(email=mail).update(dict(confirmation="true"))
    db.session.commit()
    session['confirmation']=True
    return " votre compte est confirme %s "% mail

if __name__ == "__main__":
    app.run(debug=True)
