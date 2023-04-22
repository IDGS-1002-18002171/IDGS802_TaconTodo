from flask import Blueprint,render_template,abort,session, flash
from flask_security import login_required,current_user, login_user
from flask_security.decorators import roles_required,roles_accepted
from ..models import Producto,Venta,db,Pedidos,Pedidos_Productos,User
from flask import Flask, jsonify, request, redirect, url_for,make_response
import json,os,stripe,logging
from decimal import Decimal
from datetime import datetime
from plyer import notification
from flask_wtf.csrf import generate_csrf,validate_csrf
from datetime import datetime
import requests
from sqlalchemy import create_engine
import pymysql

venta=Blueprint('venta', __name__)

items = []
direccion_global = ''

#venta.config(RAPPI_CLIENT_ID = "TU_ID_DE_CLIENTE_RAPPI")
#venta.config(RAPPI_CLIENT_SECRET = "TU_CLAVE_SECRETA_RAPPI")

def make_rappi_request(url, params={}):
    headers = {
        "Authorization": f"Bearer {RAPPI_CLIENT_ID}:{RAPPI_CLIENT_SECRET}"
    }
    response = requests.post(url, headers=headers, json=params)
    return response.json()

def insertar_pedido():
    global items
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cuenta = Decimal('20.0')
    for item in items:
        idNew=item.id_producto
        producto = Producto.query.get(idNew) # Get the product with the given ID
        #producto.cantidad_disponible = (int(producto.cantidad_disponible)-int(item.cantidad_disponible)) # Subtract 1 from the cantidad_disponible attribute
        precio = Decimal(item.precio_venta)
        cantidad = Decimal(item.cantidad_disponible)
        total = precio * cantidad
        cuenta += total
    venta =Venta(
        id_usuario=current_user.id,
        precio_total=cuenta,
        fecha_hora_venta=current_time
    )
    # Agregar el objeto a la sesión y hacer commit para que se realice la inserción en la tabla
    db.session.add(venta)
    pedido = Pedidos(
        id_usuario=current_user.id,
        estado_pedido=1,
        fecha_hora_pedido=current_time,
        domicilio=direccion_global
    )
    # Agregar el objeto a la sesión y hacer commit para que se realice la inserción en la tabla
    db.session.add(pedido)
    db.session.commit()

    id_pedido = pedido.id_pedido
    # Insertar los productos del pedido en la tabla Pedidos_Productos
    for producto in items:
        pedido_productos = Pedidos_Productos.insert().values(
        id_pedido=id_pedido,
        id_producto=producto.id_producto,
        cantidad=producto.cantidad_disponible
        )
        db.session.execute(pedido_productos)
    db.session.commit()

def Descontar_materia_prima(id_pedido):
    # Open database connection
    db1 = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="TaconTodo"
    )
    cursor = db1.cursor()
    # execute the stored procedure
    cursor.callproc('Descuento_Materias_Primas', [id_pedido])
    # commit the transaction
    db1.commit()
    # close the database connection
    db1.close()

def calculate_order_amount():
    cuenta = Decimal('2000.0')
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

@venta.route("/cart")
@login_required
#@roles_required('')
@roles_accepted('Usuario','Empleado')
def cart():
    global items
    csrf_token = generate_csrf()
    if 'Usuario' in current_user.roles:
        cuenta = Decimal('20.0')
        for item in items:
            precio = Decimal(item.precio_venta)
            cantidad = Decimal(item.cantidad_disponible)
            total = precio * cantidad
            cuenta += total
    else :
        cuenta = Decimal('00.0')
        for item in items:
            precio = Decimal(item.precio_venta)
            cantidad = Decimal(item.cantidad_disponible)
            total = precio * cantidad
            cuenta += total
    return render_template("carrito.html", items=items,total=cuenta,csrf_token=csrf_token)

@venta.route("/agregar_al_carrito", methods=["POST"])
def agregar_al_carrito():
    global items
    if 'Usuario' in current_user.roles or 'Empleado' in current_user.roles:
        try:
            validate_csrf(request.form.get('csrf_token'))
            producto = Producto.query.get(request.form["id"])
            producto.cantidad_disponible = request.form["cantidad"]
            producto.descripcion = ' '+request.form["options1"]+' y '+request.form["salsa"]
            items.append(producto)
            return redirect(url_for("venta.getproduct"))
        except :
            # El token CSRF no coincide, rechazar la solicitud
            abort(403)
    else :
        flash('Inicia sesion como Cliente antes de realizar compras')
        return redirect(url_for("auth.login"))
    

@venta.route("/eliminar_al_carrito", methods=["POST"])
@login_required
#@roles_required('')
@roles_accepted('Usuario','Empleado')
def eliminar_al_carrito():
    global items
    try:
        validate_csrf(request.form.get('csrf_token'))
        for item in items:
            if item.id_producto == int(request.form["id"]):
                items.remove(item)
                break
    except :
        # El token CSRF no coincide, rechazar la solicitud
        abort(403)
    return redirect(url_for("venta.getproduct"))

