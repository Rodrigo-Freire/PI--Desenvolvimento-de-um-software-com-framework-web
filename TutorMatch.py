from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "Flask_univesp"

@app.route('/')
def index():
    return render_template("index.html",)

@app.route('/login')
def login():
    
    return render_template("login.html")

@app.route('/criar-conta')
def criar_conta():
    return render_template("criar_conta.html")

@app.route('/calendario-aulas')
def calendario_aulas():
    return render_template("calendario_aulas.html")

app.run(debug=True,)