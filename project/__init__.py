import os
from flask import Flask
from flask_login import LoginManager
from flask_security import Security,SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy
import logging
from flask_login import current_user

#Creamos instancia de SQLAlchemy
db = SQLAlchemy()
from .models import User,Role
#Creamos un objeto de SQLAlchemyUserDatastore
userDataStore=SQLAlchemyUserDatastore(db,User,Role)

#Método de inicio de la aplicación
def create_app(test_config=None):
    #Creamos nuestra aplicación de Flask
    app = Flask(__name__)
    
    #Creamos la configuración de la aplicación
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:1218@127.0.0.1/TaconTodo"
    app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
    app.config['SECURITY_PASSWORD_SALT'] = 'secretsalt'

    db.init_app(app)
    #Método para crear la BD en la primera petición
    @app.before_first_request
    def create_all():
        db.create_all()
    
    #Conectando los modelos de Flask-security usando SQLAlchemyUserDatastore
    security=Security(app,userDataStore)

    #Registramos dos Blueprints 
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .inventario.routes import inven as inven_blueprint
    app.register_blueprint(inven_blueprint)

    from .compra.routes import compra as compra_blueprint
    app.register_blueprint(compra_blueprint)

    from .producto.routes import product as product_blueprint
    app.register_blueprint(product_blueprint)

    logging.basicConfig(filename='trazabilidad.log',level=logging.DEBUG)
    logging.info('Arranque de aplicacion')
    logging.shutdown()

    return app

