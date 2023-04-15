from flask import Blueprint,render_template,abort,session
from flask_security import login_required,current_user, login_user
from flask_security.decorators import roles_required,roles_accepted
from ..models import Producto,Venta,db,Pedidos,Pedidos_Productos,User
from flask import Flask, jsonify, request, redirect, url_for
import json,os,stripe,logging
from decimal import Decimal
from datetime import datetime
from plyer import notification
from flask_wtf.csrf import generate_csrf,validate_csrf
from datetime import datetime
import requests

venta=Blueprint('venta', __name__)

items = []

#venta.config(RAPPI_CLIENT_ID = "TU_ID_DE_CLIENTE_RAPPI")
#venta.config(RAPPI_CLIENT_SECRET = "TU_CLAVE_SECRETA_RAPPI")

def make_rappi_request(url, params={}):
    headers = {
        "Authorization": f"Bearer {RAPPI_CLIENT_ID}:{RAPPI_CLIENT_SECRET}"
    }
    response = requests.post(url, headers=headers, json=params)
    return response.json()

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
@roles_accepted('Usuario')
def create_payment():
    try:
        global items
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
        order_info = {
            "customer_name": current_user.name,
            "product_name": calculate_order_description(),
            "store_id": 99,
            "user_id" : current_user.id,
            "total_price": int(calculate_order_amount()),
            "payment_method": ['card'],
            "items": items
        }
        #create_rappi_order(order_info)
    except Exception as e:
        return jsonify(error=str(e)), 403

@venta.route("/cart")
@login_required
#@roles_required('')
@roles_accepted('Usuario')
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
@roles_accepted('Usuario')
def agregar_al_carrito():
    global items
    try:
        validate_csrf(request.form.get('csrf_token'))
        producto = Producto.query.get(request.form["id"])
        producto.cantidad_disponible = request.form["cantidad"]
        producto.descripcion = ' '+request.form["options1"]+' y '+request.form["salsa"]
        items.append(producto)
    except ValidationError:
        # El token CSRF no coincide, rechazar la solicitud
        abort(403)
    return redirect(url_for("venta.getproduct"))

@venta.route("/eliminar_al_carrito", methods=["POST"])
@login_required
#@roles_required('')
@roles_accepted('Usuario')
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
    if 'Usuario' in current_user.roles:
        productos=Producto.query.all()
        lista_productos=productos
        csrf_token = generate_csrf()
        #alumnos = Alumnos.query.filter(Alumnos.nombre.like('%CO%')).all()
        return render_template('venta1.html',productos=lista_productos,items=len(items),csrf_token=csrf_token)
    if 'Administrador' in current_user.roles:
        pedidos = Pedidos.query.filter(Pedidos.estado_pedido == 2).all()
        lista_pedidos_estructurado1=[]
        total = Decimal('0.0')
        for pedido in pedidos:
            productos_pedido = []
            usuario=User.query.filter_by(id=pedido.id_usuario).first()
            detalles_pedido = db.session.query(Pedidos_Productos).filter_by(id_pedido=pedido.id_pedido).all()
            for detalle in detalles_pedido:
                producto = Producto.query.filter_by(id_producto=detalle.id_producto).first()
                producto.tipo_producto=detalle.cantidad
                total=producto.precio_venta+total
                productos_pedido.append(producto)
            pedido_estructurado = {
                'pedido': pedido,
                'productos': productos_pedido,
                'total': total,
                'usuario': usuario
            }
            lista_pedidos_estructurado1.append(pedido_estructurado)
        lista_pedidos_estructurado = []
        lista_pedidos_estructurado=lista_pedidos_estructurado1
        csrf_token = generate_csrf()
        tittle='Ventas Concluidas'
        #alumnos = Alumnos.query.filter(Alumnos.nombre.like('%CO%')).all()
        return render_template('venta2.html',items=lista_pedidos_estructurado,csrf_token=csrf_token,tittle=tittle)

@venta.route("/pasarela")
@login_required
#@roles_required('')
@roles_accepted('Usuario')
def pasarela():
    return render_template("venta.html", items=items)

@venta.route("/thanks")
@login_required
#@roles_required('')
@roles_accepted('Usuario')
def thanks():
    global items
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.debug(f'Compra en linea por .... id:{current_user.id} name:{current_user.name} correo:{current_user.email} fecha:{current_time}')
    logging.shutdown()
    verdura=0
    salsa_verde=0
    salsa_roja=0
    for item in items:
        if 'Con verdura' in item.descripcion:
            verdura+=1
        if 'Salsa verde' in item.descripcion:
            salsa_verde+=1
        if 'Salsa roja' in item.descripcion:
            salsa_roja+=1
        if 'Ambas salsas' in item.descripcion:
            salsa_roja+=.5
            salsa_verde+=.5
    promedio_verdura=(verdura/len(items))
    promedio_salsa_verde=(salsa_verde/len(items))
    promedio_salsa_roja=(salsa_roja/len(items))
    cuenta = Decimal('0.0')
    for item in items:
        idNew=item.id_producto
        producto = Producto.query.get(idNew) # Get the product with the given ID
        #producto.cantidad_disponible = (int(producto.cantidad_disponible)-int(item.cantidad_disponible)) # Subtract 1 from the cantidad_disponible attribute
        precio = Decimal(item.precio_venta)
        cantidad = Decimal(item.cantidad_disponible)
        total = precio * cantidad
        cuenta += total
    if promedio_verdura!=0.0:
        if(cuenta>100):
            promedio_verdura=.003*promedio_verdura
        if(cuenta>500):
            promedio_verdura=.007*promedio_verdura
        if(cuenta<100):
            promedio_verdura=.001*promedio_verdura
    if promedio_salsa_verde!=0.0:
        if(cuenta>100):
            promedio_salsa_verde=.002*promedio_salsa_verde
        if(cuenta>500):
            promedio_salsa_verde=.006*promedio_salsa_verde
        if(cuenta<100):
            promedio_salsa_verde=.0001*promedio_salsa_verde
    if promedio_salsa_roja!=0.0:
        if(cuenta>100):
            promedio_salsa_roja=.002*promedio_salsa_roja
        if(cuenta>500):
            promedio_salsa_roja=.006*promedio_salsa_roja
        if(cuenta<100):
            promedio_salsa_roja=.0001*promedio_salsa_roja
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
    success_message='Gracias por su compra'
    flash(success_message,category='success')
    return render_template("thanks.html", items=items,verdura=promedio_verdura,salsa_verde=promedio_salsa_verde,salsa_roja=promedio_salsa_roja)

def create_rappi_order(order_info):
    url = "https://services.rappi.com/api/orders/v2/create"
    order = {
        "store": {
            "id": order_info["store_id"]
        },
        "user": {
            "id": order_info["user_id"]
        },
        "items": order_info["items"],
        "payment_method_id": order_info["payment_method_id"],
        "scheduled_time": order_info["scheduled_time"],
        "delivery": {
            "address": {
                "description": order_info["delivery_address"],
                "latitude": order_info["delivery_latitude"],
                "longitude": order_info["delivery_longitude"]
            }
        },
        "total_amount": order_info["total_amount"],
        "currency": "MXN"
    }
    response = make_rappi_request(url, order)
    return response
