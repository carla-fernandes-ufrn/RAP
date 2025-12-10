function alerta_sugestoes() {
    var quantidade_alertas = 0;
    $.ajax({
        url : "/disciplina/numero-sugestoes/", // the endpoint
        type : "GET", // http method
        success: function (response) {
            quantidade_alertas = response["qnt"];
            if (quantidade_alertas > 0) {
                document.getElementById('alerta_sugestoes').innerHTML = quantidade_alertas
            }
            else {
                document.getElementById('alerta_sugestoes').style.display = 'none'
            }
        }
    });    
};

window.onload = function() {
    alerta_sugestoes();
};