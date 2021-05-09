from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'
db = SQLAlchemy(app)

class account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    balance = db.Column(db.Integer)

    def __init__(self, id, username, password, balance):
        self.id = id
        self.username = username
        self.password = password
        self.balance = balance
class record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.Integer)
    receiver = db.Column(db.Integer)
    amount = db.Column(db.Integer)
    time = db.Column(db.Text)

    def __init__(self, sender, receiver, amount, time):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.time = time

db.create_all()
admin = account(id=0, username="admin", password="12345", balance=0)
eric = account(id=1, username="eric", password="uci266", balance=100)
db.session.add(admin)
db.session.add(eric)
db.session.commit()

@app.route("/")
def index():
    return account.query.all()
    # return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/send")
def send():
    return render_template("send.html")

@app.route("/user/<name>")
def user(name):
    return render_template("user.html", name=name)

if __name__ == "__main__":
    app.run(debug=True)