#Importamos el objeto de la base de datos __init__.py
from . import db
from flask_sqlalchemy import SQLAlchemy
#Importamos la clase UserMixin de  flask_login
from flask_security import UserMixin,RoleMixin

#Definiendo la tabla relacional entre usuarios roles
user_roles=db.Table('user_roles',
    db.Column('userId',db.Integer,db.ForeignKey('user.id')),
    db.Column('roleId',db.Integer,db.ForeignKey('role.id'))
)

Pedidos_Productos=db.Table('Pedidos_Productos',
    db.Column('id_pedido',db.Integer,db.ForeignKey('Pedidos.id_pedido')),
    db.Column('id_producto',db.Integer,db.ForeignKey('Producto.id_producto')),
    db.Column('cantidad',db.Integer, nullable=False)
)

class User(UserMixin, db.Model):
    """User account model."""
    
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active=db.Column(db.Boolean)
    confirmed_at=db.Column(db.DateTime)
    roles=db.relationship('Role',
        secondary=user_roles,
        backref=db.backref('users',lazy='dynamic'))

class Role(RoleMixin, db.Model):
    """Role model"""

    __tablename__='role'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50), nullable=False)
    description=db.Column(db.String(255))

class Producto(db.Model):
    __tablename__ = 'Productos'
    id_producto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    imagen = db.Column(db.Text)
    tipo_producto = db.Column(db.Integer, nullable=False)
    precio_venta = db.Column(db.Numeric(10,2), nullable=False)
    cantidad_disponible = db.Column(db.Integer, nullable=False)

class Proveedor(db.Model):
    __tablename__ = 'Proveedores'
    id_proveedor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_empresa = db.Column(db.String(50), nullable=False)
    nombre_contacto = db.Column(db.String(50), nullable=False)
    correo_electronico = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)

class MateriaPrima(db.Model):
    __tablename__ = 'Materias_Primas'
    id_materia_prima = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_proveedor = db.Column(db.Integer, db.ForeignKey('Proveedores.id_proveedor'), nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    unidad_medida = db.Column(db.String(20), nullable=False)
    cantidad_minima_requerida = db.Column(db.Numeric(12,5), nullable=False)
    precio_compra = db.Column(db.Numeric(10,2), nullable=False)
    proveedor = db.relationship('Proveedor', backref='materias_primas')

class Receta(db.Model):
    __tablename__ = 'Receta'
    id_receta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_materia_prima = db.Column(db.Integer, db.ForeignKey('Materias_Primas.id_materia_prima'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('Productos.id_producto'), nullable=False)
    cantidad_requerida = db.Column(db.Numeric(12,5), nullable=False)

class Venta(db.Model):
    __tablename__ = 'Ventas'
    id_venta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    precio_total = db.Column(db.Numeric(10,2), nullable=False)
    fecha_hora_venta = db.Column(db.DateTime, nullable=False)
    

class Pedidos(db.Model):
    id_pedido = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('user.id'))
    estado_pedido = db.Column(db.Integer, nullable=False)
    fecha_hora_pedido = db.Column(db.DateTime, nullable=False)

class Inventario(db.Model):
    id_inventario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_materia_prima = db.Column(db.Integer, db.ForeignKey('Materias_Primas.id_materia_prima'))
    cantidad_almacenada = db.Column(db.Numeric(15,5), nullable=False)
    fecha_registro = db.Column(db.DateTime, nullable=False)

class Perecederos(db.Model):
    id_perecedero = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_materia_prima = db.Column(db.Integer, db.ForeignKey('Materias_Primas.id_materia_prima'))
    descripcion = db.Column(db.String(50))
    cantidad_perdida = db.Column(db.Numeric(12,5), nullable=False)
    fecha_registro = db.Column(db.DateTime, nullable=False)