@venta.route('/getproduct',methods=['GET'])
def getproduct():
    if 'Administrador' in current_user.roles:
        pedidos = Pedidos.query.filter(Pedidos.estado_pedido == 5).all()
        lista_pedidos_estructurado1=[]
        for pedido in pedidos:
            total = Decimal('20.0')
            productos_pedido = []
            usuario=User.query.filter_by(id=pedido.id_usuario).first()
            detalles_pedido = db.session.query(Pedidos_Productos).filter_by(id_pedido=pedido.id_pedido).all()
            for detalle in detalles_pedido:
                producto = Producto.query.filter_by(id_producto=detalle.id_producto).first()
                producto.tipo_producto=detalle.cantidad
                total+=producto.precio_venta*detalle.cantidad
                productos_pedido.append(producto)
            cocinero={'name':'None'}
            try :
                cocinero=User.query.filter_by(id=pedido.cocinero).first()
            except:
                pass
            repartidor={'name':'None'}
            try :
                repartidor=User.query.filter_by(id=pedido.repartidor).first()
            except:
                pass
            pedido_estructurado = {
                'pedido': pedido,
                'productos': productos_pedido,
                'total': total,
                'usuario': usuario,
                'cocinero':cocinero,
                'repartidor':repartidor
            }
            lista_pedidos_estructurado1.append(pedido_estructurado)
        lista_pedidos_estructurado = []
        lista_pedidos_estructurado=lista_pedidos_estructurado1
        csrf_token = generate_csrf()
        tittle='Ventas Concluidas'
        #alumnos = Alumnos.query.filter(Alumnos.nombre.like('%CO%')).all()
        return render_template('venta2.html',items=lista_pedidos_estructurado,csrf_token=csrf_token,tittle=tittle)
    else :
        productos=Producto.query.all()
        lista_productos=productos
        csrf_token = generate_csrf()
        #alumnos = Alumnos.query.filter(Alumnos.nombre.like('%CO%')).all()
        return render_template('venta1.html',productos=lista_productos,items=len(items),csrf_token=csrf_token)
    

@venta.route("/pasarela")
@login_required
#@roles_required('')
@roles_accepted('Usuario','Empleado')
def pasarela():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if 'Empleado' in current_user.roles:
        cuenta = Decimal('0.0')
        for item in items:
            idNew=item.id_producto
            producto = Producto.query.get(idNew) # Get the product with the given ID
            #producto.cantidad_disponible = (int(producto.cantidad_disponible)-int(item.cantidad_disponible)) # Subtract 1 from the cantidad_disponible attribute
            precio = Decimal(item.precio_venta)
            cantidad = Decimal(item.cantidad_disponible)
            total = precio * cantidad
            cuenta += total
        venta =Venta(
            id_usuario=current_user.id,
            precio_total=cuenta,
            fecha_hora_venta=current_time
        )

        # Agregar el objeto a la sesión y hacer commit para que se realice la inserción en la tabla
        db.session.add(venta)
        pedido = Pedidos(
            id_usuario=current_user.id,
            estado_pedido=5,
            fecha_hora_pedido=current_time,
            domicilio='Sucursal Zona Centro'
        )
        # Agregar el objeto a la sesión y hacer commit para que se realice la inserción en la tabla
        db.session.add(pedido)
        db.session.commit()

        id_pedido = pedido.id_pedido
        # Insertar los productos del pedido en la tabla Pedidos_Productos
        for producto in items:
            pedido_productos = Pedidos_Productos.insert().values(
                id_pedido=id_pedido,
                id_producto=producto.id_producto,
                cantidad=producto.cantidad_disponible
            )
            db.session.execute(pedido_productos)
        db.session.commit()
        items.clear()
        success_message='Gracias por su compra'
        flash(success_message,category='success')
        Descontar_materia_prima(id_pedido)
        return redirect(url_for("venta.getproduct"))
    else :
        return render_template("venta.html", items=items)

@venta.route("/thanks")
@login_required
#@roles_required('')
@roles_accepted('Usuario')
def thanks():
    global items
    global direccion_global
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.debug(f'Compra en linea por .... id:{current_user.id} name:{current_user.name} correo:{current_user.email} fecha:{current_time}')
    logging.shutdown()
    verdura=0.0
    salsa_verde=0.0
    salsa_roja=0.0
    promedio_verdura=0.0
    promedio_salsa_verde=0.0
    promedio_salsa_roja=0.0
    for item in items:
        if 'Con verdura' in item.descripcion:
            verdura+=1.0*float(item.cantidad_disponible)
        if 'Salsa verde' in item.descripcion:
            salsa_verde+=1.0*float(item.cantidad_disponible)
        if 'Salsa roja' in item.descripcion:
            salsa_roja+=1.0*float(item.cantidad_disponible)
        if 'Ambas salsas' in item.descripcion:
            salsa_roja+=.5*float(item.cantidad_disponible)
            salsa_verde+=.5*float(item.cantidad_disponible)

    if verdura>0.0:
        promedio_verdura=.001*verdura

    if salsa_verde>0.0:
        promedio_salsa_verde=.0001*salsa_verde

    if salsa_roja>0.0:
        promedio_salsa_roja=.0001*salsa_roja
    
    insertar_pedido()
    items.clear()
    success_message='Gracias por su compra'
    flash(success_message,category='success')
    # Configure the notification
    notification_title = "Nueva orden"
    notification_message = "Se ha realizado una nueva venta. Por favor, revise los detalles en la sección de pedidos de la aplicación."
    notification_timeout = 5  # Timeout in seconds
    if 'Administrador' in [role.name for role in current_user.roles] or 'Empleado' in [role.name for role in current_user.roles] or 'Repartidor' in [role.name for role in current_user.roles]:
        notification.notify(title=notification_title, message=notification_message, timeout=notification_timeout)
    return redirect(url_for('pedido.getpedidos'))

@venta.route('/update-direccion', methods=['POST'])
@login_required
#@roles_required('')
@roles_accepted('Usuario')
def update_direccion():
    global direccion_global
    colonias_validas = ['Brisas del Lago', 'San Pedro', 'Villas de San Juan']
    direccion_usuario = request.json['direccion']
    if any(colonia in direccion_usuario for colonia in colonias_validas):
        direccion_global=direccion_usuario
        # la dirección del usuario contiene una colonia válida
        return jsonify({'success': True})
    else:
        # la dirección del usuario no contiene una colonia válida
        return jsonify({'success': False})

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
