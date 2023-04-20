from flask import Blueprint,render_template, redirect, url_for
from flask_security import login_required,current_user
from flask_security.decorators import roles_required,roles_accepted
from ..models import Inventario, Producto, MateriaPrima, Proveedor,db
from flask import jsonify, request, flash
from datetime import datetime
import logging
from .forms import InventarioForm
from flask_wtf.csrf import generate_csrf,validate_csrf

inven = Blueprint('inven', __name__)

# Parte de modulos de inventario, compras y productos

@inven.route('/inventario', methods=["GET"])
@login_required
@roles_accepted('Administrador')
def inventario():

    inv = Inventario.query.all()
    matpr = MateriaPrima.query.all()
    pro = Proveedor.query.all()

    return render_template("inventario.html", inv=inv, materia=matpr,proveedor=pro)

@inven.route('/agregarMateria', methods=["POST"])
@login_required
@roles_accepted('Administrador','Empleado')
def agregarMateria():
    csrf_token = generate_csrf()
    if request.method == "POST":
        materiapr = MateriaPrima(
            id_proveedor = request.form.get("idPro"),
            nombre = request.form.get("nombreMa"),
            unidad_medida = request.form.get("UnitM"),
            cantidad_minima_requerida = request.form.get("cantMin"),
            precio_compra = request.form.get("precioC")
        )

        db.session.add(materiapr)
        db.session.commit()

        mensaje = "Se agrego correctamente la materia prima"
        flash(mensaje, "success")

        return redirect(url_for("inven.inventario"))

    return render_template("inventario.html",csrf_token=csrf_token)


@inven.route('/editarMateria', methods=["GET","POST"])
@login_required
@roles_accepted('Administrador')
def editarMateria():
    formulario = InventarioForm(request.form)
    csrf_token = generate_csrf()
    formulario.proveedor.choices =[(pro.id_proveedor, pro.nombre_empresa) for pro in Proveedor.query.all()]
    if request.method == "GET":

        id=request.args.get("id")
        materiapr = MateriaPrima.query.get(id)
        
        formulario.idMateria.data = id
        
        formulario.proveedor.process_data(materiapr.id_proveedor)
        formulario.nombreMatpri.data = materiapr.nombre
        formulario.unidadMedida.data = materiapr.unidad_medida
        formulario.cantMinima.data = materiapr.cantidad_minima_requerida
        formulario.precioCompra.data = materiapr.precio_compra
        
    if request.method == "POST":

        idMateria = formulario.idMateria.data

        mate = db.session.query(MateriaPrima).filter(MateriaPrima.id_materia_prima==idMateria).first()

        mate.id_proveedor = float(formulario.proveedor.data)
        mate.nombre = formulario.nombreMatpri.data
        mate.unidad_medida = formulario.unidadMedida.data
        mate.cantidad_minima_requerida = formulario.cantMinima.data
        mate.precio_compra = formulario.precioCompra.data


        flash("Se actualizo correctamente", "success")
        db.session.add(mate)
        db.session.commit()
        
        return redirect(url_for("inven.inventario"))      

    return render_template("editar_materia_prima.html",form=formulario)