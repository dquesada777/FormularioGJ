from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from .forms import LoginForm, DataEntryForm, CopropiedadForm, UserForm, UserEditForm, ExcelUploadForm, ReportForm, AdminReportForm
from .models import User, PropiedadData, Copropiedad
from . import db
from .utils import generate_excel_file, process_excel_upload, generate_pdf_report, generate_filtered_excel_report  # Importar la función de utilidad
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
import io
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import calendar

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
@login_required
def index():
    form = DataEntryForm()
    return render_template('data_form.html', title='Ingreso de Datos Generales', form=form)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login fallido. Verifica tu usuario y contraseña.', 'danger')
    return render_template('login.html', title='Iniciar Sesión', form=form)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('main.login'))

@main_bp.route('/submit_data', methods=['GET', 'POST'])
@login_required
def submit_data():
    form = DataEntryForm()
    if form.validate_on_submit():
        try:
             # Realizar cálculos en el servidor para asegurar la integridad de los datos
            fecha_ingreso = form.fecha_ingreso.data
            periodo_gracia = form.periodo_de_gracia.data
            fecha_inicio_facturacion = form.fecha_inicio_facturacion.data
            
            # Calcular fecha_inicio_facturacion si no está establecida
            if fecha_ingreso and periodo_gracia and not fecha_inicio_facturacion:
                from datetime import timedelta
                fecha_inicio_facturacion = fecha_ingreso + timedelta(days=periodo_gracia)
                form.fecha_inicio_facturacion.data = fecha_inicio_facturacion
            
            # Calcular valor_a_pagar_inmueble si no está establecido
            coeficiente = form.coeficiente.data
            valor_presupuesto = form.valor_presupuesto.data
            valor_a_pagar_inmueble = form.valor_a_pagar_inmueble.data
            
            if coeficiente and valor_presupuesto and not valor_a_pagar_inmueble:
                valor_a_pagar_inmueble = (valor_presupuesto * coeficiente) / 100
                form.valor_a_pagar_inmueble.data = valor_a_pagar_inmueble
            
            # Calcular valor_a_pagar_constructora si no está establecido
            if fecha_ingreso and fecha_inicio_facturacion and valor_a_pagar_inmueble and not form.valor_a_pagar_constructora.data:
                from datetime import timedelta
                # Restar un día a la fecha de inicio de facturación
                fecha_inicio_facturacion_menos_1 = fecha_inicio_facturacion - timedelta(days=1)
                dias = (fecha_inicio_facturacion_menos_1 - fecha_ingreso).days
                valor_a_pagar_constructora = (valor_a_pagar_inmueble / 30) * dias
                form.valor_a_pagar_constructora.data = valor_a_pagar_constructora
            
            # Calcular valor_a_pagar_propietario si no está establecido
            if valor_a_pagar_inmueble and form.valor_a_pagar_constructora.data and not form.valor_a_pagar_propietario.data:
                valor_a_pagar_propietario = valor_a_pagar_inmueble - form.valor_a_pagar_constructora.data
                form.valor_a_pagar_propietario.data = valor_a_pagar_propietario

            nueva_propiedad = PropiedadData(
                inmueble=form.inmueble.data,
                modelo=form.modelo.data,
                principal=form.principal.data,
                agrupar_por=form.agrupar_por.data,
                matricula=form.matricula.data,
                telefono=form.telefono.data,
                coeficiente=form.coeficiente.data,
                tipo_persona=form.tipo_persona.data,
                primer_nombre=form.primer_nombre.data if form.tipo_persona.data == 'Natural' else None,
                segundo_nombre=form.segundo_nombre.data if form.tipo_persona.data == 'Natural' else None,
                primer_apellido=form.primer_apellido.data if form.tipo_persona.data == 'Natural' else None,
                segundo_apellido=form.segundo_apellido.data if form.tipo_persona.data == 'Natural' else None,
                razon_social=form.razon_social.data if form.tipo_persona.data == 'Jurídica' else None,
                tipo_id=form.tipo_id.data,
                identificacion=form.identificacion.data,
                dv=form.dv.data,
                email=form.email.data,
                direccion=form.direccion.data,
                fecha_inicio_facturacion=form.fecha_inicio_facturacion.data,
                fecha_ingreso=form.fecha_ingreso.data,
                periodo_de_gracia=form.periodo_de_gracia.data,
                valor_a_pagar_inmueble=form.valor_a_pagar_inmueble.data,
                valor_presupuesto=form.valor_presupuesto.data,
                valor_a_pagar_constructora=form.valor_a_pagar_constructora.data,
                valor_a_pagar_propietario=form.valor_a_pagar_propietario.data,
            )   
            if form.copropiedad.data:
                nueva_propiedad.copropiedad_id = form.copropiedad.data.id
                            
            db.session.add(nueva_propiedad)
            db.session.commit()
            flash('¡Datos de propiedad guardados exitosamente!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar los datos: {str(e)}', 'danger')
            # Considera loggear el error 'e' para depuración
    else:
        # Si el formulario no es válido, los errores se mostrarán en la plantilla
        flash('Por favor, corrige los errores en el formulario.', 'warning')
    return render_template('data_form.html', title='Ingreso de Datos Generales', form=form)

