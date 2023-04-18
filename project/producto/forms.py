from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FileField, FloatField, validators, TextAreaField, SelectField


def precio_validate(form,field):
    if field.data <= 0:
        raise validators.ValidationError("Ingrese un valor mayor a 0")

def estatus_validate(form, field):
    if field.data < 0:
        raise validators.ValidationError("Debe ser un estatus valido")
    elif field.data == "":
        raise validators.ValidationError("Ingrese un estatus")

def validator_select(form,field):
    if field.data == 0:
        raise validators.ValidationError("Debe seleccionar un proveedor")

class ProductoForm(FlaskForm):
    idProducto = IntegerField("Id Producto:")
    productName = StringField("Nombre producto:",[validators.DataRequired(message="Ingrese un nombre")])
    descripcion = TextAreaField("Descripción:",[validators.DataRequired(message="Ingresa una descripción")])
    tipo_prod = IntegerField("Tipo de producto:",[validators.DataRequired(message="Ingresa un numero de tipo")])
    precioVenta = FloatField("Precio venta:",[precio_validate])
    estatus = IntegerField("Estutus:",[estatus_validate])

class RecetaForm(FlaskForm):
    idReceta = IntegerField("Id Receta:")
    idMateriaPri = IntegerField("Id Materia prima:")
    idProducto = SelectField('Producto:', choices=[], validators=[validator_select])
    cantidadReq = FloatField("Cantidad requerida:")