from wtforms import Form
from wtforms import StringField, IntegerField, FileField, FloatField, validators, TextAreaField, SelectField

class ProductoForm(Form):
    idProducto = IntegerField("Id Producto:")
    productName = StringField("Nombre producto:")
    descripcion = TextAreaField("Descripción:")
    img = FileField("Cargar imagen:")
    tipo_prod = IntegerField("Tipo de producto:")
    precioVenta = FloatField("Precio venta:")

class RecetaForm(Form):
    idReceta = IntegerField("Id Receta:")
    idMateriaPri = IntegerField("Id Materia prima:")
    idProducto = IntegerField("Id Producto:")
    cantidadReq = FloatField("Cantidad requerida:")