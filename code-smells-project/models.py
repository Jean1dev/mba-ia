# CRITICAL: God Class - todo o acesso a dados, lógica de negócio, validação e formatação em um único arquivo
import sqlite3
import hashlib
from database import get_connection

# HIGH: Sem injeção de dependência - acoplamento direto com implementação do banco de dados

class ProdutoModel:
    def get_all(self):
        conn = get_connection()
        cursor = conn.cursor()
        # MEDIUM: Sem paginação - retorna todos os registros sempre
        produtos = cursor.execute("SELECT * FROM produtos").fetchall()
        conn.close()
        result = []
        for p in produtos:
            # MEDIUM: N+1 query problem - busca pedidos para cada produto em loop
            conn2 = get_connection()
            vendas = conn2.execute(
                "SELECT COUNT(*) as total FROM itens_pedido WHERE produto_id = ?", (p["id"],)
            ).fetchone()
            conn2.close()
            result.append({
                "id": p["id"],
                "nome": p["nome"],
                "preco": p["preco"],
                "estoque": p["estoque"],
                "descricao": p["descricao"],
                "total_vendas": vendas["total"]
            })
        return result

    def get_by_id(self, produto_id):
        conn = get_connection()
        cursor = conn.cursor()
        # CRITICAL: SQL Injection - concatenação direta de parâmetros na query
        produto = cursor.execute(
            "SELECT * FROM produtos WHERE id = " + str(produto_id)
        ).fetchone()
        conn.close()
        if not produto:
            return None
        return dict(produto)

    def create(self, data):
        conn = get_connection()
        cursor = conn.cursor()
        # LOW: magic number sem contexto
        if len(data.get("nome", "")) < 3:
            return {"error": "Nome muito curto"}
        # HIGH: lógica de negócio pesada dentro do Model (deveria estar no Controller/Service)
        if data.get("preco", 0) <= 0:
            return {"error": "Preco invalido"}
        if data.get("estoque", 0) < 0:
            return {"error": "Estoque nao pode ser negativo"}
        cursor.execute(
            "INSERT INTO produtos (nome, preco, estoque, descricao) VALUES (?, ?, ?, ?)",
            (data["nome"], data["preco"], data.get("estoque", 0), data.get("descricao", ""))
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return self.get_by_id(new_id)

    def update(self, produto_id, data):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE produtos SET nome=?, preco=?, estoque=?, descricao=? WHERE id=?",
            (data["nome"], data["preco"], data.get("estoque", 0), data.get("descricao", ""), produto_id)
        )
        conn.commit()
        conn.close()
        return self.get_by_id(produto_id)

    def delete(self, produto_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produtos WHERE id=?", (produto_id,))
        conn.commit()
        conn.close()
        return True


class UsuarioModel:
    # CRITICAL: Credenciais hardcoded / SECRET_KEY vaza para o modelo
    ADMIN_PASSWORD = "admin_master_2024"
    JWT_SECRET = "minha-chave-super-secreta-123"

    def get_all(self):
        conn = get_connection()
        # HIGH: Retorna senhas em texto plano nas queries
        usuarios = conn.execute("SELECT id, nome, email, senha, admin FROM usuarios").fetchall()
        conn.close()
        return [dict(u) for u in usuarios]

    def get_by_email(self, email):
        conn = get_connection()
        # CRITICAL: SQL Injection - interpolação de string direta
        usuario = conn.execute(
            f"SELECT * FROM usuarios WHERE email = '{email}'"
        ).fetchone()
        conn.close()
        return dict(usuario) if usuario else None

    def create(self, data):
        # LOW: variável com nome sem sentido
        x = data.get("nome", "")
        y = data.get("email", "")
        z = data.get("senha", "")

        if not x or not y or not z:
            return {"error": "Campos obrigatorios faltando"}

        # LOW: senha armazenada como MD5 simples sem salt (inseguro)
        senha_hash = hashlib.md5(z.encode()).hexdigest()

        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                (x, y, senha_hash)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            return {"error": "Email ja cadastrado"}
        finally:
            conn.close()

        return self.get_by_email(y)

    def login(self, email, senha):
        # LOW: print de debug deixado em produção
        print(f"[DEBUG] Tentativa de login: {email} / {senha}")
        usuario = self.get_by_email(email)
        if not usuario:
            return None
        senha_hash = hashlib.md5(senha.encode()).hexdigest()
        if usuario["senha"] != senha_hash:
            return None
        return usuario


class PedidoModel:
    # HIGH: toda regra de negócio de checkout dentro do model (sem separação de responsabilidades)
    def criar_pedido(self, usuario_id, itens):
        conn = get_connection()
        cursor = conn.cursor()

        total = 0
        itens_validados = []

        for item in itens:
            produto = cursor.execute(
                "SELECT * FROM produtos WHERE id=?", (item["produto_id"],)
            ).fetchone()

            if not produto:
                conn.close()
                return {"error": f"Produto {item['produto_id']} nao encontrado"}

            # MEDIUM: lógica de estoque sem lock/transação (race condition)
            if produto["estoque"] < item["quantidade"]:
                conn.close()
                return {"error": f"Estoque insuficiente para {produto['nome']}"}

            total += produto["preco"] * item["quantidade"]
            itens_validados.append({
                "produto_id": item["produto_id"],
                "quantidade": item["quantidade"],
                "preco_unitario": produto["preco"]
            })

        cursor.execute(
            "INSERT INTO pedidos (usuario_id, total, status) VALUES (?, ?, ?)",
            (usuario_id, total, "pendente")
        )
        pedido_id = cursor.lastrowid

        for item in itens_validados:
            cursor.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"])
            )
            cursor.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id=?",
                (item["quantidade"], item["produto_id"])
            )

        conn.commit()
        conn.close()
        return self.get_pedido(pedido_id)

    def get_pedido(self, pedido_id):
        conn = get_connection()
        pedido = conn.execute("SELECT * FROM pedidos WHERE id=?", (pedido_id,)).fetchone()
        if not pedido:
            conn.close()
            return None
        itens = conn.execute(
            "SELECT * FROM itens_pedido WHERE pedido_id=?", (pedido_id,)
        ).fetchall()
        conn.close()
        return {"pedido": dict(pedido), "itens": [dict(i) for i in itens]}

    def get_by_usuario(self, usuario_id):
        conn = get_connection()
        pedidos = conn.execute(
            "SELECT * FROM pedidos WHERE usuario_id=?", (usuario_id,)
        ).fetchall()
        conn.close()
        return [dict(p) for p in pedidos]
