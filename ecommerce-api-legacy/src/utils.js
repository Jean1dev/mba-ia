// LOW: funções utilitárias sem documentação, nomes genéricos
function formatMoney(val) {
    // LOW: magic number sem constante nomeada
    return parseFloat(val).toFixed(2);
}

function calcDesconto(preco, pct) {
    // LOW: nome de parâmetro abreviado sem clareza
    return preco - (preco * pct / 100);
}

// HIGH: estado global mutável compartilhado entre requests
let activeUsers = {};
let sessionStore = {};

function addSession(userId, token) {
    sessionStore[token] = { userId, createdAt: Date.now() };
    activeUsers[userId] = token;
}

function getSession(token) {
    return sessionStore[token] || null;
}

// MEDIUM: sem limpeza de sessões expiradas - memory leak
function clearExpiredSessions() {
    // TODO: implementar limpeza
}

// LOW: função nunca utilizada
function slugify(text) {
    return text.toLowerCase().replace(/ /g, '-').replace(/[^\w-]+/g, '');
}

module.exports = { formatMoney, calcDesconto, addSession, getSession, activeUsers, sessionStore };
