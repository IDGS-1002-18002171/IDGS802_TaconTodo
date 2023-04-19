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

@pedido.route('/getpedidos',methods=['GET'])
@login_required
#@roles_required('')
@roles_accepted('Administrador','Usuario','Vendedor')
def getpedidos():
    if 'Administrador' in current_user.roles:
        global lista_pedidos_estructurado
        pedidos = Pedidos.query.filter(Pedidos.estado_pedido <5).all()
        lista_pedidos_estructurado1=[]
        for pedido in pedidos:
            productos_pedido = []
            usuario=User.query.filter_by(id=pedido.id_usuario).first()
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
            detalles_pedido = db.session.query(Pedidos_Productos).filter_by(id_pedido=pedido.id_pedido).all()
            for detalle in detalles_pedido:
                producto = Producto.query.filter_by(id_producto=detalle.id_producto).first()
                producto.tipo_producto=detalle.cantidad
                productos_pedido.append(producto)
            pedido_estructurado = {
                'pedido': pedido,
                'productos': productos_pedido,
                'usuario': usuario,
                'cocinero':cocinero,
                'repartidor':repartidor
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
        #alumnos = Alumnos.query.filter(Alumnos.nombre.like('%CO%')).all()
        tittle='Historial de pedidos'
        return render_template('venta2.html',items=lista_pedidos_estructurado,csrf_token=csrf_token,tittle=tittle)

'''@pedido.route('/terminando',methods=['POST'])
@login_required
#@roles_required('')
@roles_accepted('Administrador','Vendedor')
def terminado():
    id_pedido=request.form["id"]
    pedido=Pedidos.query.filter_by(id_pedido=id_pedido).first()
    # Open database connection
    db1 = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="TaconTodo"
    )
    try:
        validate_csrf(request.form.get('csrf_token'))
        id_pedido=request.form["id"]
        pedido=Pedidos.query.filter_by(id_pedido=id_pedido).first()
        if pedido.estado_pedido==1:
            pedido.cocinero==current_user.id
            pedido.estado_pedido==2
            db1.session.commit()
            db1.close()
            success_message='Orden apartada con exito'
            flash(success_message,category='success')
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.debug(f'Orden Tomada por .... id:{current_user.id} name:{current_user.name} correo:{current_user.email} fecha:{current_time}')
            logging.shutdown()
        if pedido.estado_pedido==2:
            success_message='Orden Terminada con exito'
            flash(success_message,category='success')
            cursor = db.cursor()
            # execute the stored procedure
            cursor.callproc('Descuento_Materias_Primas', [id_pedido])
            # commit the transaction
            db1.commit()
            # close the database connection
            db1.close()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.debug(f'Orden finalizada por .... id:{current_user.id} name:{current_user.name} correo:{current_user.email} fecha:{current_time}')
            logging.shutdown()
    except :
        # El token CSRF no coincide, rechazar la solicitud
        abort(403)
    #alumnos = Alumnos.query.filter(Alumnos.nombre.like('%CO%')).all()
    return redirect(url_for('pedido.getpedidos'))'''

@pedido.route('/terminando',methods=['POST'])
@login_required
#@roles_required('')
@roles_accepted('Administrador','Vendedor')
def terminado():
    id_pedido=request.form["id"]
    pedido=Pedidos.query.filter_by(id_pedido=id_pedido).first()
    if pedido.estado_pedido==1:
        pedido.cocinero=current_user.id
        pedido.estado_pedido=2
        success_message='Orden apartada con exito'
        flash(success_message,category='success')
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.debug(f'Orden Tomada por .... id:{current_user.id} name:{current_user.name} correo:{current_user.email} fecha:{current_time}')
        logging.shutdown()
    elif  pedido.estado_pedido==2:
        pedido.estado_pedido=3
        Descontar_materia_prima(id_pedido)
        success_message='Orden Terminada con exito'
        flash(success_message,category='success')
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.debug(f'Orden finalizada por .... id:{current_user.id} name:{current_user.name} correo:{current_user.email} fecha:{current_time}')
        logging.shutdown()
    db.session.commit()
    #alumnos = Alumnos.query.filter(Alumnos.nombre.like('%CO%')).all()
    return redirect(url_for('pedido.getpedidos'))

@pedido.route('/viaje',methods=['POST'])
@login_required
#@roles_required('')
@roles_accepted('Administrador','Vendedor')
def viaje():
    try:
        validate_csrf(request.form.get('csrf_token'))
        id_pedido=request.form["id"]
        pedido=Pedidos.query.filter_by(id_pedido=id_pedido).first()
        if pedido.estado_pedido==3:
            pedido.repartidor=current_user.id
            pedido.estado_pedido=4
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.debug(f'Viaje de la orden tomada por .... id:{current_user.id} name:{current_user.name} correo:{current_user.email} fecha:{current_time}')
            logging.shutdown()
            success_message='Viaje registrado con exio'
            flash(success_message,category='success')
        elif pedido.estado_pedido==4:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pedido.fecha_hora_entrega=current_time
            pedido.estado_pedido=5
            logging.debug(f'Orden entregada por .... id:{current_user.id} name:{current_user.name} correo:{current_user.email} fecha:{current_time}')
            logging.shutdown()
            success_message='Orden entregada con exito'
            flash(success_message,category='success')
        db.session.commit()
    except :
        # El token CSRF no coincide, rechazar la solicitud
        abort(403)
    #alumnos = Alumnos.query.filter(Alumnos.nombre.like('%CO%')).all()
    return redirect(url_for('pedido.getpedidos'))