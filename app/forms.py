from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, DateField, IntegerField, DecimalField, PasswordField, SubmitField, TextAreaField, BooleanField, SelectField, FloatField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField

def get_copropiedades():
        from app.models import Copropiedad
        return Copropiedad.query.order_by(Copropiedad.nombre).all()

class ExcelUploadForm(FlaskForm):
    excel_file = FileField('Archivo Excel', validators=[
        FileRequired(),
        FileAllowed(['xlsx'], 'Solo se permiten archivos Excel (.xlsx)')
    ])
    copropiedad = QuerySelectField('Copropiedad (para todos los registros)', 
                                  query_factory=get_copropiedades,
                                  get_label='nombre',
                                  validators=[DataRequired()])
    submit = SubmitField('Cargar Datos')

class LoginForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recuérdame')
    submit = SubmitField('Iniciar Sesión')

class UserForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    is_admin = BooleanField('Es Administrador')
    submit = SubmitField('Guardar')

class UserEditForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Contraseña', validators=[Optional(), Length(min=6)])
    is_admin = BooleanField('Es Administrador')
    submit = SubmitField('Actualizar')

class CopropiedadForm(FlaskForm):
    nombre = StringField('Nombre de la Copropiedad', validators=[DataRequired(), Length(max=200)])
    direccion = StringField('Dirección', validators=[DataRequired(), Length(max=255)])
    nit = StringField('NIT', validators=[Optional(), Length(max=20)])
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=50)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])
    numero_unidades = IntegerField('Número de Unidades Privadas', validators=[Optional(), NumberRange(min=1)])
    submit = SubmitField('Guardar Copropiedad')

class DataEntryForm(FlaskForm):
      
    copropiedad = QuerySelectField('Copropiedad', 
                                  query_factory=get_copropiedades,
                                  get_label='nombre',
                                  allow_blank=True,
                                  blank_text='-- Seleccione una Copropiedad --',
                                  validators=[Optional()])
    
    
    inmueble = StringField('Inmueble (Ej: Apto 101, Torre 1)', validators=[DataRequired(), Length(max=200)])
    modelo_choices = [
        ('individual', 'Individual'),
        ('principal', 'Principal'),
        ('dependiente', 'Dependiente')
    ]
    modelo = SelectField('Modelo', choices=modelo_choices, validators=[DataRequired()])

    agrupar_por_choices = [
        ('inmueble', 'Inmueble'),
        ('propietario', 'Propietario'),

    ]
    agrupar_por = SelectField('Agrupar Por', choices=agrupar_por_choices, validators=[DataRequired()])  
      
    principal = BooleanField('¿Es Inmueble Principal?')
    matricula = StringField('Matrícula Inmobiliaria', validators=[DataRequired(), Length(max=100)])
    telefono = StringField('Teléfono de Contacto', validators=[DataRequired(), Length(min=7, max=50)])
    coeficiente = FloatField('Coeficiente (Ej: 0.0123)', validators=[Optional(), NumberRange(min=0, max=1)])

    tipo_persona_choices = [('Natural', 'Persona Natural'), ('Jurídica', 'Persona Jurídica')]
    tipo_persona = SelectField('Tipo de Persona', choices=tipo_persona_choices, validators=[DataRequired()])
    
    primer_nombre = StringField('Primer Nombre', validators=[Optional(), Length(max=100)])
    segundo_nombre = StringField('Segundo Nombre', validators=[Optional(), Length(max=100)])
    primer_apellido = StringField('Primer Apellido', validators=[Optional(), Length(max=100)])
    segundo_apellido = StringField('Segundo Apellido', validators=[Optional(), Length(max=100)])
    razon_social = StringField('Razón Social (Para Persona Jurídica)', validators=[Optional(), Length(max=255)])

    tipo_id_choices = [
        ('CC', 'Cédula de Ciudadanía'),
        ('NIT', 'NIT'),
        ('CE', 'Cédula de Extranjería'),
        ('PAS', 'Pasaporte'),
        ('OTRO', 'Otro')
    ]
    tipo_id = SelectField('Tipo de Identificación', choices=tipo_id_choices, validators=[DataRequired()])
    identificacion = StringField('Número de Identificación', validators=[DataRequired(), Length(max=100)])
    dv = StringField('DV (Dígito de Verificación, para NIT)', validators=[Optional(), Length(max=1), Regexp(r'^\d?$', message="DV debe ser un solo dígito o vacío.")])
    
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email(), Length(max=120)])
    direccion = TextAreaField('Dirección Completa', validators=[DataRequired(), Length(max=255)])

    # Campos para calculos internos
    fecha_inicio_facturacion = DateField('Fecha Inicio Facturación', format='%Y-%m-%d', validators=[Optional()])
    fecha_ingreso = DateField('Fecha Ingreso', format='%Y-%m-%d', validators=[Optional()])
    periodo_de_gracia = FloatField('Periodo de Gracia (días)', validators=[Optional(), NumberRange(min=0)])
    valor_a_pagar_inmueble = DecimalField('Valor a Pagar Inmueble', validators=[Optional()], places=2)
    valor_presupuesto = DecimalField('Valor Presupuesto', validators=[Optional()], places=2)
    valor_a_pagar_constructora = DecimalField('Valor a Pagar Constructora', validators=[Optional()], places=2)
    valor_a_pagar_propietario = DecimalField('Valor a Pagar Propietario', validators=[Optional()], places=2)
    
    submit = SubmitField('Guardar Datos')

    def validate(self, extra_validators=None):
        # Validación condicional básica
        if not super().validate(extra_validators):
            return False
        if self.tipo_persona.data == 'Natural':
            if not self.primer_nombre.data or not self.primer_apellido.data:
                self.primer_nombre.errors.append('Primer nombre y apellido son requeridos para Persona Natural.')
                return False
        elif self.tipo_persona.data == 'Jurídica':
            if not self.razon_social.data:
                self.razon_social.errors.append('Razón Social es requerida para Persona Jurídica.')
                return False
        return True
    # Se incluyen formularios de usuario para la gestion de los usuarios.