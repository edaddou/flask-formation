from flask import Flask
from flask import session, url_for,redirect, render_template,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum


app = Flask(__name__)
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

    def __init__(self, email,name,password):
        super(User, self).__init__()
        self.email = email
        self.name = name;
        self.password = password

"""User class end."""


@app.route('/')
def index():
    if session.get('logged_in') == True:
        return render_template('index.html')
    return redirect(url_for('login'))


@app.route('/register', methods = ['GET'])
def register():
    return render_template('register.html')

@app.route('/login', methods = ['GET'])
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    return redirect(url_for('index'))

@app.route('/user', methods = ['POST'])
def add_user():
    if request.form['password'] != request.form['confirm-password']:
        return redirect(url_for('register'))

    user = User(request.form['name'],request.form['email'],request.form['password'])
    db.session.add(user)
    db.session.commit()
    session['email'] = user.email
    session['name'] = user.name
    session['logged_in'] = True

    return redirect(url_for('index'))

@app.route('/find', methods = ['POST'])
def find_user():

    user = User.query.filter_by(email = request.form['email']).first();
    if user.password == request.form['password']:
        session['email'] = request.form['email']
        session['logged_in'] = True
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))


    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
