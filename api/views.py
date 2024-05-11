from flask import Flask, render_template, request, redirect, url_for, flash
from TutorMatch import app, db
from utils import FormUser, insert_user

@app.route('/')
def index():
    return render_template("index.html",)

@app.route('/calendario-aulas')
def calendario_aulas():
    return render_template("calendario_aulas.html")

@app.route('/politica_privacidade')
def politica_privacidade():
    return render_template("politica_privacidade.html")

#Rotas referente aos usuário
@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/criar-conta')
def criar_conta():
    form = FormUser()
    return render_template("criar_conta.html", titulo='Criar Conta', form=form)

@app.route('/cadastro-bd-conta', methods=["POST"],)
def cadastro_bd_conta():
    form = FormUser(request.form)

    if not insert_user(db, form):
        flash("Erro ao cadastrar usuário!")
        return redirect(url_for('criar_conta'))
    
    flash("Usuário Cadastrado com Sucesso!")
    return redirect(url_for('login'))