from datetime import datetime
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

    def __init__(self, id, sender, receiver, amount, time):
        self.id = id
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.time = time

db.create_all()
admin = account(id=0, username="admin", password="12345", balance=0)
eric = account(id=None, username="eric", password="uci266", balance=100)
db.session.add(admin)
db.session.add(eric)
db.session.commit()

@app.route("/", methods = ['POST', 'GET'])
def index():
    return render_template("index.html")

@app.route("/login", methods = ['POST', 'GET'])
def login():
    id = request.form.get("account_number")
    password = request.form.get("password")
    acc = account.query.get(id)
    print(acc.password)
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
        new_acc = account(id = None, username = name, password = password, balance = 0)
        db.session.add(new_acc)
        db.session.commit()
        last = account.query.filter_by(username = name).first()
        session[str(last.id)] = name
        return redirect(url_for('user', id = last.id))

@app.route("/logout/<id>")
def logout(id):
    session.pop(id, None)
    return redirect(url_for("index"))

@app.route("/send/<id>", methods = ['POST', 'GET'])
def send(id):
    if id in session:
        if request.method == "GET":
            return render_template("send.html")
        if request.method == "POST":
            transfer_to = request.form.get('transfer_to')
            amount = request.form.get('amount')
            #todo: get my real id
            my_id = 1
            if verify(transfer_to, amount, my_id):
                sender = db.session.query(account).filter_by(id = my_id).first()
                sender.balance -= int(amount)
                receiver = db.session.query(account).filter_by(id = transfer_to).first() 
                receiver.balance += int(amount)
                new_record = record(id = None, sender = sender.id, receiver = receiver.id, amount = amount, time = str(datetime.now().time))
                db.session.add(new_record)         
                db.session.commit()
                return ("transfer to account: " + transfer_to, "amount: " + amount)
            else:
                return "Transaction failed"      
    else:
        return redirect(url_for("index"))

def verify(transfer_to, amount, my_id):    
    # transfer_to exist in db
    exist = db.session.query(account).filter_by(id = transfer_to).first() is not None
    if not exist:
        app.logger.error('not exist')
    enough_balance = int(db.session.query(account).filter_by(id = my_id).first().balance) >= int(amount)
    if not enough_balance:
        app.logger.error('not enough balance')
    if exist and enough_balance:
        return True
    else:
        return False

@app.route("/user/<id>")
def user(id):
    # 临时数据
    records = [
        {
            'receiver': 'Tom',
            'amount': 100,
            'time': 'june 6, 2010'
        },
        {
            'receiver': 'Jerry',
            'amount': 250,
            'time': 'May 5, 2010'
        }
    ]

    balance = 1000
    acc = account.query.get(id);
    return render_template("user.html", id=id, name = acc.username, balance = acc.balance, records = records)

if __name__ == "__main__":
    app.run(debug=True)