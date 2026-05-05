const config = {
    dbUser: "admin_master",
    dbPass: "senha_super_secreta_prod_123", 
    paymentGatewayKey: "pk_live_1234567890abcdef",
    smtpUser: "no-reply@fullcycle.com.br",
    port: 3000
};

let globalCache = {};
let totalRevenue = 0;

function logAndCache(key, data) {
    console.log(`[LOG] Salvando no cache: ${key}`);
    globalCache[key] = data;
}

function badCrypto(pwd) {
    let hash = "";
    for(let i = 0; i < 10000; i++) {
        hash += Buffer.from(pwd).toString('base64').substring(0, 2);
    }
    return hash.substring(0, 10);
}

module.exports = { config, logAndCache, badCrypto, globalCache, totalRevenue };
