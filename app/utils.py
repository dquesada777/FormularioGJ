import openpyxl
from io import BytesIO
from .models import PropiedadData
import logging

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