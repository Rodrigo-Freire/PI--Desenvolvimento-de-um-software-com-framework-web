import os
from TutorMatch import app
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, SelectField, validators
from wtforms.validators import DataRequired, Length, InputRequired
import psycopg2
from psycopg2 import errors
from flask_bcrypt import generate_password_hash

# class FormUser(FlaskForm):
#     nome_completo = StringField('Nome Completo', [validators.data_required(), validators.Length(min=1, max=100)])
#     data_nascimento = DateField("Data de Nascimento", format='%d-%m-%Y')
#     nome_usuario = StringField("Nome de Usuário", [validators.data_required(), validators.Length(min=1, max=50)])
#     senha = PasswordField("Senha", [validators.data_required()], validators.Length(min=1, max=100))
#     email = StringField("E-mail", [validators.data_required(), validators.Length(min=1, max=100)])
#     tipo_usuario = StringField("Tipo de Usuário", [validators.data_required(), validators.Length(min=1, max=100)])

#Formulário para incluir usuário no DB
class FormUser(FlaskForm):
    nome_completo = StringField('Nome Completo', validators=[DataRequired(), Length(min=1, max=100)])
    # data_nascimento = DateField("Data de Nascimento", format='%d-%m-%Y')
    data_nascimento = DateField("Data de Nascimento", format='%d-%m-%Y', validators=[InputRequired()])
    nome_usuario = StringField("Nickname", validators=[DataRequired(), Length(min=1, max=50)])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(min=1, max=100)])
    email = StringField("E-mail", validators=[DataRequired(), Length(min=1, max=100)])
    tipo_usuario = SelectField("Tipo de Usuário", choices=[('aluno', 'Aluno'), ('professor', 'Professor')], validators=[DataRequired()])
    salvar = SubmitField('Salvar')

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

        cursor.execute("INSERT INTO usuarios(nome_completo, data_nascimento, nome_usuario, senha, email, tipo_usuario) VALUES(%s, %s, %s, %s, %s, %s)", (nome_completo, data_nascimento_str, nome_usuario, generate_password_hash(senha), email, tipo_usuario))
        
        conn.commit()
        return True, "Usuário cadastrado com sucesso."
    except psycopg2.Error as e:
        conn.rollback()
        print("Erro ao inserir usuário:", e)
        return False, "Erro ao inserir usuário. Por favor, tente novamente."
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
