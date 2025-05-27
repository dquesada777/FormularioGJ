from . import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# app/models.py (modificar la clase User)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Nuevo campo

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Copropiedad(db.Model):
    __tablename__ = 'copropiedad'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False, unique=True)
    direccion = db.Column(db.String(255), nullable=False)
    nit = db.Column(db.String(20), nullable=True)
    telefono = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    fecha_creacion = db.Column(db.Date, default=db.func.current_date())
    numero_unidades = db.Column(db.Integer, nullable=True)

     # Relación con PropiedadData
    propiedades = db.relationship('PropiedadData', backref='copropiedad', lazy=True)
    
    def __repr__(self):
        return f'<Copropiedad {self.nombre}>'


class PropiedadData(db.Model):
    __tablename__ = 'propiedad_data' # Nombre explícito de la tabla
    id = db.Column(db.Integer, primary_key=True)
    inmueble = db.Column(db.String(200), nullable=False)
    modelo = db.Column(db.String(100))
    principal = db.Column(db.Boolean, default=False)
    agrupar_por = db.Column(db.String(100)) # 'Agruparpor'
    matricula = db.Column(db.String(100), unique=True, nullable=False)
    telefono = db.Column(db.String(50), nullable=False)
    coeficiente = db.Column(db.Float)
    
    # Relación con Copropiedad
    copropiedad_id = db.Column(db.Integer, db.ForeignKey('copropiedad.id'), nullable=False)
    
    # Datos de la Persona (Natural o Jurídica)
    tipo_persona = db.Column(db.String(50), nullable=False) # "Natural" o "Jurídica"
    primer_nombre = db.Column(db.String(100)) # Opcional si es Jurídica
    segundo_nombre = db.Column(db.String(100))
    primer_apellido = db.Column(db.String(100)) # Opcional si es Jurídica
    segundo_apellido = db.Column(db.String(100))
    razon_social = db.Column(db.String(255)) # Opcional si es Natural
    
    # Identificación
    tipo_id = db.Column(db.String(50), nullable=False) # "CC", "NIT", "CE", etc.
    identificacion = db.Column(db.String(100), unique=True, nullable=False)
    dv = db.Column(db.String(1)) # Dígito de Verificación
    
    email = db.Column(db.String(120), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)

    # Campos para calculos internos
    fecha_inicio_facturacion = db.Column(db.Date)
    fecha_ingreso = db.Column(db.Date)
    periodo_de_gracia = db.Column(db.Integer)  # en días o meses según se necesite
    valor_a_pagar_inmueble = db.Column(db.Float)
    valor_presupuesto = db.Column(db.Float)
    valor_a_pagar_constructora = db.Column(db.Float)
    valor_a_pagar_propietario = db.Column(db.Float)


    def __repr__(self):
        return f'<PropiedadData {self.matricula} - {self.inmueble}>'