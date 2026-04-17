"""
GyanPustak Startup Script
- Starts MySQL (if not already running)
- Creates DB schema (if not exists)
- Seeds demo data (if DB is empty)
- Starts Flask app
"""
import os
import sys
import time
import subprocess
import socket

MYSQL_DATA = '/home/runner/mysql_data'
MYSQL_SOCKET = '/run/mysqld/mysqld.sock'

def is_mysql_running():
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            unix_socket=MYSQL_SOCKET,
            user='hari',
            password='password',
            connection_timeout=2,
        )
        conn.close()
        return True
    except Exception:
        return False

def start_mysql():
    os.makedirs('/run/mysqld', exist_ok=True)
    if not os.path.exists(os.path.join(MYSQL_DATA, 'mysql')):
        print("Initializing MySQL data directory...")
        subprocess.run([
            'mysqld', '--initialize-insecure',
            '--user=runner',
            f'--datadir={MYSQL_DATA}',
        ], check=True, capture_output=True)

    for f in [MYSQL_SOCKET, MYSQL_SOCKET + '.lock']:
        if os.path.exists(f):
            os.remove(f)

    print("Starting MySQL server...")
    proc = subprocess.Popen([
        'mysqld_safe',
        '--user=runner',
        f'--datadir={MYSQL_DATA}',
        f'--socket={MYSQL_SOCKET}',
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for i in range(30):
        time.sleep(1)
        if is_mysql_running():
            print("MySQL started successfully.")
            return True
        print(f"Waiting for MySQL... ({i+1}/30)")
    return False

def setup_database():
    import mysql.connector
    conn = mysql.connector.connect(
        unix_socket=MYSQL_SOCKET,
        user='root',
        password='',
    )
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES LIKE 'gyanpustak'")
    exists = cursor.fetchone()
    if not exists:
        print("Creating database schema...")
        schema_path = os.path.join(os.path.dirname(__file__), 'db_setup.sql')
        with open(schema_path, 'r') as f:
            sql = f.read()
        for statement in sql.split(';'):
            stmt = statement.strip()
            if stmt:
                try:
                    cursor.execute(stmt)
                    conn.commit()
                except Exception as e:
                    print(f"Warning: {e}")
        print("Running seed data...")
        cursor.close()
        conn.close()
        sys.path.insert(0, os.path.dirname(__file__))
        import seed
        seed.seed()
    else:
        print("Database already exists, skipping setup.")
        cursor.close()
        conn.close()

if __name__ == '__main__':
    if not is_mysql_running():
        if not start_mysql():
            print("ERROR: Could not start MySQL!")
            sys.exit(1)

    setup_database()

    print("Starting Flask application...")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.environ['MYSQL_SOCKET'] = MYSQL_SOCKET
    from app import app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
