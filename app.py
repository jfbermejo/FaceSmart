from flask import Flask, g, render_template, flash, url_for, redirect
from flask_login import LoginManager
import modelos
import forms

# G es un objeto global donde podemos guardar lo que queramos de nuestra aplicación
#     por ejemplo una conexión a la base de datos o el usuario conectado en ese momento

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'adfjiuerkasdf.,admfoiwehfnmnsd,f.1279q283!ADFGEWXCVBC$' # Llave secreta aleatoria identificar la app

login_manager = LoginManager()
login_manager.init_app(app)  # Le decimos a login manager que gestione las sesiones de esta app
login_manager.login_view = 'login'  # Cuál es vista o función llamada y despleguada al usr al iniciar sesión o redirigir


# Método que carga el usuario logueado
@login_manager.user_loader
def load_user(userid):
    try:
        return modelos.User.get(modelos.User.id == userid)
    except modelos.DoesNotExist:
        return None


# Métodos que se declaran por convención para invocar antes y después de la petición
# Before para establecer la conexión a la BdD y after para cerarla
@app.before_request
def before_request():
    """Conecta a la base de datos antes de cada petición"""
    g.db = modelos.DATABASE
    if g.db.is_closed():  # Comprueba que la conexión no está abierta
        g.db.connect()


@app.after_request
def after_request(response):
    """"Cierra la conexión a la base de datos"""
    g.db.close()
    return response


@app.route('/')
def index():
    return 'Hey'


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():  # Valida la info recibida con los validadores definidos en forms.py
        flash('Has sido registrado!!!', 'success')
        modelos.User.create_user(
            username= form.username.data,
            email= form.email.data,
            password= form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


if __name__ == '__main__':
    modelos.initialize()
    modelos.User.create_user(
        username='juan',
        email='jfbermejo@gmail.com',
        password='juan1314',
    )
    app.run(debug=DEBUG, host=HOST, port=PORT)
