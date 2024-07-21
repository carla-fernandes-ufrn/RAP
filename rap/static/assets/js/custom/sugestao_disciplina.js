var lista_disciplinas_aceitas = [];
var lista_disciplinas_negadas = [];

var lista_conteudos_aceitos = [];
var lista_conteudos_negados = [];

function negar_disciplina(pk) {
    document.getElementById("aceitar_disciplina_" + pk).classList.remove('text-success');
    document.getElementById("aceitar_disciplina_" + pk).style = 'color: rgba(0, 0, 0, 0.1)';
    document.getElementById("negar_disciplina_" + pk).classList.add('text-danger');
    remover_item_lista(pk, lista_disciplinas_aceitas);
    adicionar_item_lista(pk, lista_disciplinas_negadas);
}

function aceitar_disciplina(pk) {
    document.getElementById("negar_disciplina_" + pk).classList.remove('text-danger');
    document.getElementById("negar_disciplina_" + pk).style = 'color: rgba(0, 0, 0, 0.1)';
    document.getElementById("aceitar_disciplina_" + pk).classList.add('text-success');
    remover_item_lista(pk, lista_disciplinas_negadas);
    adicionar_item_lista(pk, lista_disciplinas_aceitas);
}

function negar_conteudo(pk) {
    document.getElementById("aceitar_conteudo_" + pk).classList.remove('text-success');
    document.getElementById("aceitar_conteudo_" + pk).style = 'color: rgba(0, 0, 0, 0.1)';
    document.getElementById("negar_conteudo_" + pk).classList.add('text-danger');
    remover_item_lista(pk, lista_conteudos_aceitos);
    adicionar_item_lista(pk, lista_conteudos_negados);
}

function aceitar_conteudo(pk) {
    document.getElementById("negar_conteudo_" + pk).classList.remove('text-danger');
    document.getElementById("negar_conteudo_" + pk).style = 'color: rgba(0, 0, 0, 0.1)';
    document.getElementById("aceitar_conteudo_" + pk).classList.add('text-success');
    remover_item_lista(pk, lista_conteudos_negados);
    adicionar_item_lista(pk, lista_conteudos_aceitos);
}

function remover_item_lista(pk, lista) {
    const index = lista.indexOf(pk);
    if (index > -1) {
        lista.splice(index, 1);
    }
}

function adicionar_item_lista(pk, lista) {
    lista.push(pk)
}

$("#form_disciplina").submit(function (e) {
    
    e.preventDefault();

    $.ajax({
        url : "/disciplina/analisar-disciplinas/",
        method : "POST",
        data : { lista_disciplinas_aceitas : lista_disciplinas_aceitas,
            lista_disciplinas_negadas : lista_disciplinas_negadas },
        success: function (returndata) {
            window.location.href = '/disciplina/listar-sugestoes/0'; 
        }
    });
});

$("#form_conteudo").submit(function (e) {
    
    e.preventDefault();

    $.ajax({
        url : "/disciplina/analisar-conteudos/",
        method : "POST",
        data : { lista_conteudos_aceitos : lista_conteudos_aceitos,
            lista_conteudos_negados : lista_conteudos_negados },
        success: function (returndata) {
            window.location.href = '/disciplina/listar-sugestoes/1'; 
        }
    });
});

function mostrar_disciplinas() {
    document.getElementById("div_disciplina").style.display = 'block';
    document.getElementById("div_conteudo").style.display = 'none';
    trocar_cor("btn_disciplina", "btn_conteudo")
}

function mostrar_conteudos() {
    document.getElementById("div_disciplina").style.display = 'none';
    document.getElementById("div_conteudo").style.display = 'block';
    trocar_cor("btn_conteudo", "btn_disciplina")
}

function trocar_cor(nova, antiga) {
    document.getElementById(nova).classList.remove('btn-light');
    document.getElementById(nova).classList.add('btn-success');
    document.getElementById(antiga).classList.remove('btn-success');
    document.getElementById(antiga).classList.add('btn-light');
}

// function finalizar_sugestoes_disciplina() {

//     let cookie = document.cookie
//     let csrfToken = cookie.substring(cookie.indexOf('=') + 1)

//     $.ajax({
//         headers: { 'X-CSRFToken': csrfToken },
//         url : "analisar-disciplinas/",
//         method : "POST",
//         data : { lista_disciplinas_aceitas : lista_disciplinas_aceitas,
//             lista_disciplinas_negadas : lista_disciplinas_negadas },
//         // success: function (returndata) {
//         //     window.location.href = '/disciplina/listar-sugestoes/'; 
//         // }
//     });
// };

// function finalizar_sugestoes_conteudo() {

//     let cookie = document.cookie
//     let csrfToken = cookie.substring(cookie.indexOf('=') + 1)

//     $.ajax({
//         headers: { "X-CSRFToken": csrfToken },
//         url : "analisar-conteudos/", // the endpoint
//         method : "POST", // http method
//         data : { lista_conteudos_aceitos : lista_conteudos_aceitos,
//             lista_conteudos_negados : lista_conteudos_negados }, // data sent with the get request
//     });
// };