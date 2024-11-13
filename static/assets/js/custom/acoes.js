function alterar_status_acao(pk) {
    $.ajax({
        url: "/acoes/alterar-status-acao/"+pk, // the endpoint
        type: "GET", // http method
        success: function(response) {
            card_header_informacoes = document.getElementById("card_header_informacoes");
            card_header_midias = document.getElementById("card_header_midias");
            card_header_mensagens = document.getElementById("card_header_mensagens");
            icone_locker = document.getElementById("icone_locker");
            if (response) {
                icone_locker.classList.remove("fa-lock");
                icone_locker.classList.add("fa-lock-open");
                card_header_informacoes.classList.remove('bg-gradient-secondary');
                card_header_informacoes.classList.add('bg-gradient-primary');
                card_header_midias.classList.remove('bg-gradient-secondary');
                card_header_midias.classList.add('bg-gradient-warning');
                card_header_mensagens.classList.remove('bg-gradient-secondary');
                card_header_mensagens.classList.add('bg-gradient-success');
            }
            else {
                icone_locker.classList.add("fa-lock");
                icone_locker.classList.remove("fa-lock-open");
                card_header_informacoes.classList.add('bg-gradient-secondary');
                card_header_informacoes.classList.remove('bg-gradient-primary');
                card_header_midias.classList.add('bg-gradient-secondary');
                card_header_midias.classList.remove('bg-gradient-warning');
                card_header_mensagens.classList.add('bg-gradient-secondary');
                card_header_mensagens.classList.remove('bg-gradient-success');
            }
        }
    });
}

function alterar_status_acao_listar(pk) {
    $.ajax({
        url: "/acoes/alterar-status-acao-listar/"+pk, // the endpoint
        type: "GET", // http method
        success: function(response) {
            
        }
    });
}