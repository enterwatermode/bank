from flask import Flask, request, render_template,  redirect, url_for
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

@app.route("/",  methods=['POST',  'GET'])
def index():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "Post":
        name = account_number = request.form.get('account_number')
        return redirect(url_for('user',name = "account: " + name)) 



@app.route("/register", methods = ['POST', 'GET'])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        name = request.form.get('name')
        return redirect(url_for('user',name = name))

@app.route("/send", methods = ['POST', 'GET'])
def send():
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
            db.session.commit()
            return ("transfer to account: " + transfer_to, "amount: " + amount)
        else:
            return "Transaction failed"    
        

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

    balance = 1000;
    return render_template("user.html", id=id, balance = balance, records = records)

if __name__ == "__main__":
    app.run(debug=True)