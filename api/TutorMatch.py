from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "Flask_univesp"
app.config.from_pyfile("config.py")

url_database = app.config["DATABASE_URL"]
db = psycopg2.connect(url_database)
csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)

from views import *

if __name__ == "__main__":
    app.run(debug=True,)