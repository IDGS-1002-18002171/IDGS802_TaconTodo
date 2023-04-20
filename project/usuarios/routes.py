from flask import Blueprint,render_template,abort,session
from flask_security import login_required,current_user, login_user
from flask_security.decorators import roles_required,roles_accepted
from ..models import User, db
from flask import Flask, jsonify, request, redirect, url_for
import json,os,stripe,logging
from decimal import Decimal
from datetime import datetime
from plyer import notification
from flask_wtf.csrf import generate_csrf,validate_csrf
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request, flash

from werkzeug.security import generate_password_hash, check_password_hash
from flask_security.utils import login_user, logout_user, hash_password, encrypt_password

import base64
import logging
import datetime

from .. import userDataStore

usuarios=Blueprint('usuarios', __name__)





@usuarios.route("/obtenerUsuarios",  methods=['GET','POST'])
def obtenerUsuarios():
    csrf_token = generate_csrf()
    date = datetime.datetime.now()
    logging.debug("se cargaron las listas de usuarios en la fecha: " + date.strftime("%d/%m/%Y") + " " + date.strftime("%H:%M:%S") )
    logging.shutdown()
    filtro = request.form.get("filtro")
    if filtro:
        usuarios = User.query.filter(
            (User.id.ilike(f"%{filtro}%")) |
            (User.name.ilike(f"%{filtro}%")) |
            (User.email.ilike(f"%{filtro}%")) |
            (User.active.ilike(f"%{filtro}%")) 
            ).all()
    else:
        usuarios = User.query.all()
    return render_template("/usuarios.html", lista = usuarios,csrf_token=csrf_token)



@usuarios.route("/guardarUsuario", methods=['GET','POST'])
def guardarUsuario():
    id= str(request.form.get("id"))
    name = str(request.form.get("name"))
    email = str(request.form.get("email"))
    password=str(request.form.get("contraseña"))
    #password = request.form.get('password')
    
    rol = request.form['tipos']
    print(rol)

    


    print(len(id))
    if len(id) > 0 :
        usuarioElejido = User.query.filter_by(id=int(id)).first()
        usuarioElejido.name = name
        usuarioElejido.email = email
        db.session.commit()


        if rol == 'Usuario':
            rol = userDataStore.find_role('Usuario')
        elif rol == 'empleado':
            rol = userDataStore.find_role('empleado')
        elif rol == 'repartidor':
            rol = userDataStore.find_role('repartidor')
        else:
            rol = userDataStore.find_role('Administrador')
        
        user = User.query.filter_by(id=int(id)).first()
        user.roles = []
        user.roles.append(rol)
        db.session.commit()
    else:
        userDataStore.create_user(email=email, name=name, password=generate_password_hash(password, method='sha512'))
        db.session.commit()

    date = datetime.datetime.now()
    logging.debug("se guardo el usuario con el id: " + id + " el dia: " + date.strftime("%d/%m/%Y") + " " + date.strftime("%H:%M:%S") )
    logging.shutdown()
    success_message = 'listo, usuario guardado'
    flash (success_message,category='success')
        
    return redirect(url_for("usuarios.obtenerUsuarios"))


@usuarios.route("/eliminarUsuario", methods=['GET','POST'])
def eliminarUsuario():
    try:
        validate_csrf(request.form.get('csrf_token'))
    except :
        # El token CSRF no coincide, rechazar la solicitud
        abort(403)
    id= str(request.form.get("id"))
    usuarioElejido = User.query.filter_by(id=int(id)).first()
    usuarioElejido.active = 0
    db.session.commit()

    date = datetime.datetime.now()
    logging.debug("se elimino el usuario con el id: " + id + " el dia: " + date.strftime("%d/%m/%Y") + " " + date.strftime("%H:%M:%S") )
    logging.shutdown()
    success_message = 'listo, usuario eliminado'
    flash (success_message,category='success')
    return redirect(url_for("usuarios.obtenerUsuarios"))

@usuarios.route("/usuarioSeleccionado", methods=['GET','POST'])
def usuarioSeleccionado():
    try:
        validate_csrf(request.form.get('csrf_token'))
    except :
        # El token CSRF no coincide, rechazar la solicitud
        abort(403)
    id= str(request.form.get("id"))
    name = str(request.form.get("name"))
    email = str(request.form.get("email"))
    tipo = str(request.form.get("tipo"))


    date = datetime.datetime.now()
    logging.debug("se selecciono el usuario con el id: " + id + " el dia: " + date.strftime("%d/%m/%Y") + " " + date.strftime("%H:%M:%S") )
    logging.shutdown()
    filtro = request.form.get("filtro")
    if filtro:
        usuarios = User.query.filter(
            (User.id.ilike(f"%{filtro}%")) |
            (User.name.ilike(f"%{filtro}%")) |
            (User.email.ilike(f"%{filtro}%")) |
            (User.active.ilike(f"%{filtro}%")) 
            ).all()
    else:
        usuarios = User.query.all()
    return render_template("/usuarios.html", lista = usuarios, id=id, name=name,
                           email=email, tipo=tipo)