# Nueva ruta para gestionar copropiedades

@main_bp.route('/copropiedades')
@login_required
def list_copropiedades():
    if not check_admin():
         flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
         return redirect(url_for('main.index'))
    
     # Obtener el límite de registros a mostrar
    limit = request.args.get('limit', 20, type=int)  # Por defecto 20 registros

    copropiedades = Copropiedad.query.limit(limit).all()
    return render_template('copropiedades/list.html', title='Copropiedades', copropiedades=copropiedades, limit=limit)

@main_bp.route('/copropiedades/new', methods=['GET', 'POST'])
@login_required
def new_copropiedad():
    if not check_admin():
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return redirect(url_for('main.index'))
    form = CopropiedadForm()
    if form.validate_on_submit():
        copropiedad = Copropiedad(
            nombre=form.nombre.data,
            direccion=form.direccion.data,
            nit=form.nit.data,
            telefono=form.telefono.data,
            email=form.email.data,
            numero_unidades=form.numero_unidades.data
        )
        db.session.add(copropiedad)
        db.session.commit()
        flash(f'Copropiedad {copropiedad.nombre} creada exitosamente.', 'success')
        return redirect(url_for('main.list_copropiedades'))
    return render_template('copropiedades/form.html', title='Nueva Copropiedad', form=form)

@main_bp.route('/copropiedades/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_copropiedad(id):
    if not check_admin():
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return redirect(url_for('main.index'))
    copropiedad = Copropiedad.query.get_or_404(id)
    form = CopropiedadForm(obj=copropiedad)
    if form.validate_on_submit():
        copropiedad.nombre = form.nombre.data
        copropiedad.direccion = form.direccion.data
        copropiedad.nit = form.nit.data
        copropiedad.telefono = form.telefono.data
        copropiedad.email = form.email.data
        copropiedad.numero_unidades = form.numero_unidades.data
        db.session.commit()
        flash(f'Copropiedad {copropiedad.nombre} actualizada exitosamente.', 'success')
        return redirect(url_for('main.list_copropiedades'))
    return render_template('copropiedades/form.html', title='Editar Copropiedad', form=form)

@main_bp.route('/copropiedades/delete/<int:id>', methods=['POST'])
@login_required
def delete_copropiedad(id):
    if not check_admin():
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return redirect(url_for('main.index'))
    
    copropiedad = Copropiedad.query.get_or_404(id)
    
    # Verificar si hay propiedades asociadas a esta copropiedad
    propiedades_asociadas = PropiedadData.query.filter_by(copropiedad_id=id).count()
    if propiedades_asociadas > 0:
        flash(f'No se puede eliminar la copropiedad "{copropiedad.nombre}" porque tiene {propiedades_asociadas} inmuebles asociados.', 'danger')
        return redirect(url_for('main.list_copropiedades'))
    
    try:
        nombre = copropiedad.nombre
        db.session.delete(copropiedad)
        db.session.commit()
        flash(f'Copropiedad "{nombre}" eliminada exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la copropiedad: {str(e)}', 'danger')
    
    return redirect(url_for('main.list_copropiedades'))

@main_bp.route('/propiedades')
@login_required
def list_propiedades():
    # Obtener parámetros de búsqueda y paginación
    copropiedad_id = request.args.get('copropiedad_id', type=int)
    search_term = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)  # Por defecto 20 registros por página
    
    # Construir la consulta base
    query = PropiedadData.query
    
    # Filtrar por copropiedad si se especificó
    if copropiedad_id:
        query = query.filter_by(copropiedad_id=copropiedad_id)

        # Filtrar por término de búsqueda si se proporcionó
    if search_term:
        query = query.filter(PropiedadData.inmueble.ilike(f'%{search_term}%'))
    
     # Paginar los resultados
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    propiedades = pagination.items
    
    # Obtener todas las copropiedades para el selector
    copropiedades = Copropiedad.query.all()
    
    return render_template(
        'propiedades/list.html', 
        title='Listado de Inmuebles', 
        propiedades=propiedades,
        copropiedades=copropiedades,
        copropiedad_id=copropiedad_id,
        search_term=search_term,
        pagination=pagination,
        per_page=per_page
    )

