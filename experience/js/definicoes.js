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



// =========================================
// MODAL HISTÓRICO DE CONTAS
// =========================================

const btnHistoricoContas = document.querySelector(".historico-contas");
const modalHistoricoContas = document.querySelector("#modal-historico-contas");


// Botão Cancelar da modal de histórico
const btnCancelarHistorico = modalHistoricoContas.querySelector("#btn-cancelar-meta");


// Botão Adicionar conta
const btnAdicionarConta = modalHistoricoContas.querySelector("#btn-criar-meta");


// =========================================
// ABRIR MODAL HISTÓRICO
// =========================================

btnHistoricoContas.addEventListener("click", function () {

    modalHistoricoContas.style.display = "flex";

});


// =========================================
// FECHAR MODAL HISTÓRICO
// =========================================

btnCancelarHistorico.addEventListener("click", function () {

    modalHistoricoContas.style.display = "none";

});


// =========================================
// MODAL ADICIONAR CONTA
// =========================================

const modalAdicionarConta = document.querySelector("#modal-adicionar-conta");


// Botão Cancelar da modal de adicionar conta
const btnCancelarAdicionar = modalAdicionarConta.querySelector("#btn-cancelar-meta");


// =========================================
// ABRIR MODAL ADICIONAR CONTA
// =========================================

btnAdicionarConta.addEventListener("click", function () {

    // Fecha a modal de histórico
    modalHistoricoContas.style.display = "none";

    // Abre a modal de adicionar conta
    modalAdicionarConta.style.display = "block";

});


// =========================================
// FECHAR MODAL ADICIONAR CONTA
// =========================================

btnCancelarAdicionar.addEventListener("click", function () {

    modalAdicionarConta.style.display = "none";

});