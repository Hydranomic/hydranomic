// =========================================
// MODAL NOVA META
// =========================================

const botaoNovaMeta = document.getElementById("btn-nova-meta");

const modalNovaMeta = document.getElementById("modal-nova-meta");

const botaoCancelarMeta = document.getElementById("btn-cancelar-meta");


// ABRIR MODAL NOVA META

botaoNovaMeta.addEventListener("click", function () {

    modalNovaMeta.style.display = "flex";

});


// FECHAR MODAL NOVA META

botaoCancelarMeta.addEventListener("click", function () {

    modalNovaMeta.style.display = "none";

});


// =========================================
// MODAL GERENCIAR EQUIPE
// =========================================

const botaoGerenciarEquipe =
    document.getElementById("btn-gerenciar-equipe");

const modalGerenciarEquipe =
    document.getElementById("modal-gerenciar-equipe");

const botaoFecharEquipe =
    document.getElementById("btn-fechar-equipe");


// ABRIR MODAL GERENCIAR EQUIPE

botaoGerenciarEquipe.addEventListener("click", function () {

    modalGerenciarEquipe.style.display = "flex";

});


// FECHAR MODAL GERENCIAR EQUIPE

botaoFecharEquipe.addEventListener("click", function () {

    modalGerenciarEquipe.style.display = "none";

});

// =========================================
// MODAL ADICIONAR FUNCIONÁRIO
// =========================================

const botaoAdicionarFuncionario =
    document.getElementById("btn-adicionar-funcionario");

const modalAdicionarFuncionario =
    document.getElementById("modal-adicionar-funcionario");

const botaoFecharAdicionarFuncionario =
    document.getElementById("btn-fechar-adicionar-funcionario");


// ABRIR MODAL ADICIONAR FUNCIONÁRIO

botaoAdicionarFuncionario.addEventListener("click", function () {

    modalAdicionarFuncionario.style.display = "flex";

});


// FECHAR MODAL ADICIONAR FUNCIONÁRIO

botaoFecharAdicionarFuncionario.addEventListener("click", function () {

    modalAdicionarFuncionario.style.display = "none";

});