@main_bp.route('/propiedades/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_propiedad(id):
    propiedad = PropiedadData.query.get_or_404(id)
    form = DataEntryForm(obj=propiedad)
      
   # Si la propiedad tiene una copropiedad asignada, seleccionarla en el formulario
    if propiedad.copropiedad:
        form.copropiedad.data = propiedad.copropiedad

    # Para usuarios no administradores, solo permitir editar ciertos campos
    is_admin = current_user.is_admin
    
    if form.validate_on_submit():
        try:
            # Si es administrador, actualizar todos los campos
            if is_admin:
                propiedad.inmueble = form.inmueble.data
                propiedad.modelo = form.modelo.data
                propiedad.principal = form.principal.data
                propiedad.agrupar_por = form.agrupar_por.data
                propiedad.matricula = form.matricula.data
                propiedad.telefono = form.telefono.data
                propiedad.coeficiente = form.coeficiente.data
                propiedad.tipo_persona = form.tipo_persona.data

                # Información del propietario/responsable
                if form.tipo_persona.data == 'Natural':
                    propiedad.primer_nombre = form.primer_nombre.data
                    propiedad.segundo_nombre = form.segundo_nombre.data
                    propiedad.primer_apellido = form.primer_apellido.data
                    propiedad.segundo_apellido = form.segundo_apellido.data
                    propiedad.razon_social = None
                else:
                    propiedad.primer_nombre = None
                    propiedad.segundo_nombre = None
                    propiedad.primer_apellido = None
                    propiedad.segundo_apellido = None
                    propiedad.razon_social = form.razon_social.data

                # Identificación y contacto
                propiedad.tipo_id = form.tipo_id.data
                propiedad.identificacion = form.identificacion.data
                propiedad.dv = form.dv.data
                propiedad.email = form.email.data
                propiedad.direccion = form.direccion.data

                # Actualizar la copropiedad si se seleccionó una
                if form.copropiedad.data:
                    propiedad.copropiedad_id = form.copropiedad.data.id
            
                    # Para todos los usuarios (incluyendo no administradores)
                    # Información financiera (solo fecha_ingreso y periodo_de_gracia para no administradores)
                    propiedad.fecha_ingreso = form.fecha_ingreso.data
                    propiedad.periodo_de_gracia = form.periodo_de_gracia.data
            
            # Solo administradores pueden editar estos campos
            if is_admin:
                propiedad.fecha_inicio_facturacion = form.fecha_inicio_facturacion.data
                propiedad.valor_presupuesto = form.valor_presupuesto.data
                propiedad.valor_a_pagar_inmueble = form.valor_a_pagar_inmueble.data
                propiedad.valor_a_pagar_constructora = form.valor_a_pagar_constructora.data
                propiedad.valor_a_pagar_propietario = form.valor_a_pagar_propietario.data

            db.session.commit()
            flash(f'Inmueble {propiedad.inmueble} actualizado exitosamente.', 'success')
            return redirect(url_for('main.list_propiedades'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar los datos: {str(e)}', 'danger')
    
    return render_template('propiedades/edit.html', title='Editar Inmueble', form=form, propiedad=propiedad, is_admin=is_admin)

@main_bp.route('/download_excel_data')
@login_required
def download_excel_data():
    try:
        # Verificar si hay datos para exportar
        if PropiedadData.query.count() == 0:
            flash('No hay datos disponibles para exportar a Excel.', 'warning')
            return redirect(url_for('main.index'))
            
        # Generar el archivo Excel
        excel_data_stream = generate_excel_file()
        
        return send_file(
            excel_data_stream,
            as_attachment=True,
            download_name='datos_propiedades.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        import traceback
        traceback.print_exc()  # Imprimir el error completo en la consola
        flash(f'Error al generar el archivo Excel: {str(e)}', 'danger')
        return redirect(url_for('main.index'))


# Ruta para crear un usuario de prueba (solo para desarrollo)
@main_bp.route('/crear_usuario_admin_test_gestion')
def crear_usuario_admin_test_gestion():
    if not User.query.filter_by(username='admin_gestion').first():
        admin_user = User(username='admin_gestion', is_admin=True) #Ahora es admin
        admin_user.set_password('adminpass123') # Cambia esta contraseña
        db.session.add(admin_user)
        db.session.commit()
        return "Usuario 'admin_gestion' creado con contraseña 'adminpass123'. Por favor, cámbiala."
    return "El usuario 'admin_gestion' ya existe."
# Función auxiliar para verificar si el usuario actual es administrador
def check_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return False
    return True

@main_bp.route('/users')
@login_required
def list_users():
    if not check_admin():
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    return render_template('users/list.html', title='Gestión de Usuarios', users=users)

@main_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
def new_user():
    if not check_admin():
        return redirect(url_for('main.index'))
    
    form = UserForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash(f'El usuario {form.username.data} ya existe.', 'danger')
            return render_template('users/form.html', title='Nuevo Usuario', form=form)
        
        user = User(username=form.username.data, is_admin=form.is_admin.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Usuario {user.username} creado exitosamente.', 'success')
        return redirect(url_for('main.list_users'))
    
    return render_template('users/form.html', title='Nuevo Usuario', form=form)

@main_bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if not check_admin():
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(id)
    form = UserEditForm(obj=user)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.is_admin = form.is_admin.data
        
        if form.password.data:  # Solo actualizar la contraseña si se proporciona una nueva
            user.set_password(form.password.data)
        
        db.session.commit()
        flash(f'Usuario {user.username} actualizado exitosamente.', 'success')
        return redirect(url_for('main.list_users'))
    
    return render_template('users/form.html', title='Editar Usuario', form=form, user=user)

@main_bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if not check_admin():
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(id)
    
    # No permitir eliminar al usuario actual
    if user.id == current_user.id:
        flash('No puedes eliminar tu propio usuario.', 'danger')
        return redirect(url_for('main.list_users'))
    
    db.session.delete(user)
    db.session.commit()
    flash(f'Usuario {user.username} eliminado exitosamente.', 'success')
    return redirect(url_for('main.list_users'))

@main_bp.route('/upload_excel', methods=['GET', 'POST'])
@login_required
def upload_excel():
    form = ExcelUploadForm()
    if form.validate_on_submit():
        try:
            # Procesar el archivo Excel
            result = process_excel_upload(form.excel_file.data, form.copropiedad.data.id)
            
            if result['errors'] > 0:
                flash(f'Se encontraron {result["errors"]} errores durante la carga. {result["processed"]} registros procesados correctamente.', 'warning')
                for error in result['error_messages']:
                    flash(error, 'danger')
            else:
                flash(f'Carga exitosa. {result["processed"]} registros añadidos a la base de datos.', 'success')
            
            return redirect(url_for('main.upload_excel'))
        except Exception as e:
            flash(f'Error al procesar el archivo: {str(e)}', 'danger')
    
    return render_template('upload_excel.html', title='Carga Masiva de Datos', form=form)

@main_bp.route('/report', methods=['GET', 'POST'])
@login_required
def generate_report():
    form = ReportForm()

    # Obtener todas las copropiedades para el campo de búsqueda
    copropiedades = Copropiedad.query.order_by(Copropiedad.nombre).all()

    if form.validate_on_submit():
        try:
            # Generar el reporte PDF
            pdf_stream = generate_pdf_report(form.copropiedad.data.id) 
            
            # Nombre del archivo
            filename = f"reporte_{form.copropiedad.data.nombre.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            return send_file(
                pdf_stream,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )
        except Exception as e:
            flash(f'Error al generar el reporte: {str(e)}', 'danger')
    
    return render_template('report_form.html', title='Generar Reporte de Inmuebles', form=form, copropiedades=copropiedades)

@main_bp.route('/admin_report', methods=['GET', 'POST'])
@login_required
def admin_report():
    # Verificar si el usuario es administrador
    if not check_admin():
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return redirect(url_for('main.index'))
    
    form = AdminReportForm()
    if form.validate_on_submit():
        try:
            # Obtener los parámetros del formulario
            copropiedad_id = form.copropiedad.data.id if form.copropiedad.data else None
            year = int(form.year.data)
            month = int(form.month.data)
            
            # Si se proporcionó un valor de presupuesto, actualizar todos los inmuebles
            if form.valor_presupuesto.data:
                # Construir la consulta base
                query = PropiedadData.query
                
                # Filtrar por copropiedad si se especificó
                if copropiedad_id:
                    query = query.filter_by(copropiedad_id=copropiedad_id)
                
                # Actualizar el valor del presupuesto y recalcular los valores
                propiedades = query.all()
                for prop in propiedades:
                    prop.valor_presupuesto = int(form.valor_presupuesto.data)
                    # Recalcular valor_a_pagar_inmueble basado en el coeficiente
                    if prop.coeficiente:
                        # Aplicar la fórmula correcta: (Valor_presupuesto * coeficiente)/100
                        prop.valor_a_pagar_inmueble = int((float(form.valor_presupuesto.data) * prop.coeficiente) / 100)
                        # Recalcular valor_a_pagar_propietario y valor_a_pagar_constructora
                        if prop.fecha_inicio_facturacion:
                            # Obtener el día del mes de la fecha de inicio de facturación
                            dia_facturacion = prop.fecha_inicio_facturacion.day
                            # Calcular el valor a pagar a la constructora: (valor inmueble / 30) * (día facturación - 1)
                            prop.valor_a_pagar_constructora = int((prop.valor_a_pagar_inmueble / 30) * (dia_facturacion - 1))
                            prop.valor_a_pagar_propietario = int(prop.valor_a_pagar_inmueble - prop.valor_a_pagar_constructora)
                
                # Guardar los cambios en la base de datos
                db.session.commit()
                flash(f'Valor de presupuesto actualizado y recálculos realizados exitosamente.', 'success')
            
            # Generar el reporte Excel
            excel_stream = generate_filtered_excel_report(copropiedad_id, year, month)
            
            # Nombre del archivo
            copropiedad_nombre = form.copropiedad.data.nombre if form.copropiedad.data else "todas"
            month_name = calendar.month_name[month]
            filename = f"reporte_financiero_{copropiedad_nombre}_{month_name}_{year}.xlsx"
            
            return send_file(
                excel_stream,
                as_attachment=True,
                download_name=filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        except Exception as e:
            db.session.rollback()
            flash(f'Error al generar el reporte: {str(e)}', 'danger')
    
    return render_template('admin_report.html', title='Reporte Financiero', form=form)