SELECT 'CREATE DATABASE flight_data'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'flight_data')\gexec
