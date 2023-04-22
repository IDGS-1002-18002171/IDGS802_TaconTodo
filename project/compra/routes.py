from flask import Blueprint,render_template, redirect, url_for
from flask_security import login_required,current_user
from flask_security.decorators import roles_required,roles_accepted
from ..models import db,Inventario, Producto, MateriaPrima, Proveedor
from flask import jsonify, request, flash
from datetime import datetime
import logging

compra = Blueprint('compra', __name__)

@compra.route("/compra")
@login_required
@roles_accepted('Administrador')
def compras():
    matpri = MateriaPrima.query.all()

    return render_template("compra.html", materia=matpri)


@compra.route("/cargar_datos/<int:id>", methods=['POST'])
@login_required
def cargar_datos(id):


    materia =  MateriaPrima.query.get(id)

    return jsonify({"idMateria": materia.id_materia_prima,
                    "proveedor": materia.proveedor.nombre_empresa,
                    "unidad": materia.unidad_medida,
                    "cant_min": materia.cantidad_minima_requerida,
                    "precioCompra": materia.precio_compra
                    })


@compra.route("/solicitud_compra", methods=["POST"])
@login_required
@roles_accepted('Administrador')
def solicitud_compra():

    if request.method == "POST":

        id = request.form.get("IDMP")
        cant_add = request.form.get("cantidad_c")
        cant_min = request.form.get("cantidad_minima")
        now = datetime.now()
        
        inventory = db.session.query(Inventario).filter(Inventario.id_inventario==id).first()

        cant_act = inventory.cantidad_almacenada
        cant_new = float(cant_act) + float(cant_add)

        inventory.cantidad_almacenada = cant_new
        inventory.fecha_registro = now.date()
        success_message='Compra exitosa'
        flash(success_message,category='success')
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.debug(f'Compra de material realizada por .... id:{current_user.id} name:{current_user.name} correo:{current_user.email} fecha:{current_time}')
        logging.shutdown()
        db.session.add(inventory)
        db.session.commit()
        


        return redirect(url_for("compra.compras"))
    
    return render_template("compra.html")