from flask import Flask, request, render_template
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

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