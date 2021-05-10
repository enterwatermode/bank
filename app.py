from flask import Flask, request, render_template,  redirect, url_for
app = Flask(__name__)


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

@app.route("/send")
def send():
    return render_template("send.html")

@app.route("/user/<name>")
def user(name):
    return render_template("user.html", name=name)

if __name__ == "__main__":
    app.run(debug=True)