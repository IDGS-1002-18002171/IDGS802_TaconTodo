from flask import Blueprint,render_template,abort,session
from flask_security import login_required,current_user, login_user
from flask_security.decorators import roles_required,roles_accepted
from ..models import Producto,Venta,db,Pedidos,Pedidos_Productos
from flask import Flask, jsonify, request, redirect, url_for
import json,os,stripe,logging
from decimal import Decimal
from datetime import datetime
from plyer import notification
from flask_wtf.csrf import generate_csrf,validate_csrf
from datetime import datetime

venta=Blueprint('venta', __name__)

items = []

def calculate_order_amount():
    cuenta = Decimal('0.0')
    for item in items:
        precio = Decimal(item.precio_venta)*100
        cantidad = Decimal(item.cantidad_disponible)
        total = precio * cantidad
        cuenta += total
    return cuenta

def calculate_order_description():
    descripcion=''
    for item in items:
        if len(items)== 1:
            descripcion=item.cantidad_disponible+' '+item.nombre
        else :
            descripcion=descripcion+' '+item.cantidad_disponible+' '+item.nombre+',' 
    return descripcion

@venta.route('/create-payment-intent', methods=['POST'])
@login_required
#@roles_required('')
@roles_accepted('Administrador','Usuario')
def create_payment():
    try:
        data = json.loads(request.data)
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=int(calculate_order_amount()),  # Amount in cents, so 20 pesos is 2000 cents
            currency='mxn',  # Mexican pesos
            payment_method_types=['card'],  # Only allow card payments
            description=calculate_order_description(),
        )
        return jsonify({
            'clientSecret': intent['client_secret'],
            'description': intent['description'],# Agrega la descripción a la respuesta del JSON
        })
    except Exception as e:
        return jsonify(error=str(e)), 403

@venta.route("/cart")
@login_required
#@roles_required('')
@roles_accepted('Administrador','Usuario')
def cart():
    global items
    csrf_token = generate_csrf()
    cuenta = Decimal('0.0')
    for item in items:
        precio = Decimal(item.precio_venta)
        cantidad = Decimal(item.cantidad_disponible)
        total = precio * cantidad
        cuenta += total
    return render_template("carrito.html", items=items,total=cuenta,csrf_token=csrf_token)

@venta.route("/agregar_al_carrito", methods=["POST"])
@login_required
#@roles_required('')
@roles_accepted('Administrador','Usuario')
def agregar_al_carrito():
    global items
    try:
        validate_csrf(request.form.get('csrf_token'))
        producto = Producto.query.get(request.form["id"])
        producto.cantidad_disponible = request.form["cantidad"]
        producto.descripcion = ' '+request.form["options1"]+' y '+request.form["options"]
        items.append(producto)
    except ValidationError:
        # El token CSRF no coincide, rechazar la solicitud
        abort(403)
    return redirect(url_for("venta.getproduct"))

@venta.route("/eliminar_al_carrito", methods=["POST"])
@login_required
#@roles_required('')
@roles_accepted('Administrador','Usuario')
def eliminar_al_carrito():
    global items
    try:
        validate_csrf(request.form.get('csrf_token'))
        for item in items:
            if item.id_producto == int(request.form["id"]):
                items.remove(item)
                break
    except ValidationError:
        # El token CSRF no coincide, rechazar la solicitud
        abort(403)
    return redirect(url_for("venta.getproduct"))

@venta.route('/getproduct',methods=['GET'])
@login_required
#@roles_required('')
@roles_accepted('Administrador','Usuario')
def getproduct():
    productos=Producto.query.all()
    lista_productos=productos
    csrf_token = generate_csrf()
    #alumnos = Alumnos.query.filter(Alumnos.nombre.like('%CO%')).all()
    return render_template('venta1.html',productos=lista_productos,items=len(items),csrf_token=csrf_token)

@venta.route("/pasarela")
@login_required
#@roles_required('')
@roles_accepted('Administrador','Usuario')
def pasarela():
    return render_template("venta.html", items=items)

@venta.route("/thanks")
@login_required
#@roles_required('')
@roles_accepted('Administrador','Usuario')
def thanks():
    global items
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.debug(f'Compra en linea por .... id:{current_user.id} name:{current_user.name} correo:{current_user.email} fecha:{current_time}')
    logging.shutdown()
    verdura=0
    salsa=0
    for item in items:
        if 'Con verdura' in item.descripcion:
            verdura+=1
        if 'Con salsa' in item.descripcion:
            salsa+=1
    if verdura == range(len(items)):
        print('Toda la orden lleva verdura')
    if salsa == range(len(items)):
        print('Toda la orden lleva salsa')
    promedio_verdura=(verdura/len(items))
    promedio_salsa=(salsa/len(items))
    cuenta = Decimal('0.0')
    for item in items:
        idNew=item.id_producto
        producto = Producto.query.get(idNew) # Get the product with the given ID
        producto.cantidad_disponible = (int(producto.cantidad_disponible)-int(item.cantidad_disponible)) # Subtract 1 from the cantidad_disponible attribute
        precio = Decimal(item.precio_venta)
        cantidad = Decimal(item.cantidad_disponible)
        total = precio * cantidad
        cuenta += total
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    venta = Venta(id_usuario=current_user.id, precio_total=cuenta, fecha_hora_venta=current_time)
    db.session.add(venta)
    db.session.commit()
    if promedio_verdura!=0.0:
        if(cuenta>100):
            promedio_verdura=.003*promedio_verdura
        if(cuenta>500):
            promedio_verdura=.007*promedio_verdura
        if(cuenta<100):
            promedio_verdura=.001*promedio_verdura
    if promedio_salsa!=0.0:
        if(cuenta>100):
            promedio_salsa=.002*promedio_salsa
        if(cuenta>500):
            promedio_salsa=.006*promedio_salsa
        if(cuenta<100):
            promedio_salsa=.0001*promedio_salsa
    pedido = Pedidos(
        id_usuario=current_user.id,
        estado_pedido=1,
        fecha_hora_pedido=current_time
    )

    # Agregar el objeto a la sesión y hacer commit para que se realice la inserción en la tabla
    db.session.add(pedido)
    db.session.commit()

    id_pedido = pedido.id_pedido
    # Insertar los productos del pedido en la tabla Pedidos_Productos
    for producto in items:
        pedido_productos = Pedidos_Productos.insert().values(
            id_pedido=pedido.id_pedido,
            id_producto=producto.id_producto,
            cantidad=1
        )
        db.session.execute(pedido_productos)
    db.session.commit()
    # Configure the notification
    notification_title = "Nueva orden"
    notification_message = "Se ha realizado una nueva venta. Por favor, revise los detalles en la sección de pedidos de la aplicación."
    notification_timeout = 5  # Timeout in seconds
    if 'Administrador' in [role.name for role in current_user.roles]:
        notification.notify(title=notification_title, message=notification_message, timeout=notification_timeout)
    items.clear()
    db.session.commit()
    return render_template("thanks.html", items=items,verdura=promedio_verdura,salsa=promedio_salsa)