from database import db

class Categoria(db.Model):
    __tablename__ = 'categoria'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    peso = db.Column(db.Float, nullable=False)
    
    # Permite aceder aos produtos associados a esta categoria
    produtos = db.relationship('Produto', backref='categoria', lazy=True)
    
class Produto(db.Model):
    __tablename__ = 'produto'

    id = db.Column(db.Integer, primary_key=True)
    peso = db.Column(db.Float, nullable=False, default=0.0)
    valor = db.Column(db.Float, nullable=False, default=0.0)
    nome = db.Column(db.String(100), nullable=False)
    imagem = db.Column(db.String(200), nullable=False, default='static/uploads/padrao.png')
    
    # Chave estrangeira para ligar à tabela Categoria
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)