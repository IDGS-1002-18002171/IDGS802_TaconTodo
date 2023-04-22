from flask import Blueprint,render_template,abort,session
from flask_security import login_required,current_user, login_user
from flask_security.decorators import roles_required,roles_accepted
from ..models import Proveedor, db
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




proveedores=Blueprint('proveedores', __name__)


@proveedores.route("/obtenerProveedores",  methods=['GET','POST'])
@login_required
@roles_accepted('Administrador','Empleado')
def obtenerProveedores():
    date = datetime.datetime.now()
    logging.basicConfig(filename='trazabilidad.log', level=logging.INFO)
    logging.info("se cargaron las listas de provedores en la fecha: " + date.strftime("%d/%m/%Y") + " " + date.strftime("%H:%M:%S") )
    csrf_token = generate_csrf()
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
    if len(proveedores) == 0:
        success_message = 'Lo sentimos, no se encontraron coincidencias.'
        flash (success_message,category='warning')
    return render_template("/proveedores.html", lista = proveedores,csrf_token=csrf_token)



@proveedores.route("/guardarproveedor", methods=['GET','POST'])
@login_required
@roles_accepted('Administrador')
def guardarproveedor():
    try:
        validate_csrf(request.form.get('csrf_token'))
    except :
        # El token CSRF no coincide, rechazar la solicitud
        abort(403)
    id_proveedor= str(request.form.get("id_proveedor"))
    nombre_empresa = str(request.form.get("nombre_empresa"))
    nombre_contacto = str(request.form.get("nombre_contacto"))
    correo_electronico = str(request.form.get("correo_electronico"))
    telefono = str(request.form.get("telefono"))
    direccion = str(request.form.get("direccion"))
    
    print(len(id_proveedor))

    if int(telefono) < 0 or len(nombre_empresa) == 0 or len(nombre_contacto) == 0 or len(correo_electronico) == 0 or len(telefono) == 0 or len(direccion) == 0:
        success_message = 'llena todos los campos correctamente'
        flash (success_message,category='warning')
    else:
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

        success_message = 'listo, proveedor guardado'
        flash (success_message,category='success')
    
    return redirect(url_for("proveedores.obtenerProveedores"))


@proveedores.route("/eliminarProveedor", methods=['GET','POST'])
@login_required
@roles_accepted('Administrador')
def eliminarProveedor():
    try:
        validate_csrf(request.form.get('csrf_token'))
    except :
        # El token CSRF no coincide, rechazar la solicitud
        abort(403)
    id_proveedor= str(request.form.get("id_proveedor"))
    proveedor = Proveedor.query.get(int(id_proveedor))
    db.session.delete(proveedor)
    db.session.commit()

    date = datetime.datetime.now()
    logging.basicConfig(filename='EventosUsuario.log', level=logging.INFO)
    logging.info("se elimino el proveedor con el id: " + id_proveedor + " el dia: " + date.strftime("%d/%m/%Y") + " " + date.strftime("%H:%M:%S") )
    success_message = 'listo, proveedor Eliminado'
    flash (success_message,category='success')
    
    return redirect(url_for("proveedores.obtenerProveedores"))

@proveedores.route("/registroSeleccionado", methods=['GET','POST'])
@login_required
@roles_accepted('Administrador','Empleado')
def registroSeleccionado():
    id_proveedor= str(request.form.get("id_proveedor"))
    nombre_empresa = str(request.form.get("nombre_empresa"))
    nombre_contacto = str(request.form.get("nombre_contacto"))
    correo_electronico = str(request.form.get("correo_electronico"))
    telefono = str(request.form.get("telefono"))
    direccion = str(request.form.get("direccion"))
    csrf_token = generate_csrf()

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
                           direccion=direccion,csrf_token=csrf_token)
