from flask import Blueprint,render_template, redirect, url_for
from flask_security import login_required,current_user
from flask_security.decorators import roles_required,roles_accepted
from . import db
from .models import Inventario, Producto, MateriaPrima, Proveedor
from flask import jsonify, request, flash
from datetime import datetime
import logging


main=Blueprint('main', __name__)

#Definimos la ruta para la página principal
@main.route('/')
def index():
    return render_template('index.html')

#Definimos la ruta para la página de perfil de usuario
@main.route('/profile')
@login_required
#@roles_required('')
@roles_accepted('Administrador','Usuario')
def profile():
    return render_template('profile.html', name=current_user.name)

