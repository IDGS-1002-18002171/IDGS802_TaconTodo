from flask import Blueprint,render_template, redirect, url_for
from flask_security import login_required,current_user
from flask_security.decorators import roles_required,roles_accepted
from ..models import db,Inventario, Producto, MateriaPrima, Proveedor
from flask import jsonify, request, flash
from datetime import datetime
import logging
from .forms import ProductoForm, RecetaForm
import base64
from flask_wtf.csrf import generate_csrf,validate_csrf

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
    csrf_token = generate_csrf()

    if request.method == "POST":
        
        img = request.files["imagenes"]
        img_b64 = base64.b64encode(img.read()).decode("utf-8")

        producto = Producto(
            nombre=prod_form.productName.data,
            descripcion=prod_form.descripcion.data,
            imagen=img_b64,
            tipo_producto=prod_form.tipo_prod.data,
            precio_venta=prod_form.precioVenta.data,
            cantidad_disponible=0,
            estatus = 1
        )

        db.session.add(producto)
        db.session.commit()

        flash("Se agrego un producto exitosamente", "success")

        return redirect(url_for("product.producto"))
    
    return render_template("producto.html", form=prod_form,csrf_token=csrf_token)

@product.route("/editarProducto", methods=["GET","POST"])
@login_required
@roles_accepted("Administrador")
def editarProducto():
    pr = ProductoForm(request.form);

    if request.method == "GET":
        idProducto = request.args.get("id")

        p = Producto.query.filter_by(id_producto=idProducto).first()

        pr.idProducto.data = idProducto
        pr.productName.data = p.nombre 
        pr.descripcion.data = p.descripcion
        imagen = p.imagen
        pr.tipo_prod.data = p.tipo_producto
        pr.precioVenta.data = p.precio_venta
        pr.estatus.data = p.estatus
    
    if request.method == "POST" :

        id = pr.idProducto.data
        pu = Producto.query.filter_by(id_producto=id).first()
        imagen = request.form.get("imgBase64");
        pu.nombre = pr.productName.data
        pu.descripcion = pr.descripcion.data
        
        img = request.files["img_edit"]
        img_b64 = base64.b64encode(img.read()).decode("utf-8")

        if img_b64:
            pu.imagen = img_b64
        else:
            pu.imagen = request.form.get("imgBase64")
        
        pu.tipo_producto = pr.tipo_prod.data
        pu.precio_venta = pr.precioVenta.data
        pu.estatus = pr.estatus.data

        db.session.add(pu)
        db.session.commit()

        flash("Se actualizo correctamente el producto","success")
        return redirect(url_for("product.producto"))

    return render_template("editar_producto.html",form=pr,imagen=imagen)
