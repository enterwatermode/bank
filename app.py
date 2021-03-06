from datetime import datetime
from flask import Flask, request, render_template,  redirect
from flask.globals import session
from flask_sqlalchemy import SQLAlchemy
from flask import send_file
from flask import request, g, redirect
from urllib.parse import urlparse, urljoin
import os
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'
app.secret_key = 'uci266p'
db = SQLAlchemy(app)

class account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    balance = db.Column(db.Float)

    def __init__(self, id, username, password, balance):
        self.id = id
        self.username = username
        self.password = password
        self.balance = balance
        
class record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.Integer)
    receiver = db.Column(db.Integer)
    amount = db.Column(db.Float)
    time = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, id, sender, receiver, amount, time):
        self.id = id
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.time = time

db.create_all()
admin = account(id=0, username="admin", password="12345", balance=10.00)
eric = account(id=None, username="eric", password="uci266", balance=100.00)
db.session.add(admin)
db.session.add(eric)
db.session.commit()

#main 
@app.route("/", methods = ['POST', 'GET'])
def index():
    return render_template("index.html")

#login 
@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == "POST":
        id = int(request.form.get("account_number"))
        password = request.form.get("password")
        acc = account.query.get(id)
        if acc is not None and acc.password == password:
            session[str(id)] = acc.username
            return "OK"
        return "ERROR"
    elif request.method == "GET":
        return redirect("/")

#register page
@app.route("/register", methods = ['POST', 'GET'])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        name = request.form.get('name')
        password = request.form.get('password')
        init = request.form.get('init')
        new_acc = account(id = None, username = name, password = password, balance = init)
        db.session.add(new_acc)
        db.session.commit()
        last = account.query.filter_by(username = name).first()
        session[str(last.id)] = name
        return str(last.id)

#logged in user 
@app.route("/user/<id>")
def user(id):
    acc = account.query.get(id)
    return render_template("user.html", id = id, name = acc.username, balance = acc.balance, msg = "", records = getRecords(id))

#user log out, redirect to index page
@app.route("/logout", methods = ['POST', 'GET'])
def logout():
    if request.method == "POST":
        id = request.form.get('id')
        session.pop(id, None)
    return redirect("/")

#request money transfer to another user
@app.route("/send", methods = ['POST', 'GET'])
def send():
    if request.method == "POST":
        my_id = int(request.form.get('id'))
        # Check the user id is equal to the id in the session to make sure the user cannot transfer others' money
        if str(my_id) in session:
            transfer_to = int(request.form.get('transfer_to'))
            amount = float(request.form.get('amount'))
            if CheckValidNumber(amount) and verify(transfer_to, amount, my_id):
                sender = db.session.query(account).filter_by(id = my_id).first()
                sender.balance -= amount
                receiver = db.session.query(account).filter_by(id = transfer_to).first() 
                receiver.balance += amount
                new_record = record(id = None, sender = sender.id, receiver = receiver.id, amount = amount, time = datetime.utcnow())
                db.session.add(new_record)         
                db.session.commit()
                acc = account.query.get(my_id)
                return { "balance": acc.balance, "msg": "You have successfully sent to account: {} {}$!".format(transfer_to, amount), "records": getRecords(my_id) }
            else:
                acc = account.query.get(my_id)
                return { "balance": acc.balance, "msg": "Transaction Failed", "records": getRecords(my_id) }
        else:
            return redirect("/")

def CheckValidNumber(number):
    try:
        # check if the number is digit
        num = float(number)
        # check if the number is negative
        if num < 0:
            return False
        # check if the number has two decimal places at most
        bigNum = num * 100;
        if int(bigNum) != bigNum:
            return False
        # it is valid
        return True
    except ValueError:
        pass 
    return False

#transfer request verification 
def verify(transfer_to, amount, my_id):    
    exist = db.session.query(account).filter_by(id = transfer_to).first() is not None
    if not exist:
        app.logger.error('not exist')
    enough_balance = float(db.session.query(account).filter_by(id = my_id).first().balance) >= float(amount)
    if not enough_balance:
        app.logger.error('not enough balance')
    if exist and enough_balance:
        return True
    else:
        return False

#deposit money
@app.route("/deposit", methods = ['POST', 'GET'])
def deposit():
    if request.method == "POST":
        my_id = int(request.form.get('id'))
        amount = float(request.form.get('amount'))
        if str(my_id) in session:
            customer = db.session.query(account).filter_by(id = my_id).first()
            customer.balance += amount
            new_record = record(id = None, sender = my_id, receiver = my_id, amount = amount, time = datetime.utcnow())
            db.session.add(new_record)         
            db.session.commit()
            acc = account.query.get(my_id)
            return { "balance": acc.balance, "msg": "You have successfully deposited {}$!".format(amount), "records": getRecords(my_id) }

#withdraw money
@app.route("/withdraw", methods = ['POST', 'GET'])
def withdraw():
    if request.method == "POST":
        my_id = int(request.form.get('id'))
        # insufficient balance
        amount = float(request.form.get('amount'))
        if not sufficientBanlance(amount, my_id):
            app.logger.error('insufficient banlance, unable to withdraw money')
            return redirect("/")
        if str(my_id) in session:
            customer = db.session.query(account).filter_by(id = my_id).first()
            customer.balance -= amount
            new_record = record(id = None, sender = my_id, receiver = my_id, amount = -amount, time = datetime.utcnow())
            db.session.add(new_record)         
            db.session.commit()
            acc = account.query.get(my_id)
            return { "balance": acc.balance, "msg": "You have successfully withdrew {}$!".format(amount), "records": getRecords(my_id) }

#balance verification
def sufficientBanlance(amount, my_id):
    return float(db.session.query(account).filter_by(id = my_id).first().balance) >= float(amount)

# get records of a user 
def getRecords(id):
    send_record = db.session.query(record).filter_by(sender = id).all()
    receive_record = db.session.query(record).filter(record.receiver == id, record.sender != id).all()
    records = [{"sender": record.sender, "receiver": record.receiver, "amount": record.amount, "time": record.time.strftime('%B %d %Y - %H:%M:%S')} for record in send_record] \
    + [{"sender": record.sender, "receiver": record.receiver, "amount": record.amount, "time": record.time.strftime('%B %d %Y - %H:%M:%S')} for record in receive_record]
    return records

# download file "f" from /return-files/?file=f
@app.route('/return-files')
def return_file():
    try:
        file = request.args.get('file')
        file_to_download = os.path.join(os.getcwd(), file)
        if os.path.os.path.dirname(file_to_download) == (os.getcwd() + "/public"):
            return send_file(os.path.join(os.getcwd(), file))
        return "file not permitted for downloading or does not exist"
    except Exception as e:
        return str(e)

# redirect to site "abc" from /link/?link=abc
@app.route('/link')
def link():
    link = request.args.get('link')
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, link))
    if host_url.netloc == redirect_url.netloc:
        return redirect(link)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)