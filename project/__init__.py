from flask import Flask, session
from flask_login import LoginManager,current_user
from flask_security import Security,SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy
import json,os,stripe,logging

#Creamos instancia de SQLAlchemy
db = SQLAlchemy()
from .models import User,Role
#Creamos un objeto de SQLAlchemyUserDatastore
userDataStore=SQLAlchemyUserDatastore(db,User,Role)

stripe.api_key = 'sk_test_51MtEODBMu9RgSpPEini9G9YdSjjoepnch1SljAmu7plwuVrwEm8QhxNs63Pi7585IZo7byXP2ee64jHukEobNc7c00LUPvOz6q'
    
#Método de inicio de la aplicación
def create_app(test_config=None):
    #Creamos nuestra aplicación de Flask
    app = Flask(__name__)
        #,static_folder='templates',
            #static_url_path='', template_folder='templates'
    #Creamos la configuración de la aplicación
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:root@127.0.0.1/TaconTodo"
    app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
    app.config['SECURITY_PASSWORD_SALT'] = 'secretsalt'
    


    db.init_app(app)

    #Conectando los modelos de Flask-security usando SQLAlchemyUserDatastore
    security=Security(app,userDataStore)

    #Registramos dos Blueprints 
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .venta.routes import venta as venta_blueprint
    app.register_blueprint(venta_blueprint)

    from .pedido.routes import pedido as pedido_blueprint
    app.register_blueprint(pedido_blueprint)
    
    from .proovedores.routes import proveedores as proveedores_blueprint
    app.register_blueprint(proveedores_blueprint)

    from .usuarios.routes import usuarios as usuarios_blueprint
    app.register_blueprint(usuarios_blueprint)


    from .inventario.routes import inven as inven_blueprint
    app.register_blueprint(inven_blueprint)

    from .compra.routes import compra as compra_blueprint
    app.register_blueprint(compra_blueprint)

    from .producto.routes import product as product_blueprint
    app.register_blueprint(product_blueprint)

    logging.basicConfig(filename='trazabilidad.log',level=logging.DEBUG)
    logging.basicConfig(filename='pedidos.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
    logging.info('Arranque de aplicacion')
    logging.shutdown()

    return app

