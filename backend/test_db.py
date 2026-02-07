from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM users'))
    count = result.scalar()
    print(f"Usuarios en BD: {count}")
    
    # Verificar estructura de tabla
    result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users' ORDER BY ordinal_position"))
    columns = [row[0] for row in result.fetchall()]
    print(f"Columnas de users: {', '.join(columns[:10])}")
    print(f"Total de columnas: {len(columns)}")
