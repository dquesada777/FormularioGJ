from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Añadir la columna numero_unidades a la tabla copropiedad
    inspector = db.inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('copropiedad')]
    
    if 'numero_unidades' not in columns:
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE copropiedad ADD COLUMN numero_unidades INTEGER'))
            conn.commit()
        print("Columna 'numero_unidades' añadida a la tabla 'copropiedad'")
    else:
        print("La columna 'numero_unidades' ya existe en la tabla 'copropiedad'")
    
    print("Base de datos actualizada correctamente")