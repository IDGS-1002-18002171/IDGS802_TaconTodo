from wtforms import Form
from wtforms import StringField, IntegerField,SelectField, FloatField
from wtforms import EmailField
from wtforms import validators


def validator_select(form,field):
    if field.data == 0:
        raise validators.ValidationError("Debe seleccionar un proveedor")
    
def validator_number(form,field):
    if field.data == 0:
        raise validators.ValidationError("No puede ser 0, ingrese otro valor")
    elif field.data < 0:
        raise validators.ValidationError("No puede ser negativa la cantidad")
    elif field.data > 75:
        raise validators.ValidationError("No debe ser mayor a 75")

def validator_precio(form,field):
    if field.data == 0:
        raise validators.ValidationError("No todo es gratis")
    elif field.data < 0:
        raise validators.ValidationError("Dede ser un precio valido")



class InventarioForm(Form):
    idMateria = IntegerField('ID Mareria:')
    proveedor = SelectField('Proveedor:', choices=[], validators=[validator_select])
    nombreMatpri =  StringField("Nombre de materia:", [validators.DataRequired("El campo es requerido")])
    unidadMedida = StringField("Unidad de medida:",[validators.DataRequired("El campo es requerido")])
    cantMinima = FloatField("Cantidad minima requerida:",[validator_number])
    precioCompra = FloatField("Precio compra:",[validator_precio])
