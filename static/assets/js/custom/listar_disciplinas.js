function mostrar_disciplinas() {
    document.getElementById("div_disciplina").style.display = 'block';
    document.getElementById("div_conteudo").style.display = 'none';
    document.getElementById('div-alert-conteudo').style.display = "none";
    trocar_cor("btn_disciplina", "btn_conteudo")
}

function mostrar_conteudos() {
    document.getElementById("div_disciplina").style.display = 'none';
    document.getElementById("div_conteudo").style.display = 'block';
    document.getElementById('div-alert-disciplina').style.display = "none";
    trocar_cor("btn_conteudo", "btn_disciplina")
}

function trocar_cor(nova, antiga) {
    document.getElementById(nova).classList.remove('btn-outline-secondary');
    document.getElementById(nova).classList.add('btn-outline-success');
    document.getElementById(antiga).classList.remove('btn-outline-success');
    document.getElementById(antiga).classList.add('btn-outline-secondary');
}

function sugerir_disciplina() {
  nome = document.getElementById('disciplina_text').value;
  if (nome != "") {
    $.ajax({
        url : "/disciplina/sugerir-disciplina/", // the endpoint
        type : "POST", // http method
        data : { nome : nome }, // data sent with the get request
    });
    document.getElementById('disciplina_text').value = "";
    document.getElementById('div-alert-disciplina').style.display = "block";
    document.getElementById('text-alert-disciplina').innerHTML = "A sugestão da disciplina <strong>" + nome + "</strong> foi enviada com sucesso.";
  }
};

function sugerir_conteudo() {
    nome = document.getElementById('conteudo_text').value;
    disciplina = document.getElementById('disciplina_selecionada').value;
    if (nome != "" && disciplina != "") {
        $.ajax({
            url : "/disciplina/sugerir-conteudo/", // the endpoint
            type : "POST", // http method
            data : { nome : nome, 
                    disciplina : disciplina }, // data sent with the post request
        });
        document.getElementById('conteudo_text').value = ""
        document.getElementById('disciplina_selecionada').value = ""
        document.getElementById('div-alert-conteudo').style.display = "block";
        document.getElementById('text-alert-conteudo').innerHTML = "A sugestão do conteúdo <strong>" + nome + "</strong> foi enviado com sucesso.";
    }
};