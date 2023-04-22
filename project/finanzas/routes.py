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
from sqlalchemy import create_engine,func
import pymysql

finanza=Blueprint('finanza', __name__)

@finanza.route('/finanzas')
@login_required
@roles_accepted('Administrador')
def finanzas():
    # Obtener la información de ventas necesaria para la gráfica
    ventas_por_mes = db.session.query(func.year(Venta.fecha_hora_venta).label('Anio'), func.month(Venta.fecha_hora_venta).label('Mes'), func.sum(Venta.precio_total).label('Monto')).group_by('Anio', 'Mes').all()
    pedidos_por_mes = db.session.query(func.year(Pedidos.fecha_hora_pedido).label('Anio'), func.month(Pedidos.fecha_hora_pedido).label('Mes'), func.count(Pedidos.id_pedido).label('Cantidad')).group_by('Anio', 'Mes').all()
    # Pasar la información a la plantilla de Flask
    return render_template('finanza.html', ventas_por_mes=ventas_por_mes,pedidos_por_mes=pedidos_por_mes)

@finanza.route('/pedidos')
@login_required
def pedidos():
    # Obtener la cantidad de pedidos por mes
    
    # Pasar la información a la plantilla de Flask
    return render_template('finanza.html', )
'''@classmethod
def generar_reporte_ventas(cls):
    reporte = []
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SET sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';")
            cursor.execute('SELECT * FROM reporte_mensual;')
            reporte = cursor.fetchall()
        connection.close()
    except Exception as e:
        print('ERROR WE: ', e)
    # Transformacion de los datos a un DataFrame
    df = pd.DataFrame(reporte, columns=['Anio', 'Mes', 'Ventas', 'Monto', 'Crecimiento', 'Porcentaje Crecimiento'])
    # Agrupar las ventas por año y mes
    ventas_por_mes = df.groupby(['Anio','Mes'])['Monto'].sum().reset_index()
    #Crear una nueva columna que combine el año y el mes
    ventas_por_mes['Anio_Mes'] = ventas_por_mes['Anio'].astype(str) + '-' + ventas_por_mes['Mes'].astype(str)
    # Crear la gráfica de barras
    plt.bar(ventas_por_mes['Anio_Mes'], ventas_por_mes['Monto'])
    # Crear la línea de crecimiento
    plt.plot(ventas_por_mes['Anio_Mes'], ventas_por_mes['Monto'], 'o-', color='red', linewidth=2)
    # Configurar las etiquetas de los ejes
    plt.xlabel('Año-Mes')
    plt.ylabel('Ventas')
    # Configurar el título de la gráfica
    plt.title('Ventas por mes')
    # Rotar las etiquetas del eje 'x'
    plt.xticks(rotation=45)
    # Guardar la imagen en formato PNG y sobrescribir la imagen existente
    ruta_imagen = 'app/static/img/ventas.png'    
    if os.path.exists(ruta_imagen):
        os.remove(ruta_imagen)
        plt.savefig(ruta_imagen, bbox_inches='tight')
    else:
        plt.savefig(ruta_imagen, bbox_inches='tight')
    # Cerrar la gráfica
    plt.close()
    url_imagen_ventas = '../../../static/img/ventas.png'
    return url_imagen_ventas'''