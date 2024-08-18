from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
import psycopg2
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, SelectField, validators
from wtforms.validators import DataRequired, Length, InputRequired
from flask_bcrypt import generate_password_hash, check_password_hash
import time

app = Flask(__name__)
app.secret_key = "Flask_univesp"
app.config.from_pyfile("config.py")

url_database = app.config["DATABASE_URL"]
db = psycopg2.connect(url_database)
csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)

class FormUser(FlaskForm):
    nome_completo = StringField('Nome Completo', validators=[DataRequired(), Length(min=1, max=100)])
    # data_nascimento = DateField("Data de Nascimento", format='%d-%m-%Y')
    data_nascimento = DateField("Data de Nascimento", format='%d-%m-%Y', validators=[InputRequired()])
    nome_usuario = StringField("Nickname", validators=[DataRequired(), Length(min=1, max=50)])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(min=1, max=100)])
    email = StringField("E-mail", validators=[DataRequired(), Length(min=1, max=100)])
    tipo_usuario = SelectField("Tipo de Usuário", choices=[('aluno', 'Aluno'), ('professor', 'Professor')], validators=[DataRequired()])
    salvar = SubmitField('Salvar')

class FormLogin(FlaskForm):
    senha = PasswordField("Senha", validators=[DataRequired(), Length(min=1, max=100)])
    email = StringField("E-mail", validators=[DataRequired(), Length(min=1, max=100)])
    login = SubmitField("Login")

class FormEvent(FlaskForm):
    data = DateField('Data', validators=[DataRequired()])
    hora = StringField('Hora', validators=[DataRequired(), Length(min=1, max=100)])
    nome_aula = StringField('Nome da Aula', validators=[DataRequired(), Length(min=1, max=200)])
    link_aula = StringField('Link da Aula', validators=[DataRequired(), Length(min=1, max=255)])
    salvar = SubmitField('Salvar')

#Insere usuário no DB
def insert_user(conn, form):
    try:
        cursor = conn.cursor()
        email = form.email.data

        # Validar se o e-mail já está cadastrado
        if email_validate(conn, email):
            return False, "E-mail já cadastrado. Por favor, escolha outro e-mail."

        # Continuar com a inserção do usuário
        nome_completo = form.nome_completo.data 
        data_nascimento = form.data_nascimento.raw_data
        data_nascimento_str = ''.join(data_nascimento)
        nome_usuario = form.nome_usuario.data
        senha = form.senha.data
        tipo_usuario = form.tipo_usuario.data

        cursor.execute("INSERT INTO usuarios(nome_completo, data_nascimento, nome_usuario, senha, email, tipo_usuario) VALUES(%s, %s, %s, %s, %s, %s)", (nome_completo, data_nascimento_str, nome_usuario, senha, email, tipo_usuario))
        
        conn.commit()
        return True, "Usuário cadastrado com sucesso."
    except psycopg2.Error as e:
        conn.rollback()
        print("Erro ao inserir usuário:", e)
        return False, "Erro ao inserir usuário. Por favor, tente novamente."
    finally:
        cursor.close()

#Recupera lista de eventos no DB
def recovery_event(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM public.tb_eventos")
        result = cursor.fetchall()
        return result
    except psycopg2.Error as e:
        print("Nenhuma aula cadastrada", e)
        flash("Nenhuma aula cadastrada")
        return False
    finally:
        cursor.close()

#Função para inserir evento na base
def insert_event(conn, form):
    try:
        cursor = conn.cursor()
        data = form.data.data
        hora = form.hora.data
        nome_aula = form.nome_aula.data
        link_aula = form.link_aula.data

        email = session['usuario_logado']
        usuario = user_select(db, email)
        professor = usuario[1]

        cursor.execute("INSERT INTO tb_eventos(data, hora, nome_aula, professor, link_aula) VALUES(%s, %s, %s, %s, %s)", (data, hora, nome_aula, professor, link_aula))
        conn.commit()
        return True, flash('Evento cadastrado com sucesso.')
    except psycopg2.Error as e:
        conn.rollback()
        print("Erro ao inserir evento:", e)
        return False, flash("Erro ao inserir evento. Por favor, tente novamente.")
    finally:
        cursor.close()

#função para recuperar o usuário na base
def user_select(conn, email):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM public.usuarios WHERE email = %s", (email,))
        result = cursor.fetchone()
        return result
    except psycopg2.Error as e:
        print("Usuário não cadastrado.", e)
        return False
    finally:
        cursor.close()

#Função para checar e validar a senha do usuário
def password_check(conn, email):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT senha FROM public.usuarios WHERE email = %s", (email,))
        result = cursor.fetchone()
        return result
    except psycopg2.Error as e:
        print("Usuário não cadastrado.", e)
        return False
    finally:
        cursor.close()

#Função para verificar se o e-mail já existe na base
def email_validate(conn, email):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM public.usuarios WHERE email = %s", (email,))
        result = cursor.fetchone()
        return True if result else False
    except psycopg2.Error as e:
        print("Erro ao validar e-mail:", e)
        return False
    finally:
        cursor.close()

@app.before_request
def clear_session():
    if 'usuario_logado' not in session and 'primeiro_acesso' not in request.cookies:
        session['usuario_logado'] = None
        response = make_response()
        response.set_cookie('primeiro_acesso', 'True')
        return render_template("index.html",)

@app.route('/')
def index():
    return render_template("index.html",)
#Rotas referebte a politica de privacidade
@app.route('/politica_privacidade')
def politica_privacidade():
    return render_template("politica_privacidade.html")

#Rotas referente a lista de eventos
@app.route('/calendario-aulas')
def calendario_aulas():
    if 'usuario_logado' not in session or session["usuario_logado"] == None:
        flash("Você precisa estar logado para acessar o calendário.")
        return redirect(url_for("login"))
    
    eventos = recovery_event(db)
    return render_template("calendario_aulas.html", eventos=eventos)

@app.route('/criar-evento')
def criar_evento():
    email = session['usuario_logado']
    usuario = user_select(db, email)
    if usuario[6] != 'professor':
        flash("Somente professores podem inserir aulas")
        return redirect(url_for("calendario_aulas"))

    form = FormEvent()
    return render_template("criar_evento.html", form=form)

@app.route("/cadastro_bd_evento", methods=["POST"])
def cadastro_bd_evento():
    form = FormEvent(request.form)

    insert_event(db, form)

    return redirect(url_for("calendario_aulas"))


#Rotas referente aos usuário
@app.route('/login')
def login():
    form = FormLogin()
    if session['usuario_logado'] != None:
        flash("Usuário já logado.")
        return redirect(url_for('index'))

    return render_template("login.html", form=form)

@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash(f"Usuário deslogado!")
    return redirect(url_for("index"))

@app.route('/autenticar', methods=["POST"])
def autenticar():
    form = FormLogin(request.form)
    email = form.email.data
    senha = form.senha.data
    senha_db = password_check(db, email)
    usuario = user_select(db, email)

    if not usuario:
        flash(f"Usuário: {email} não cadastrado!")
        return redirect(url_for("login"))
    
    if  senha != senha_db[0]:
        flash("Senha Incorreta!")
        return redirect(url_for("login"))
    else:
        session['usuario_logado'] = usuario[5]
        flash(f"Usuário: {usuario[1]} logado com sucesso!")
        return redirect(url_for('index'))

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

if __name__ == "__main__":
    app.run(debug=True,)