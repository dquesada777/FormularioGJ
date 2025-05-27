import openpyxl
from io import BytesIO
from .models import PropiedadData
import logging
from app.models import PropiedadData, Copropiedad
from app import db
from datetime import datetime

def generate_excel_file():
    """Genera un archivo Excel con los datos de PropiedadData."""
    
    try:
        # Obtener todos los registros de la base de datos
        propiedades = PropiedadData.query.all()
        
        # Crear un nuevo libro de trabajo de Excel
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Datos de Propiedades"

        # Encabezados
        headers = [
            "ID", "Copropiedad", "Inmueble", "Modelo", "Principal", "Agrupar Por", "Matrícula", 
            "Teléfono", "Coeficiente", "Tipo Persona", "Primer Nombre", "Segundo Nombre",
            "Primer Apellido", "Segundo Apellido", "Razón Social", "Tipo ID", 
            "Identificación", "DV", "Email", "Dirección", "Fecha Inicio Facturación", 
            "Fecha Ingreso", "Periodo de Gracia", "Valor a Pagar Inmueble", "Valor Presupuesto", 
            "Valor a Pagar Constructora", "Valor a Pagar Propietario"
        ]
        sheet.append(headers)

        # Datos
        for prop in propiedades:

            copropiedad_nombre = prop.copropiedad.nombre if prop.copropiedad else "No asignada"

            row = [
                prop.id, copropiedad_nombre,prop.inmueble, prop.modelo, prop.principal, prop.agrupar_por, prop.matricula,
                prop.telefono, prop.coeficiente, prop.tipo_persona, prop.primer_nombre, prop.segundo_nombre,
                prop.primer_apellido, prop.segundo_apellido, prop.razon_social, prop.tipo_id,
                prop.identificacion, prop.dv, prop.email, prop.direccion, prop.fecha_inicio_facturacion,
                prop.fecha_ingreso, prop.periodo_de_gracia, prop.valor_a_pagar_inmueble, prop.valor_presupuesto,
                prop.valor_a_pagar_constructora, prop.valor_a_pagar_propietario
            ]
            sheet.append(row)

         # Ajustar el ancho de las columnas para mejor visualización
        for col in sheet.columns:
            max_length = 0
            column = col[0].column_letter  # Obtener la letra de la columna
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            adjusted_width = (max_length + 2)
            sheet.column_dimensions[column].width = adjusted_width

        # Guardar el libro de trabajo en un stream de bytes en memoria
        excel_stream = BytesIO()
        workbook.save(excel_stream)
        excel_stream.seek(0)  # Mover el cursor al inicio del stream

        return excel_stream
        
    except Exception as e:
        # Registrar el error para depuración
        logging.error(f"Error al generar el archivo Excel: {str(e)}")
        # Re-lanzar la excepción para que sea manejada por la ruta
        raise

def process_excel_upload(file_stream, copropiedad_id):
    """Procesa un archivo Excel y carga los datos en la base de datos."""

    workbook = openpyxl.load_workbook(file_stream)
    sheet = workbook.active
    
    # Obtener los encabezados (primera fila)
    headers = [cell.value for cell in sheet[1]]
    
    # Contador de registros procesados y errores
    processed = 0
    errors = 0
    error_messages = []
    
    # Procesar cada fila (excepto la primera que son los encabezados)
    for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), 2):
        try:
            # Crear un diccionario con los datos de la fila
            data = dict(zip(headers, row))
            
            # Verificar si la matrícula ya existe
            if PropiedadData.query.filter_by(matricula=data.get('Matrícula')).first():
                error_messages.append(f"Fila {row_idx}: La matrícula {data.get('Matrícula')} ya existe.")
                errors += 1
                continue
                
            # Crear un nuevo objeto PropiedadData
            nueva_propiedad = PropiedadData(
                copropiedad_id=copropiedad_id,
                inmueble=data.get('Inmueble', ''),
                modelo=data.get('Modelo', 'individual'),
                principal=data.get('Principal', False),
                agrupar_por=data.get('Agrupar Por', 'inmueble'),
                matricula=data.get('Matrícula', ''),
                telefono=data.get('Teléfono', ''),
                coeficiente=float(data.get('Coeficiente', 0) or 0),
                tipo_persona=data.get('Tipo Persona', 'Natural'),
                primer_nombre=data.get('Primer Nombre'),
                segundo_nombre=data.get('Segundo Nombre'),
                primer_apellido=data.get('Primer Apellido'),
                segundo_apellido=data.get('Segundo Apellido'),
                razon_social=data.get('Razón Social'),
                tipo_id=data.get('Tipo ID', 'CC'),
                identificacion=data.get('Identificación', ''),
                dv=data.get('DV', ''),
                email=data.get('Email', ''),
                direccion=data.get('Dirección', ''),
                fecha_inicio_facturacion=datetime.strptime(data.get('Fecha Inicio Facturación'), '%Y-%m-%d').date() if data.get('Fecha Inicio Facturación') else None,
                fecha_ingreso=datetime.strptime(data.get('Fecha Ingreso'), '%Y-%m-%d').date() if data.get('Fecha Ingreso') else None,
                periodo_de_gracia=int(data.get('Periodo de Gracia', 0) or 0),
                valor_a_pagar_inmueble=float(data.get('Valor a Pagar Inmueble', 0) or 0),
                valor_presupuesto=float(data.get('Valor Presupuesto', 0) or 0),
                valor_a_pagar_constructora=float(data.get('Valor a Pagar Constructora', 0) or 0),
                valor_a_pagar_propietario=float(data.get('Valor a Pagar Propietario', 0) or 0)
            )
            
            db.session.add(nueva_propiedad)
            processed += 1
            
        except Exception as e:
            errors += 1
            error_messages.append(f"Fila {row_idx}: {str(e)}")
    
    # Commit solo si no hubo errores
    if errors == 0:
        db.session.commit()
    else:
        db.session.rollback()
    
    return {
        'processed': processed,
        'errors': errors,
        'error_messages': error_messages
    }   