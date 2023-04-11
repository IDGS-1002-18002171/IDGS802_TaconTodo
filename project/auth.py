from flask import Blueprint,render_template,redirect,url_for,request,flash,abort,session
from werkzeug.security import generate_password_hash,check_password_hash
from flask_security import login_required
from flask_security.utils import login_user,logout_user,hash_password,encrypt_password
from .models import User
import logging
from . import db,userDataStore
from flask_login import current_user
from datetime import datetime
from flask_wtf.csrf import generate_csrf
from flask_wtf.csrf import validate_csrf


auth=Blueprint('auth', __name__,url_prefix='/security')



@auth.route('/login')
def login():
    csrf_token = generate_csrf()
    return render_template('/security/login.html',csrf_token=csrf_token)

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    try:
        validate_csrf(request.form.get('csrf_token'))
    except ValidationError:
        # El token CSRF no coincide, rechazar la solicitud
        abort(403)
    #Consultamos si existe el usuario registrado con ese email
    user = User.query.filter_by(email=email).first()
    
    #Verificamos si el usuario existe y comprobamos el password
    if not user or not check_password_hash(user.password, password):
        flash('El usuario y/o password son incorrectos')
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.error(f'Fallo al iniciar sesion id:{user.id} name:{user.name} correo:{user.email} fecha:{current_time}')
        logging.shutdown()
        return redirect(url_for('auth.login')) #Rebotamos a la página de login

    #Si llegamos aquí los datos son correctos y creamos una session para el usuario
    login_user(user, remember=remember)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.debug(f'Inicio sesion del usuario .... id:{user.id} name:{user.name} correo:{user.email} fecha:{current_time}')
    logging.shutdown()
    return redirect(url_for('main.profile'))

@auth.route('/register')
def register():
    return render_template('/security/register.html')

@auth.route('/register', methods=['POST'])
def register_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    #Consultamos si existe un usuario registrado con ese email
    user = User.query.filter_by(email=email).first()

    if user:
        flash('El correo ya está en uso')
        logging.error('Error de registro, usuario existente')
        logging.shutdown()
        return redirect(url_for('auth.register'))
    
    #Creando un nuevo usuario y lo guardamos en la bd
    userDataStore.create_user(email=email, name=name, password=generate_password_hash(password, method='sha512'))
    db.session.commit()
    logging.info('Registro exitoso')
    logging.shutdown()
    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    #Cerramos sesión
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.debug(f'Sesion concluida para.... id:{current_user.id} name:{current_user.name} correo:{current_user.email} fecha:{current_time}')
    logging.shutdown()
    logout_user()
    return redirect(url_for('main.index'))