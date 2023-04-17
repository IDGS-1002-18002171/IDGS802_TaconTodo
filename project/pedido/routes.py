from flask import Blueprint,render_template,abort,session,flash
from flask_security import login_required,current_user,login_user
from flask_security.decorators import roles_required,roles_accepted
from ..models import Producto,Venta,db,Pedidos,Pedidos_Productos,User
from flask import Flask,jsonify,request,redirect,url_for
import json,os,stripe,logging
from decimal import Decimal
from datetime import datetime
from plyer import notification
from flask_wtf.csrf import generate_csrf,validate_csrf
from datetime import datetime
from sqlalchemy import create_engine
import pymysql

pedido=Blueprint('pedido', __name__)

lista_pedidos_estructurado=[]



@pedido.route('/getpedidos',methods=['GET'])
@login_required
#@roles_required('')
@roles_accepted('Administrador','Usuario','Vendedor')
def getpedidos():
    if 'Administrador' in current_user.roles:
        global lista_pedidos_estructurado
        pedidos = Pedidos.query.filter(Pedidos.estado_pedido == 1).all()
        lista_pedidos_estructurado1=[]
        for pedido in pedidos:
            productos_pedido = []
            usuario=User.query.filter_by(id=pedido.id_usuario).first()
            detalles_pedido = db.session.query(Pedidos_Productos).filter_by(id_pedido=pedido.id_pedido).all()
            for detalle in detalles_pedido:
                producto = Producto.query.filter_by(id_producto=detalle.id_producto).first()
                producto.tipo_producto=detalle.cantidad
                productos_pedido.append(producto)
            pedido_estructurado = {
                'pedido': pedido,
                'productos': productos_pedido,
                'usuario': usuario
            }
            lista_pedidos_estructurado1.append(pedido_estructurado)
        lista_pedidos_estructurado = []
        lista_pedidos_estructurado=lista_pedidos_estructurado1
        csrf_token = generate_csrf()
        #alumnos = Alumnos.query.filter(Alumnos.nombre.like('%CO%')).all()
        return render_template('pedido.html',items=lista_pedidos_estructurado,csrf_token=csrf_token)
    if 'Usuario' in current_user.roles:
        pedidos = Pedidos.query.filter(Pedidos.id_usuario == current_user.id).all()
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
        #alumnos = Alumnos.query.filter(Alumnos.nombre.like('%CO%')).all()
        tittle='Historial de pedidos'
        return render_template('venta2.html',items=lista_pedidos_estructurado,csrf_token=csrf_token,tittle=tittle)

@pedido.route('/terminando',methods=['POST'])
@login_required
#@roles_required('')
@roles_accepted('Administrador','Vendedor')
def terminado():
    try:
        validate_csrf(request.form.get('csrf_token'))
        # Open database connection
        db = pymysql.connect(
            host="localhost",
            user="root",
            password="root",
            database="TaconTodo"
        )
        success_message='Pedido Finalizado con exito'
        flash(success_message,category='success')
        cursor = db.cursor()

        # execute the stored procedure
        cursor.callproc('Descuento_Materias_Primas', [request.form["id"]])
        # commit the transaction
        db.commit()

        # close the database connection
        db.close()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.debug(f'Orden finalizada por .... id:{current_user.id} name:{current_user.name} correo:{current_user.email} fecha:{current_time}')
        logging.shutdown()
        
    except :
        # El token CSRF no coincide, rechazar la solicitud
        abort(403)
    #alumnos = Alumnos.query.filter(Alumnos.nombre.like('%CO%')).all()
    return redirect(url_for('venta.getproduct'))