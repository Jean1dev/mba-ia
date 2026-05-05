from flask import request, jsonify
import models
from database import get_db

def listar_produtos():
    try:
        produtos = models.get_todos_produtos()
        print("Listando " + str(len(produtos)) + " produtos")
        return jsonify({"dados": produtos, "sucesso": True}), 200
    except Exception as e:
        print("ERRO: " + str(e))
        return jsonify({"erro": str(e)}), 500

def buscar_produto(id):
    try:
        produto = models.get_produto_por_id(id)
        if produto:
            return jsonify({"dados": produto, "sucesso": True}), 200
        else:
            return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def criar_produto():
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400
        if "nome" not in dados:
            return jsonify({"erro": "Nome é obrigatório"}), 400
        if "preco" not in dados:
            return jsonify({"erro": "Preço é obrigatório"}), 400
        if "estoque" not in dados:
            return jsonify({"erro": "Estoque é obrigatório"}), 400

        nome = dados["nome"]
        descricao = dados.get("descricao", "")
        preco = dados["preco"]
        estoque = dados["estoque"]
        categoria = dados.get("categoria", "geral")

        if preco < 0:
            return jsonify({"erro": "Preço não pode ser negativo"}), 400
        if estoque < 0:
            return jsonify({"erro": "Estoque não pode ser negativo"}), 400
        if len(nome) < 2:
            return jsonify({"erro": "Nome muito curto"}), 400
        if len(nome) > 200:
            return jsonify({"erro": "Nome muito longo"}), 400

        categorias_validas = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
        if categoria not in categorias_validas:
            return jsonify({"erro": "Categoria inválida. Válidas: " + str(categorias_validas)}), 400

        id = models.criar_produto(nome, descricao, preco, estoque, categoria)
        print("Produto criado com ID: " + str(id))
        return jsonify({"dados": {"id": id}, "sucesso": True, "mensagem": "Produto criado"}), 201

    except Exception as e:
        print("ERRO ao criar produto: " + str(e))
        return jsonify({"erro": str(e)}), 500

def atualizar_produto(id):
    try:
        dados = request.get_json()

        produto_existente = models.get_produto_por_id(id)
        if not produto_existente:
            return jsonify({"erro": "Produto não encontrado"}), 404

        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400
        if "nome" not in dados:
            return jsonify({"erro": "Nome é obrigatório"}), 400
        if "preco" not in dados:
            return jsonify({"erro": "Preço é obrigatório"}), 400
        if "estoque" not in dados:
            return jsonify({"erro": "Estoque é obrigatório"}), 400

        nome = dados["nome"]
        descricao = dados.get("descricao", "")
        preco = dados["preco"]
        estoque = dados["estoque"]
        categoria = dados.get("categoria", "geral")

        if preco < 0:
            return jsonify({"erro": "Preço não pode ser negativo"}), 400
        if estoque < 0:
            return jsonify({"erro": "Estoque não pode ser negativo"}), 400

        models.atualizar_produto(id, nome, descricao, preco, estoque, categoria)
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def deletar_produto(id):
    try:

        produto = models.get_produto_por_id(id)
        if not produto:
            return jsonify({"erro": "Produto não encontrado"}), 404

        models.deletar_produto(id)
        print("Produto " + str(id) + " deletado")
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def buscar_produtos():
    try:
        termo = request.args.get("q", "")
        categoria = request.args.get("categoria", None)
        preco_min = request.args.get("preco_min", None)
        preco_max = request.args.get("preco_max", None)

        if preco_min:
            preco_min = float(preco_min)
        if preco_max:
            preco_max = float(preco_max)

        resultados = models.buscar_produtos(termo, categoria, preco_min, preco_max)
        return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def listar_usuarios():
    try:
        usuarios = models.get_todos_usuarios()

        return jsonify({"dados": usuarios, "sucesso": True}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def buscar_usuario(id):
    try:
        usuario = models.get_usuario_por_id(id)
        if usuario:
            return jsonify({"dados": usuario, "sucesso": True}), 200
        else:
            return jsonify({"erro": "Usuário não encontrado"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def criar_usuario():
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400

        nome = dados.get("nome", "")
        email = dados.get("email", "")
        senha = dados.get("senha", "")

        if not nome or not email or not senha:
            return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400

        id = models.criar_usuario(nome, email, senha)
        print("Usuário criado: " + email)
        return jsonify({"dados": {"id": id}, "sucesso": True}), 201

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def login():
    try:
        dados = request.get_json()
        email = dados.get("email", "")
        senha = dados.get("senha", "")

        if not email or not senha:
            return jsonify({"erro": "Email e senha são obrigatórios"}), 400

        usuario = models.login_usuario(email, senha)
        if usuario:

            print("Login bem-sucedido: " + email)
            return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
        else:
            print("Login falhou: " + email)
            return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def criar_pedido():
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400

        usuario_id = dados.get("usuario_id")
        itens = dados.get("itens", [])

        if not usuario_id:
            return jsonify({"erro": "Usuario ID é obrigatório"}), 400
        if not itens or len(itens) == 0:
            return jsonify({"erro": "Pedido deve ter pelo menos 1 item"}), 400

        resultado = models.criar_pedido(usuario_id, itens)

        if "erro" in resultado:
            return jsonify({"erro": resultado["erro"], "sucesso": False}), 400

        print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]) + " criado para usuario " + str(usuario_id))
        print("ENVIANDO SMS: Seu pedido foi recebido!")
        print("ENVIANDO PUSH: Novo pedido recebido pelo sistema")

        return jsonify({
            "dados": resultado,
            "sucesso": True,
            "mensagem": "Pedido criado com sucesso"
        }), 201

    except Exception as e:
        print("ERRO CRITICO ao criar pedido: " + str(e))
        return jsonify({"erro": str(e)}), 500

def listar_pedidos_usuario(usuario_id):
    try:
        pedidos = models.get_pedidos_usuario(usuario_id)
        return jsonify({"dados": pedidos, "sucesso": True}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def listar_todos_pedidos():
    try:

        pedidos = models.get_todos_pedidos()
        return jsonify({"dados": pedidos, "sucesso": True}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def atualizar_status_pedido(pedido_id):
    try:
        dados = request.get_json()
        novo_status = dados.get("status", "")

        if novo_status not in ["pendente", "aprovado", "enviado", "entregue", "cancelado"]:
            return jsonify({"erro": "Status inválido"}), 400

        models.atualizar_status_pedido(pedido_id, novo_status)

        if novo_status == "aprovado":
            print("NOTIFICAÇÃO: Pedido " + str(pedido_id) + " foi aprovado! Preparar envio.")
        if novo_status == "cancelado":
            print("NOTIFICAÇÃO: Pedido " + str(pedido_id) + " cancelado. Devolver estoque.")

        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def relatorio_vendas():
    try:
        relatorio = models.relatorio_vendas()
        return jsonify({"dados": relatorio, "sucesso": True}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def health_check():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        cursor.execute("SELECT COUNT(*) FROM produtos")
        produtos = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        usuarios = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        pedidos = cursor.fetchone()[0]

        return jsonify({
            "status": "ok",
            "database": "connected",
            "counts": {
                "produtos": produtos,
                "usuarios": usuarios,
                "pedidos": pedidos
            },

            "versao": "1.0.0",
            "ambiente": "producao",
            "db_path": "loja.db",
            "debug": True,
            "secret_key": "minha-chave-super-secreta-123"
        }), 200
    except Exception as e:
        return jsonify({"status": "erro", "detalhes": str(e)}), 500
