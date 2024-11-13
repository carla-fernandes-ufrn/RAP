function marcar_favorito(plano_aula, usuario, funcao_listar) {
    $.ajax({
        url : "/plano-aula/marcar-favorito/"+plano_aula+"/"+usuario,
        method : "GET",
        success: function (returndata) {
            alterar_contador("thumbs_up", plano_aula, returndata)
            trocar_cor("thumbs_up", plano_aula, returndata);
            if (funcao_listar==='favoritos' && returndata === 0) {
                document.getElementById("card_plano_aula_"+plano_aula).remove()
            }
        }
    });
}

function marcar_executado(plano_aula, usuario, funcao_listar) {
    $.ajax({
        url : "/plano-aula/marcar-executado/"+plano_aula+"/"+usuario,
        method : "GET",
        success: function (returndata) {
            alterar_contador("play", plano_aula, returndata);
            trocar_cor("play", plano_aula, returndata);
            if (funcao_listar==='executados' && returndata === 0) {
                document.getElementById("card_plano_aula_"+plano_aula).remove()
                var main_div = document.getElementById("main_div")
                var cards = document.getElementsByClassName("card")
            }
        }
    });
}

function alterar_contador(tipo, id, returndata) {
    const str = "contador_" + tipo + "_" + id.toString()
    const elemento = document.getElementById(str)
    if (returndata == 0) {
        elemento.textContent = (parseInt(elemento.textContent) - 1).toString();
    }
    else {
        elemento.textContent = (parseInt(elemento.textContent) + 1).toString();
    }
}

function trocar_cor(tipo, id, returndata) {
    console.log("Entrei")
    const str = "icon_" + tipo + "_" + id.toString()
    const elemento = document.getElementById(str)
    if (returndata == 0) {
        elemento.style = 'color: gray;';
    }
    else {
        elemento.style = 'color: var(--bs-success);';
    }
}