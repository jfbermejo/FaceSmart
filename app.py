from flask import Flask, g, render_template, flash, url_for, redirect, abort
from flask_bcrypt import check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, AnonymousUserMixin
import modelos
import forms

# G es un objeto global donde podemos guardar lo que queramos de nuestra aplicación
#     por ejemplo una conexión a la base de datos o el usuario conectado en ese momento

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'adfjiuerkasdf.,admfoiwehfnmnsd,f.1279q283!ADFGEWXCVBC$' # Llave secreta aleatoria identificar la app


# Definimos nuestro propio usuario anónimo para manejar a los usuarios no logeados
class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = 'Invitado'


login_manager = LoginManager()
login_manager.init_app(app)  # Le decimos a login manager que gestione las sesiones de esta app
login_manager.login_view = 'login'  # Cuál es vista o función llamada y despleguada al usr al iniciar sesión o redirigir
login_manager.anonymous_user = Anonymous


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
        g.user = current_user # Apunta al usuario actual


@app.after_request
def after_request(response):
    """"Cierra la conexión a la base de datos"""
    g.db.close()
    return response


@app.route('/post/<int:post_id>')
def view_post(post_id):
    posts = modelos.Post.select().where(modelos.Post.id == post_id)
    if posts.count() == 0:
        abort(404)
    return render_template('stream.html', stream=posts)


@app.route('/follow/<username>')
@login_required
def follow(username):
    try:
        to_user = modelos.User.get(modelos.User.username**username)
    except modelos.DoesNotExist:
        abort(404)
    else:
        try:
            modelos.Relationship.create(
                from_user=g.user._get_current_object(),
                to_user=to_user
            )
        except modelos.IntegrityError:
            pass
        else:
            flash('Ahora sigues a {}'.format(to_user.username), 'success')
    return redirect(url_for('stream', username=to_user.username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    try:
        to_user = modelos.User.get(modelos.User.username ** username)
    except modelos.DoesNotExist:
        abort(404)
    else:
        try:
            modelos.Relationship.get(
                from_user=g.user._get_current_object(),
                to_user=to_user
            ).delete_instance()
        except modelos.IntegrityError:
            pass
        else:
            flash('Has dejado de seguir a {}'.format(to_user.username), 'success')
    return redirect(url_for('stream', username=to_user.username))


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


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = modelos.User.get(modelos.User.email == form.email.data)
        except modelos.DoesNotExist:
            flash('Tu nombre de usuario o contraseña no existen', 'error')
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('Has iniciado sesión', 'success')
                return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has salido de FaceSmash', 'success')
    return redirect(url_for('index'))


@app.route('/new_post', methods=('GET', 'POST'))
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        modelos.Post.create(user=g.user._get_current_object(),
                            content=form.content.data.strip())
        flash('Mensaje publicado!', 'success')
        return redirect(url_for('index'))
    return render_template('post.html', form=form)


@app.route('/')
def index():
    stream = modelos.Post.select().limit(100)
    return render_template('stream.html', stream=stream)


@app.route('/stream')
@app.route('/stream/<username>')
def stream(username=None):
    template = 'stream.html'    # Template por defecto
    if username and username != current_user.username:
        try:
            user = modelos.User.select().where(modelos.User.username**username).get()   # Nombre parecido, uncase sensitive
        except modelos.DoesNotExist:
            abort(404)
        else:
            stream = user.posts.limit(100)
    else:
        stream = current_user.get_stream().limit(100)
        user = current_user

    if username:
        template = 'user_stream.html'

    return render_template(template, stream=stream, user=user)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    modelos.initialize()
    try:
        modelos.User.create_user(
            username='juan',
            email='jfbermejo@gmail.com',
            password='juan1314',
        )
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)
