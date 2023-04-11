// Validaciones del formulario de materia prima //

// const selectPro = document.getElementById("select_pro");
// const nombreMa = document.getElementById("txtNmateria");
// const uniMe = document.getElementById("txtUnitM");
// const cantMin = document.getElementById("txtCantMin");
// const precioCom = document.getElementById("txtPreCo");
// const formInv = document.getElementById("form_matpr");
// const adver = document.getElementById("advertencia");

// formInv.addEventListener("submit", e=>{
//     e.preventDefault()
//     let warnings2 = "";
//     let enviar = false;
//     adver.innerHTML = "";
//     if(selectPro.value == "disabled"){
//         warnings2 += "Selecciona un proveedor <br>"
//         enviar = true
//     };

//     if(nombreMa.value == ''){
//         warnings2 += "Ingrese nombre de materia prima <br>"
//         enviar = true
//     };

//     if(uniMe.value == ''){
//         warnings2 += "Ingrese unidad de medida <br>"
//         enviar = true
//     };

//     if(cantMin == ''){
//         warnings2 += "Ingrese una cantidad <br>"
//         enviar = true
//     };

//     if(precioCom.value == ''){
//         warnings2 += "Ingrese un precio <br>"
//         enviar = true
//     };

//     if(enviar){
//         adver.innerHTML = warnings2;
//     };

// });