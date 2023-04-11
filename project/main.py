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



# Parte de modulos de inventario, compras y productos

@main.route('/inventario')
@login_required
@roles_accepted('Administrador')
def inventario():

    inv = Inventario.query.all()
    matpr = MateriaPrima.query.all()
    pro = Proveedor.query.all()

    mensajeb = "Bienvenido"
    flash("")

    return render_template("inventario.html", inv=inv, materia=matpr,proveedor=pro)

@main.route('/agregarMateria', methods=["POST"])
@login_required
@roles_accepted('Administrador')
def agregarMateria():

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
        flash(mensaje)

        return redirect(url_for("main.inventario"))

    return render_template("inventario.html")

@main.route('/editarMateria', methods=["GET","POST"])
@login_required
@roles_accepted('Administrador')
def editarMateria():

    return render_template("editar_materia_prima.html")



# Rutas del modulo de compras

@main.route("/compra")
@login_required
@roles_accepted('Administrador')
def compras():
    matpri = MateriaPrima.query.all()

    return render_template("compra.html", materia=matpri)


@main.route("/cargar_datos/<int:id>", methods=['POST'])
@login_required
def cargar_datos(id):


    materia =  MateriaPrima.query.get(id)

    return jsonify({"idMateria": materia.id_materia_prima,
                    "proveedor": materia.proveedor.nombre_empresa,
                    "unidad": materia.unidad_medida,
                    "cant_min": materia.cantidad_minima_requerida,
                    "precioCompra": materia.precio_compra
                    })

@main.route("/solicitud_compra", methods=["POST"])
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

        db.session.add(inventory)
        db.session.commit()

        return redirect(url_for("main.compras"))
    
    return render_template("compra.html")

# Funiciones o rutas del modulo de productos

@main.route("/producto")
@login_required
@roles_accepted('Administrador')
def producto():
    return render_template("producto.html")