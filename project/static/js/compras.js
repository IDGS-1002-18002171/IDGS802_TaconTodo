function cargarDatosCompra(){

    var idMateria = $("#select_compra").val();

    $.ajax({
        url: "/cargar_datos/" + idMateria,
        type: "POST",
        success: function(data){
            $("#txtIdMaPr").val(data.idMateria);
            $("#txtproveedor").val(data.proveedor);
            $("#txtUnidadM").val(data.unidad);
            $("#txtCantidadMin").val(data.cant_min);
            $("#txtPreciocom").val(data.precioCompra);
            $("#txtPrecioTotal").val(0.00)
            $("#txtCantidad").val(0)
        }
        
    });

}

// Poner el precio en tiempo real

const cant_c = document.getElementById("txtCantidad")
var precioT = document.getElementById("txtPrecioTotal")
var precioU = document.getElementById("txtPreciocom")


cant_c.addEventListener("input",()=>{

    let cantidads = parseFloat(cant_c.value);
    let pru = parseFloat(precioU.value);
    let precioTotal = cantidads *  pru;

    if (!isNaN(precioTotal)) {
        precioT.value = "$" + precioTotal.toFixed(2);
    };
});

// Validaciones del formulario de compras //

// const selectC = document.getElementById("select_compra");
// const cantidad = document.getElementById("txtCantidad");
// const form = document.getElementById("solicitud_compra");
// const cantidadMin = document.getElementById("txtCantidadMin");
// const warningsDiv = document.getElementById("warnings");

// form.addEventListener("submit", e=>{
//     e.preventDefault()
//     let warnings = "";
//     let enviar = false;
//     warningsDiv.innerHTML = "";
//     if(selectC.value == "disabled"){
//         warnings += "Selecciona una materia prima <br>"
//         enviar = true
//     }

//     if(cantidad.value < cantidadMin.value){
//         warnings += "Debes comprar como minimo la cantidad pedida <br>"
//         enviar = true
//     }

//     if(enviar){
//         warningsDiv.innerHTML = warnings;
//     }

// });

(() => {
    'use strict'
  
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    const forms = document.querySelectorAll('.needs-validation')
  
    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
      form.addEventListener('submit', event => {
        if (!form.checkValidity()) {
          event.preventDefault()
          event.stopPropagation()
        }
  
        form.classList.add('was-validated')
      }, false)
    })
  })()