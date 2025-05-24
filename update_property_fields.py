# update_property_fields.py
from app import create_app, db
from sqlalchemy import Column, Float, Date, Integer, text

app = create_app()

with app.app_context():
    # Verificar y añadir las nuevas columnas
    inspector = db.inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('propiedad_data')]
    
    # Lista de columnas a añadir con sus tipos
    new_columns = {
        'fecha_inicio_facturacion': 'DATE',
        'fecha_ingreso': 'DATE',
        'periodo_de_gracia': 'INTEGER',
        'valor_a_pagar_inmueble': 'FLOAT',
        'valor_presupuesto': 'FLOAT',
        'valor_a_pagar_constructora': 'FLOAT',
        'valor_a_pagar_propietario': 'FLOAT'
    }
    
    with db.engine.connect() as conn:
        for col_name, col_type in new_columns.items():
            if col_name not in columns:
                conn.execute(text(f'ALTER TABLE propiedad_data ADD COLUMN {col_name} {col_type}'))
                print(f"Columna '{col_name}' añadida a la tabla 'propiedad_data'")
        conn.commit()
    
    print("Base de datos actualizada correctamente")
