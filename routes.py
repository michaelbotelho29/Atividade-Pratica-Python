import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from database import db
from models import Categoria, Produto

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def home():
    # Barra de busca opcional (pesquisar por nome em ordem alfabética)
    termo_busca = request.args.get("busca", "").strip()
    if termo_busca:
        produtos = Produto.query.filter(Produto.nome.ilike(f"%{termo_busca}%")).order_by(Produto.nome.asc()).all()
    else:
        produtos = Produto.query.order_by(Produto.nome.asc()).all()
        
    categorias = Categoria.query.all()
    return render_template("cadastro.html", produtos=produtos, categorias=categorias)

@main_bp.route("/salvar", methods=["POST"])
def salvar_cadastro():
    nome = request.form.get("nome", "").strip()
    preco_str = request.form.get("preco", "").strip()
    categoria_id = request.form.get("categoria_id")
    
    # Validação 1: Nome com menos de 3 caracteres
    if len(nome) < 3:
        return "Erro: O nome do produto deve ter pelo menos 3 caracteres.", 400

    # Validação 2: Proteção e conversão segura do preço (deve ser > 0)
    try:
        preco = float(preco_str)
        if preco <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        return "Erro: O preço informado é inválido ou menor/igual a zero.", 400

    # Tratamento da imagem enviada
    foto = request.files.get("foto")
    nome_imagem = "padrao.png"  # Imagem padrão exigida
    
    if foto and foto.filename != '':
        extensoes_permitidas = {'png', 'jpg', 'jpeg'}
        extensao = foto.filename.rsplit('.', 1)[1].lower() if '.' in foto.filename else ''
        
        if extensao not in extensoes_permitidas:
            return "Erro: Extensão de imagem não permitida!", 400
            
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        caminho_completo = os.path.join(upload_folder, foto.filename)
        foto.save(caminho_completo)
        nome_imagem = foto.filename

    # Registo no banco via ORM
    novo_produto = Produto(
        nome=nome,
        valor=preco,
        peso=0.0,
        imagem=nome_imagem,
        categoria_id=int(categoria_id) if categoria_id else None
    )
    db.session.add(novo_produto)
    db.session.commit()
    
    return redirect(url_for('main.home'))

@main_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    produto = Produto.query.get_or_404(id)
    categorias = Categoria.query.all()

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        preco_str = request.form.get("preco", "").strip()
        categoria_id = request.form.get("categoria_id")

        # Validação 1: Nome com menos de 3 caracteres
        if len(nome) < 3:
            return "Erro: O nome do produto deve ter pelo menos 3 caracteres.", 400

        # Validação 2: Preço válido e maior que zero
        try:
            preco = float(preco_str)
            if preco <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            return "Erro: O preço informado é inválido.", 400

        # Tratamento da troca de imagem
        foto = request.files.get("foto")
        if foto and foto.filename != '':
            extensoes_permitidas = {'png', 'jpg', 'jpeg'}
            extensao = foto.filename.rsplit('.', 1)[1].lower() if '.' in foto.filename else ''
            
            if extensao not in extensoes_permitidas:
                return "Erro: Extensão de imagem não permitida!", 400

            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            # Salva o novo ficheiro
            caminho_completo = os.path.join(upload_folder, foto.filename)
            foto.save(caminho_completo)

            # Remove a foto antiga do disco se não for a padrão
            if produto.imagem and produto.imagem != "padrao.png":
                caminho_antigo = os.path.join(upload_folder, produto.imagem)
                if os.path.exists(caminho_antigo):
                    os.remove(caminho_antigo)

            produto.imagem = foto.filename

        # Atualiza os restantes dados do produto
        produto.nome = nome
        produto.valor = preco
        produto.categoria_id = int(categoria_id) if categoria_id else produto.categoria_id

        db.session.commit()
        return redirect(url_for('main.home'))

    return render_template("editar.html", produto=produto, categorias=categorias)

@main_bp.route("/excluir/<int:id>")
def excluir(id):
    produto = Produto.query.get_or_404(id)
    
    # Remove a imagem do disco se não for a padrão
    if produto.imagem and produto.imagem != "padrao.png":
        caminho_imagem = os.path.join(current_app.root_path, 'static', 'uploads', produto.imagem)
        if os.path.exists(caminho_imagem):
            os.remove(caminho_imagem)
            
    db.session.delete(produto)
    db.session.commit()
    return redirect(url_for('main.home'))