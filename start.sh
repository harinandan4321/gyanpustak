#!/bin/bash
set -e

MYSQL_DATA=/home/runner/mysql_data
MYSQL_SOCKET=/run/mysqld/mysqld.sock

mkdir -p /run/mysqld

# Start MySQL if not running
if ! mysqladmin --socket=$MYSQL_SOCKET -u root status 2>/dev/null; then
    echo "Starting MySQL..."
    if [ ! -d "$MYSQL_DATA/mysql" ]; then
        echo "Initializing MySQL data directory..."
        mysqld --initialize-insecure --user=runner --datadir=$MYSQL_DATA 2>&1
    fi
    mysqld --user=runner --datadir=$MYSQL_DATA --socket=$MYSQL_SOCKET \
           --bind-address=127.0.0.1 --port=3306 --daemonize=ON \
           --pid-file=/home/runner/mysqld.pid 2>&1
    sleep 5
    echo "MySQL started"
fi

# Run schema setup if not already done
DB_EXISTS=$(mysql --socket=$MYSQL_SOCKET -u root -e "SHOW DATABASES LIKE 'gyanpustak';" 2>/dev/null | grep gyanpustak || true)
if [ -z "$DB_EXISTS" ]; then
    echo "Creating database schema..."
    mysql --socket=$MYSQL_SOCKET -u root < /home/runner/workspace/flask_app/db_setup.sql
    echo "Seeding data..."
    python3 /home/runner/workspace/flask_app/seed.py
fi

# Start Flask app
echo "Starting Flask application..."
cd /home/runner/workspace/flask_app
exec python3 app.py
