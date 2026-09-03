// Modal de nova meta
const botaoNovaMeta = document.querySelector("button-nova-meta");
const modalNovaMeta = document.querySelector(".nova-meta");
const botaoCancelarMeta = document.querySelector("button-cancelar-meta");


// Abrir Nova Meta
botaoNovaMeta.addEventListener("click", function () {
    modalNovaMeta.style.display = "flex";
});


// Fechar Nova Meta
botaoCancelarMeta.addEventListener("click", function () {
    modalNovaMeta.style.display = "none";
});


// Modal de gerenciamento da equipe
const botaoGerenciarEquipe =
    document.querySelector("button-gerenciar-equipe");

const modalGerenciarEquipe =
    document.querySelector(".gerenciar-equipe");

const botaoFecharEquipe =
    document.querySelector("button-fechar-gerenciar-equipe");


// Abrir Gerenciar Equipe
botaoGerenciarEquipe.addEventListener("click", function () {
    modalGerenciarEquipe.style.display = "flex";
});


// Fechar Gerenciar Equipe
botaoFecharEquipe.addEventListener("click", function () {
    modalGerenciarEquipe.style.display = "none";
});