
from flask_security.decorators import roles_required,roles_accepted
from . import db



from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_security import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_security.utils import login_user, logout_user, hash_password, encrypt_password

from .models import Proveedor
from .models import User
from . import db, userDataStore
import base64
import logging
import datetime

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










@main.route("/obtenerProveedores",  methods=['GET','POST'])
def obtenerProveedores():
    date = datetime.datetime.now()
    logging.basicConfig(filename='trazabilidad.log', level=logging.INFO)
    logging.info("se cargaron las listas de provedores en la fecha: " + date.strftime("%d/%m/%Y") + " " + date.strftime("%H:%M:%S") )

    filtro = request.form.get("filtro")
    if filtro:
        proveedores = Proveedor.query.filter(
            (Proveedor.id_proveedor.ilike(f"%{filtro}%")) |
            (Proveedor.nombre_contacto.ilike(f"%{filtro}%")) |
            (Proveedor.nombre_empresa.ilike(f"%{filtro}%")) |
            (Proveedor.correo_electronico.ilike(f"%{filtro}%")) |
            (Proveedor.telefono.ilike(f"%{filtro}%")) |
            (Proveedor.direccion.ilike(f"%{filtro}%")) 
            ).all()
    else:
        proveedores = Proveedor.query.all()
    return render_template("/proveedores.html", lista = proveedores)



@main.route("/guardarproveedor", methods=['GET','POST'])
def guardarproveedor():
    id_proveedor= str(request.form.get("id_proveedor"))
    nombre_empresa = str(request.form.get("nombre_empresa"))
    nombre_contacto = str(request.form.get("nombre_contacto"))
    correo_electronico = str(request.form.get("correo_electronico"))
    telefono = str(request.form.get("telefono"))
    direccion = str(request.form.get("direccion"))
    
    print(len(id_proveedor))
    if len(id_proveedor) > 0 :
        proveedorElejido = Proveedor.query.filter_by(id_proveedor=int(id_proveedor)).first()
        proveedorElejido.nombre_empresa = nombre_empresa
        proveedorElejido.nombre_contacto = nombre_contacto
        proveedorElejido.correo_electronico = correo_electronico
        proveedorElejido.telefono = telefono
        proveedorElejido.direccion=direccion
        db.session.commit()
    else:
        proveedorIngresado = Proveedor(nombre_empresa=nombre_empresa, nombre_contacto = nombre_contacto, 
                                       correo_electronico=correo_electronico, telefono=telefono, direccion=direccion)
        db.session.add(proveedorIngresado)
        db.session.commit()

    date = datetime.datetime.now()
    logging.basicConfig(filename='EventosUsuario.log', level=logging.INFO)
    logging.info("se guardo el proveedor con el id: " + id_proveedor + " el dia: " + date.strftime("%d/%m/%Y") + " " + date.strftime("%H:%M:%S") )

    
    return redirect(url_for("main.obtenerProveedores"))


@main.route("/eliminarProveedor", methods=['GET','POST'])
def eliminarProveedor():
    id_proveedor= str(request.form.get("id_proveedor"))
    proveedor = Proveedor.query.get(int(id_proveedor))
    db.session.delete(proveedor)
    db.session.commit()

    date = datetime.datetime.now()
    logging.basicConfig(filename='EventosUsuario.log', level=logging.INFO)
    logging.info("se elimino el proveedor con el id: " + id_proveedor + " el dia: " + date.strftime("%d/%m/%Y") + " " + date.strftime("%H:%M:%S") )

    
    return redirect(url_for("main.obtenerProveedores"))

@main.route("/registroSeleccionado", methods=['GET','POST'])
def registroSeleccionado():
    id_proveedor= str(request.form.get("id_proveedor"))
    nombre_empresa = str(request.form.get("nombre_empresa"))
    nombre_contacto = str(request.form.get("nombre_contacto"))
    correo_electronico = str(request.form.get("correo_electronico"))
    telefono = str(request.form.get("telefono"))
    direccion = str(request.form.get("direccion"))


    date = datetime.datetime.now()
    logging.basicConfig(filename='EventosUsuario.log', level=logging.INFO)
    logging.info("se selecciono el proveedor con el id: " + id_proveedor + " el dia: " + date.strftime("%d/%m/%Y") + " " + date.strftime("%H:%M:%S") )

    filtro = request.form.get("filtro")
    if filtro:
        proveedores = Proveedor.query.filter(
            (Proveedor.id_proveedor.ilike(f"%{filtro}%")) |
            (Proveedor.nombre_contacto.ilike(f"%{filtro}%")) |
            (Proveedor.nombre_empresa.ilike(f"%{filtro}%")) |
            (Proveedor.correo_electronico.ilike(f"%{filtro}%")) |
            (Proveedor.telefono.ilike(f"%{filtro}%")) |
            (Proveedor.direccion.ilike(f"%{filtro}%")) 
            ).all()
    else:
        proveedores = Proveedor.query.all()
    return render_template("/proveedores.html", lista = proveedores, id_proveedor=id_proveedor, nombre_empresa=nombre_empresa,
                           nombre_contacto=nombre_contacto, correo_electronico=correo_electronico,telefono=telefono,
                           direccion=direccion)

    
    











@main.route("/obtenerUsuarios",  methods=['GET','POST'])
def obtenerUsuarios():
    date = datetime.datetime.now()
    logging.basicConfig(filename='trazabilidad.log', level=logging.INFO)
    logging.info("se cargaron las listas de usuarios en la fecha: " + date.strftime("%d/%m/%Y") + " " + date.strftime("%H:%M:%S") )

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
    return render_template("/usuarios.html", lista = usuarios)



@main.route("/guardarUsuario", methods=['GET','POST'])
def guardarUsuario():
    id= str(request.form.get("id"))
    name = str(request.form.get("name"))
    email = str(request.form.get("email"))
    
    print(len(id))
    if len(id) > 0 :
        usuarioElejido = User.query.filter_by(id=int(id)).first()
        usuarioElejido.name = name
        usuarioElejido.email = email
        db.session.commit()
    else:
        usuarioIngresado = User(name=name, email = email)
        db.session.add(usuarioIngresado)
        db.session.commit()

    date = datetime.datetime.now()
    logging.basicConfig(filename='EventosUsuario.log', level=logging.INFO)
    logging.info("se guardo el usuario con el id: " + id + " el dia: " + date.strftime("%d/%m/%Y") + " " + date.strftime("%H:%M:%S") )

    
    return redirect(url_for("main.obtenerUsuarios"))


@main.route("/eliminarUsuario", methods=['GET','POST'])
def eliminarUsuario():
    id= str(request.form.get("id"))
    usuarioElejido = User.query.filter_by(id=int(id)).first()
    usuarioElejido.active = 0
    db.session.commit()

    date = datetime.datetime.now()
    logging.basicConfig(filename='EventosUsuario.log', level=logging.INFO)
    logging.info("se elimino el usuario con el id: " + id + " el dia: " + date.strftime("%d/%m/%Y") + " " + date.strftime("%H:%M:%S") )

    
    return redirect(url_for("main.obtenerUsuarios"))

@main.route("/usuarioSeleccionado", methods=['GET','POST'])
def usuarioSeleccionado():
    id= str(request.form.get("id"))
    name = str(request.form.get("name"))
    email = str(request.form.get("email"))


    date = datetime.datetime.now()
    logging.basicConfig(filename='EventosUsuario.log', level=logging.INFO)
    logging.info("se selecciono el usuario con el id: " + id + " el dia: " + date.strftime("%d/%m/%Y") + " " + date.strftime("%H:%M:%S") )

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
                           email=email)

