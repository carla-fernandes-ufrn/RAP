function mostrar_em_aberto() {
    document.getElementById("div_em_aberto").style.display = 'block';
    document.getElementById("div_aceitos").style.display = 'none';
    document.getElementById("div_negados").style.display = 'none';
    trocar_cor("btn_em_aberto", "btn_aceitos", "btn_negados")
}

function mostrar_aceitos() {
    document.getElementById("div_em_aberto").style.display = 'none';
    document.getElementById("div_aceitos").style.display = 'block';
    document.getElementById("div_negados").style.display = 'none';
    trocar_cor("btn_aceitos", "btn_em_aberto", "btn_negados")
}

function mostrar_negados() {
    document.getElementById("div_em_aberto").style.display = 'none';
    document.getElementById("div_aceitos").style.display = 'none';
    document.getElementById("div_negados").style.display = 'block';
    trocar_cor("btn_negados", "btn_em_aberto", "btn_aceitos")
}

function trocar_cor(nova, antiga1, antiga2) {
    document.getElementById(nova).classList.remove('btn-light');
    document.getElementById(nova).classList.add('btn-success');
    document.getElementById(antiga1).classList.remove('btn-success');
    document.getElementById(antiga1).classList.add('btn-light');
    document.getElementById(antiga2).classList.remove('btn-success');
    document.getElementById(antiga2).classList.add('btn-light');
}