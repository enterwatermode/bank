from flask import Flask, request, render_template,  redirect, url_for
from flask.globals import session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'
app.secret_key = 'uci266p'
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

@app.route("/",  methods=['GET'])
def index():
    return render_template("index.html")

@app.route("/login", methods = ["POST"])
def login():
    id = request.form.get("account_number")
    password = request.form.get("password")
    acc = account.query.get(id=id)
    if acc is not None and acc.password == password:
        session[id] = acc.username
        return redirect(url_for('user', id = id, name = "account: {}".format(acc.username), balance = acc.balance)) 
    return render_template("index.html")

@app.route("/register", methods = ['POST', 'GET'])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        name = request.form.get('name')
        password = request.form.get('password')
        new_acc = account(None, name, password, 0)
        db.session.add(new_acc)
        db.session.commit()
        session[id] = name
        return redirect(url_for('user', name = name))

@app.route("/send/<id>", methods = ["POST"])
def send(id):
    if id in session:
        return render_template("send.html")
    else:
        return redirect(url_for("index"))

@app.route("/user/<id>", methods = ["GET"])
def user(id):
    if id in session:
        return render_template("user.html", id = id, name = session[id])
    else:
        return redirect(url_for("index"))

@app.route("/logout/<id>", methods = ["POST"])
def logout(id):
    session.pop(id, None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)