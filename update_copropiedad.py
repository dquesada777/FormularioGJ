from app import create_app, db
from app.models import Copropiedad
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Crear la tabla copropiedad si no existe
    db.create_all()
    
    # Añadir la columna copropiedad_id a la tabla propiedad_data si no existe
    inspector = db.inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('propiedad_data')]
    
    if 'copropiedad_id' not in columns:
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE propiedad_data ADD COLUMN copropiedad_id INTEGER'))
            conn.commit()
        print("Columna 'copropiedad_id' añadida a la tabla 'propiedad_data'")
    else:
        print("La columna 'copropiedad_id' ya existe en la tabla 'propiedad_data'")
    
    print("Base de datos actualizada correctamente")
