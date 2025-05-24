from app import create_app, db
from app.models import User
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Verificar si la columna is_admin ya existe
    inspector = db.inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('user')]
    
    if 'is_admin' not in columns:
        # Agregar la columna is_admin usando la sintaxis actualizada
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0'))
            conn.commit()
        print("Columna 'is_admin' agregada a la tabla 'user'")
        
        # Hacer que el usuario existente sea administrador
        admin = User.query.filter_by(username='admin_gestion').first()
        if admin:
            admin.is_admin = True
            db.session.commit()
            print(f"Usuario '{admin.username}' actualizado como administrador")
    else:
        print("La columna 'is_admin' ya existe en la tabla 'user'")
