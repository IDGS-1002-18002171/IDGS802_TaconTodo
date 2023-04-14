from flask import Blueprint,render_template, redirect, url_for
from flask_security import login_required,current_user
from flask_security.decorators import roles_required,roles_accepted
from ..models import db,Inventario, Producto, MateriaPrima, Proveedor
from flask import jsonify, request, flash
from datetime import datetime
import logging
from .forms import ProductoForm, RecetaForm
import base64

product = Blueprint('product', __name__)


@product.route("/producto")
@login_required
@roles_accepted('Administrador')
def producto():

    prod_form = ProductoForm(request.form)

    prod = Producto.query.all()

    return render_template("producto.html", form=prod_form, producto=prod)

@product.route("/agregarProducto", methods=["POST"])
@login_required
@roles_accepted("Administrador")
def agregarPro():

    prod_form = ProductoForm(request.form)
    if request.method == "POST":

        img = prod_form.img.data
        print(type(img))
        img_b64 = base64.b64encode(img.read()).decode("utf-8")

        producto = Producto(
            nombre=prod_form.productName.data,
            descripcion=prod_form.descripcion.data,
            imagen=img_b64,
            tipo_producto=prod_form.tipo_prod.data,
            precio_venta=prod_form.precioVenta.data,
            cantidad_disponible=0
        )

        db.session.add(producto)
        db.session.commit()
        
    prod = Producto.query.all()
    return render_template("producto.html", form=prod_form, producto=prod)