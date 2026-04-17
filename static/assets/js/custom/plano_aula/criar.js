let passoAtual = 1;
let conteudosSelecionados = [];

function carregarConteudosSelecionadosIniciais() {
    const hidden = document.getElementById('lista_id_conteudos').value.trim();

    if (!hidden) {
        conteudosSelecionados = [];
        atualizarContadorSelecionados();
        atualizarEstadoVazioSelecionados();
        return;
    }

    conteudosSelecionados = hidden
        .split(',')
        .map(i => i.trim())
        .filter(i => i !== '');

    atualizarContadorSelecionados();
    atualizarEstadoVazioSelecionados();
}

function mostrarPasso(numero) {
    passoAtual = numero;

    document.querySelectorAll('.step-pane').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.wizard-step').forEach(s => s.classList.remove('active'));

    document.getElementById(`passo${numero}`).classList.add('active');
    document.getElementById(`indicator-passo${numero}`).classList.add('active');

    document.getElementById('btn-voltar').style.display = numero === 1 ? 'none' : 'inline-block';
    document.getElementById('btn-proximo').style.display = numero === 4 ? 'none' : 'inline-block';
    document.getElementById('btn-submit').style.display = numero === 4 ? 'inline-block' : 'none';

    if (numero === 4) {
        preencherRevisao();
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function proximoPasso() {
    if (passoAtual < 4) {
        mostrarPasso(passoAtual + 1);
    }
}

function voltarPasso() {
    if (passoAtual > 1) {
        mostrarPasso(passoAtual - 1);
    }
}

function atualizarHiddenConteudos() {
    document.getElementById('lista_id_conteudos').value = conteudosSelecionados.join(',');
    atualizarContadorSelecionados();
    atualizarEstadoVazioSelecionados();
}

function atualizarContadorSelecionados() {
    document.getElementById('selected-counter').innerText = conteudosSelecionados.length;
}

function atualizarEstadoVazioSelecionados() {
    const empty = document.getElementById('selected-empty');
    empty.style.display = conteudosSelecionados.length ? 'none' : 'block';
}

function criarChipConteudo(id, conteudo, disciplina) {
    const chipsContainer = document.getElementById('selected-chips');

    if (document.getElementById(`chip-${id}`)) {
        return;
    }

    const chip = document.createElement('span');
    chip.className = 'selected-chip';
    chip.id = `chip-${id}`;
    chip.innerHTML = `
        ${conteudo} — ${disciplina}
        <button type="button" onclick="removeConteudo('${id}')">×</button>
    `;

    chipsContainer.appendChild(chip);
}

function removeChipConteudo(id) {
    const chip = document.getElementById(`chip-${id}`);
    if (chip) {
        chip.remove();
    }
}

function marcarCardSelecionado(id, selected) {
    const item = document.querySelector(`.content-item[data-id="${id}"]`);
    if (!item) return;

    if (selected) {
        item.classList.add('selected');
    } else {
        item.classList.remove('selected');
    }
}

function toggleConteudo(id, conteudo, disciplina) {
    id = String(id);

    if (conteudosSelecionados.includes(id)) {
        removeConteudo(id);
        return;
    }

    conteudosSelecionados.push(id);
    criarChipConteudo(id, conteudo, disciplina);
    marcarCardSelecionado(id, true);
    atualizarHiddenConteudos();
}

function removeConteudo(id) {
    id = String(id);
    conteudosSelecionados = conteudosSelecionados.filter(i => i !== id);
    removeChipConteudo(id);
    marcarCardSelecionado(id, false);
    atualizarHiddenConteudos();
}

function configurarBuscaConteudos() {
    const input = document.getElementById('busca_conteudo');
    const lista = document.getElementById('content-list');
    const msg = document.getElementById('content-search-empty');
    const items = document.querySelectorAll('.content-item');

    input.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault();
        }
    });

    input.addEventListener('input', function () {
        const termo = this.value.toLowerCase().trim();
        let encontrou = false;

        if (!termo) {
            lista.style.display = 'none';
            msg.style.display = 'block';
            msg.innerText = 'Digite para buscar conteúdos.';
            items.forEach(i => i.style.display = 'none');
            return;
        }

        lista.style.display = 'block';
        msg.style.display = 'none';

        items.forEach(i => {
            const ok = i.dataset.conteudo.includes(termo) || i.dataset.disciplina.includes(termo);
            i.style.display = ok ? 'block' : 'none';
            if (ok) encontrou = true;
        });

        if (!encontrou) {
            lista.style.display = 'none';
            msg.style.display = 'block';
            msg.innerText = 'Nenhum conteúdo encontrado.';
        }
    });
}

function preencherRevisao() {
    document.getElementById('review_titulo').innerText =
        document.getElementById('id_titulo')?.value || '—';

    document.getElementById('review_contextualizacao').innerText =
        document.getElementById('id_contextualizacao')?.value || '—';

    document.getElementById('review_descricao_atividade').innerText =
        document.getElementById('id_descricao_atividade')?.value || '—';

    document.getElementById('review_avaliacao').innerText =
        document.getElementById('id_avaliacao')?.value || '—';

    document.getElementById('review_nivel_montagem').innerText =
        document.getElementById('id_nivel_dificuldade_montagem')?.selectedOptions?.[0]?.text || '—';

    document.getElementById('review_robo_equipamento').innerText =
        document.getElementById('id_robo_equipamento')?.value || '—';

    document.getElementById('review_robo_descricao').innerText =
        document.getElementById('id_robo_descricao')?.value || '—';

    document.getElementById('review_nivel_programacao').innerText =
        document.getElementById('id_nivel_dificuldade_programacao')?.selectedOptions?.[0]?.text || '—';

    document.getElementById('review_prog_linguagem').innerText =
        document.getElementById('id_prog_linguagem')?.value || '—';

    document.getElementById('review_prog_descricao').innerText =
        document.getElementById('id_prog_descricao')?.value || '—';

    const reviewConteudos = document.getElementById('review_conteudos');
    const selecionados = document.querySelectorAll('#selected-chips .selected-chip');

    if (!selecionados.length) {
        reviewConteudos.innerHTML = '<span class="text-muted">Nenhum conteúdo selecionado.</span>';
    } else {
        reviewConteudos.innerHTML = '';
        selecionados.forEach(chip => {
            const novo = document.createElement('div');
            novo.className = 'mb-2';
            novo.innerText = chip.childNodes[0].textContent.trim();
            reviewConteudos.appendChild(novo);
        });
    }
}

document.addEventListener('DOMContentLoaded', function () {
    carregarConteudosSelecionadosIniciais();
    configurarBuscaConteudos();

    const abaSelecionada = window.abaSelecionada || 'passo1';

    if (abaSelecionada === 'passo3') {
        mostrarPasso(3);
    } else if (abaSelecionada === 'passo4') {
        mostrarPasso(4);
    } else if (abaSelecionada === 'passo2') {
        mostrarPasso(2);
    } else {
        mostrarPasso(1);
    }
});