import os
from flask import Flask
from database import db
from models import Categoria, Produto
from routes import main_bp

app = Flask(__name__)

# Configuração da Chave Secreta
app.secret_key = "sua_chave_secreta_aqui"

# Configuração do Banco de Dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização da extensão do banco de dados na aplicação
db.init_app(app)

# Registro do Blueprint com as rotas do projeto
app.register_blueprint(main_bp)

# Criação automática das tabelas SQLite e inserção de 3 categorias iniciais
with app.app_context():
    db.create_all()
    
    # Garante que o banco possui pelo menos 3 categorias cadastradas
    if Categoria.query.count() == 0:
        c1 = Categoria(nome="Eletrônicos", peso=1.0)
        c2 = Categoria(nome="Alimentos", peso=0.5)
        c3 = Categoria(nome="Vestuário", peso=0.3)
        db.session.add_all([c1, c2, c3])
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)