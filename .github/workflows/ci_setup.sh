sudo apt-get update
sudo apt-get install postgresql postgresql-contrib -y
sudo service postgresql start
sudo -u postgres psql -c "CREATE DATABASE appdb;"
sudo -u postgres psql -c "CREATE USER umair WITH PASSWORD 'umair';"
sudo -u postgres psql -c "ALTER ROLE umair SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE umair SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE umair SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE appdb TO umair;"
sudo service postgresql restart