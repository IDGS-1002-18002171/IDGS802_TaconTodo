function ver_foto() {
    var file = document.getElementById("img_edit").files[0];
    var reader = new FileReader();
    if (file) {
        reader.readAsDataURL(file);
        reader.onloadend = function() {
            document.getElementById("img_original").src = reader.result;
        }
    }
}