const inputBusca = document.getElementById('input_busca');

if (inputBusca) {
    inputBusca.addEventListener('keyup', function() {
        const termo = inputBusca.value;

        if (window.location.pathname.includes('/buscar/')) {
            // Live Search
            fetch(`/buscar-ajax/?q=${termo}`)
                .then(response => response.json())
                .then(data => {
                    const div = document.getElementById('resultado_busca');
                    div.innerHTML = '';

                    data.planos.forEach(plano => {
                        div.innerHTML += `
                            <div class="card border-primary mb-2">
                                <div class="card-body">
                                    <h5 class="card-title">${plano.titulo}</h5>
                                    <a href="/plano-aula/detalhes/${plano.id}">Ver Plano de Aula</a>
                                </div>
                            </div>`;
                    });

                    data.acoes.forEach(acao => {
                        div.innerHTML += `
                            <div class="card border-warning mb-2">
                                <div class="card-body">
                                    <h5 class="card-title">${acao.titulo}</h5>
                                    <a href="/acoes/detalhes/${acao.id}">Ver Ação</a>
                                </div>
                            </div>`;
                    });

                    data.usuarios.forEach(usuario => {
                        div.innerHTML += `
                            <div class="card border-purple mb-2" style="border-color: purple;">
                                <div class="card-body">
                                    <h5 class="card-title">${usuario.first_name} ${usuario.last_name}</h5>
                                    <a href="/usuario/perfil/${usuario.id}">Ver Perfil</a>
                                </div>
                            </div>`;
                    });
                });
        }
    });
}
