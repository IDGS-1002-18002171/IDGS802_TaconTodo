from flask import Blueprint,render_template, redirect, url_for
from flask_security import login_required,current_user
from flask_security.decorators import roles_required,roles_accepted
from ..models import db,Inventario, Producto, MateriaPrima, Proveedor, Receta
from flask import jsonify, request, flash
from datetime import datetime
import logging
from .forms import ProductoForm, RecetaForm
import base64
from flask_wtf.csrf import generate_csrf,validate_csrf
import logging
import datetime

product = Blueprint('product', __name__)


@product.route("/producto")
@login_required
@roles_accepted('Administrador','Empleado')
def producto():
    prod_form = ProductoForm(request.form)
    rect_form = RecetaForm(request.form)
    rect_form.idProducto.choices = [(prod.id_producto, prod.nombre)for prod in Producto.query.filter_by(estatus=1).all()]
    rect_form.idMateriaPri.choices = [(mat.id_materia_prima, mat.nombre) for mat in MateriaPrima.query.all()]
    prod = Producto.query.filter_by(estatus=1).all()
    recetas=Receta.query.all()
    lista_recetas_estructurado=[]
    for receta in recetas:
        producto=Producto.query.filter_by(id_producto=receta.id_producto).first()
        materia=MateriaPrima.query.filter_by(id_materia_prima=receta.id_materia_prima).first()
        receta_estructurada = {
                'receta': receta,
                'producto': producto,
                'materia': materia
            }
        lista_recetas_estructurado.append(receta_estructurada)
    csrf_token = generate_csrf()
    return render_template("producto.html", form=prod_form,formR=rect_form, producto=prod,csrf_token=csrf_token,recetas=lista_recetas_estructurado)

@product.route("/agregarProducto", methods=["POST"])
@login_required
@roles_accepted("Administrador")
def agregarPro():
    try:
        validate_csrf(request.form.get('csrf_token'))
    except :
        # El token CSRF no coincide, rechazar la solicitud
        abort(403)
    prod_form = ProductoForm(request.form)
    rect_form = RecetaForm(request.form)
    csrf_token = generate_csrf()

    date = datetime.datetime.now()
    logging.basicConfig(filename='trazabilidad.log', level=logging.INFO)
    logging.info("se cargaron las listas de usuarios en la fecha: " + date.strftime("%d/%m/%Y") + " " + date.strftime("%H:%M:%S") )

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
    
    return render_template("producto.html", form=prod_form,formR=rect_form,csrf_token=csrf_token)

@product.route("/editarProducto", methods=["GET","POST"])
@login_required
@roles_accepted("Administrador")
def editarProducto():
    pr = ProductoForm(request.form)

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

@product.route("/eliminar_producto/<id>")
@login_required
@roles_accepted('Administrador')
def eliminar_producto(id):
 
    producto = Producto.query.filter_by(id_producto=id).first()

    if producto:

        producto.nombre = producto.nombre
        producto.descripcion = producto.descripcion
        producto.imagen = producto.imagen
        producto.tipo_producto = producto.tipo_producto
        producto.precio_venta = producto.precio_venta
        producto.estatus = 0

        db.session.add(producto)
        db.session.commit()

        flash("Se elimino correctamente","success")
        return redirect(url_for("product.producto"))
    else: 
        flash("No existe ese producto","danger")
        return redirect(url_for("product.producto"))
    

@product.route("/buscarProducto", methods=["GET","POST"])
@login_required
@roles_accepted('Administrador','Empleado')
def buscarProducto():
    search = request.form.get("searchProducto")
    prod_form = ProductoForm(request.form)
    rect_form = RecetaForm(request.form)
    csrf_token = generate_csrf()

    if search:
        prod = Producto.query.filter_by( estatus=1 and
            (Producto.id_producto.ilike(f"%{search}%")) |
            (Producto.nombre.ilike(f"%{search}%")) |
            (Producto.descripcion.ilike(f"%{search}%")) |
            (Producto.tipo_producto.ilike(f"%{search}%")) |
            (Producto.precio_venta.ilike(f"%{search}%")) 
            ).all()
    else:
       flash("No existe", "error")

    return render_template("producto.html", form=prod_form,formR=rect_form, producto=prod)

@product.route("/crearReceta", methods=["POST"])
@login_required
@roles_accepted("Administrador")
def crearReceta():
    id_materia_prima = request.form['idMateriaPri']
    id_producto = request.form['idProducto']
    cantidad_requerida = request.form['cantidadReq']
    receta = Receta(id_materia_prima=id_materia_prima, id_producto=id_producto, cantidad_requerida=cantidad_requerida)
    db.session.add(receta)
    db.session.commit()
    return redirect(url_for('product.producto'))


@product.route('/eliminarReceta', methods=['POST'])
@login_required
@roles_accepted('Administrador')
def eliminarReceta():
    receta_id = request.form.get('id_receta')
    receta = Receta.query.filter(Receta.id_receta==receta_id).first()
    print(receta)
    db.session.delete(receta)
    db.session.commit()
    return redirect(url_for('product.producto'))


@product.route("/buscarReceta", methods=["GET","POST"])
@login_required
@roles_accepted('Administrador','Empleado')
def buscarReceta():
    search = request.form.get("searchReceta")
    prod_form = ProductoForm(request.form)
    rect_form = RecetaForm(request.form)
    rect_form.idProducto.choices = [(prod.id_producto, prod.nombre)for prod in Producto.query.filter_by(estatus=1).all()]
    rect_form.idMateriaPri.choices = [(mat.id_materia_prima, mat.nombre) for mat in MateriaPrima.query.all()]
    csrf_token = generate_csrf()

    if search:
        prod = Producto.query.filter_by( estatus=1 and
            (Producto.nombre.ilike(f"%{search}%"))
            ).all()
        recetas=Receta.query.all()
        lista_recetas_estructurado=[]
        for producto in prod:
            try:
                recetas=Receta.query.filter_by(id_producto=producto.id_producto).all()
                for receta in recetas:
                    producto=Producto.query.filter_by(id_producto=receta.id_producto).first()
                    materia=MateriaPrima.query.filter_by(id_materia_prima=receta.id_materia_prima).first()
                    receta_estructurada = {
                            'receta': receta,
                            'producto': producto,
                            'materia': materia
                        }
                    lista_recetas_estructurado.append(receta_estructurada)
            except:
                pass
        csrf_token = generate_csrf()
        return render_template("producto.html", form=prod_form,formR=rect_form, producto=prod,csrf_token=csrf_token,recetas=lista_recetas_estructurado)
    else:
       flash("No existe", "error")
       prod = Producto.query.filter_by(estatus=1).all()
       recetas=Receta.query.all()
       lista_recetas_estructurado=[]
       for receta in recetas:
            producto=Producto.query.filter_by(id_producto=receta.id_producto).first()
            materia=MateriaPrima.query.filter_by(id_materia_prima=receta.id_materia_prima).first()
            receta_estructurada = {
                    'receta': receta,
                    'producto': producto,
                    'materia': materia
                }
            lista_recetas_estructurado.append(receta_estructurada)
    return render_template("producto.html", form=prod_form,formR=rect_form, producto=prod,csrf_token=csrf_token,recetas=lista_recetas_estructurado)
