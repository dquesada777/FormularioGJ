from app import create_app, db
from app.models import PropiedadData
import openpyxl
from io import BytesIO
import os

app = create_app()

with app.app_context():
    # Verificar si hay datos en la base de datos
    propiedades = PropiedadData.query.all()
    print(f"Número de registros encontrados: {len(propiedades)}")
    
    if propiedades:
        # Crear un archivo Excel directamente en el sistema de archivos
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Datos de Propiedades"
        
        # Encabezados
        headers = [
            "ID", "Inmueble", "Modelo", "Principal", "Agrupar Por", "Matrícula", 
            "Teléfono", "Coeficiente", "Tipo Persona", "Primer Nombre", "Segundo Nombre",
            "Primer Apellido", "Segundo Apellido", "Razón Social", "Tipo ID", 
            "Identificación", "DV", "Email", "Dirección"
        ]
        sheet.append(headers)
        
        # Datos
        for prop in propiedades:
            try:
                row = [
                    prop.id, prop.inmueble, prop.modelo, prop.principal, prop.agrupar_por, prop.matricula,
                    prop.telefono, prop.coeficiente, prop.tipo_persona, prop.primer_nombre, prop.segundo_nombre,
                    prop.primer_apellido, prop.segundo_apellido, prop.razon_social, prop.tipo_id,
                    prop.identificacion, prop.dv, prop.email, prop.direccion
                ]
                sheet.append(row)
                print(f"Agregado registro ID: {prop.id}")
            except Exception as e:
                print(f"Error al procesar registro ID {prop.id}: {str(e)}")
        
        # Guardar el archivo en el directorio actual
        file_path = os.path.join(os.getcwd(), "datos_propiedades_debug.xlsx")
        workbook.save(file_path)
        print(f"Archivo Excel guardado en: {file_path}")
    else:
        print("No hay datos para exportar a Excel.")
