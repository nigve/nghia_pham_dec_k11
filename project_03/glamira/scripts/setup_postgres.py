import subprocess

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        print(stdout.decode())
    else:
        print(stderr.decode())
        raise Exception(f"Command failed with exit code {process.returncode}")

def create_database():
    print("Creating database if not exists...")
    check_db_cmd = """
    sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='glamira'" | grep -q 1 || sudo -u postgres psql -c "CREATE DATABASE glamira;"
    """
    run_command(check_db_cmd)

def create_user():
    print("Creating user if not exists...")
    create_user_cmd = """
    sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='scrapy'" | grep -q 1 || sudo -u postgres psql -c "CREATE USER scrapy WITH ENCRYPTED PASSWORD 'password';"
    """
    run_command(create_user_cmd)

def grant_privileges():
    print("Granting privileges...")
    grant_privileges_cmd = """
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE glamira TO scrapy;"
    """
    run_command(grant_privileges_cmd)

def create_table():
    print("Creating table if not exists...")
    create_table_cmd = """
    sudo -u postgres psql -d glamira -c "
    CREATE TABLE IF NOT EXISTS images_metadata (
        id SERIAL PRIMARY KEY,
        response_url TEXT NOT NULL,
        product_url TEXT NOT NULL,
        product_name TEXT NOT NULL,
        lastmod TIMESTAMP,
        sku TEXT NOT NULL,
        image_url TEXT NOT NULL,
        view TEXT,
        womenstone TEXT,
        diamond TEXT,
        stone2 TEXT,
        stone3 TEXT,
        alloycolour TEXT,
        accent TEXT,
        wood TEXT,
        minio_path TEXT NOT NULL,
        UNIQUE (image_url),
        UNIQUE (minio_path)
    );
    "
    """
    run_command(create_table_cmd)
  
def grant_table_privileges():
    print("Granting table privileges...")
    grant_table_privileges_cmd = """
    sudo -u postgres psql -d glamira -c "GRANT ALL PRIVILEGES ON TABLE images_metadata TO scrapy;"
    """
    run_command(grant_table_privileges_cmd)

    print("Granting sequence privileges...")
    grant_seq_privileges_cmd = """
    sudo -u postgres psql -d glamira -c "GRANT ALL PRIVILEGES ON SEQUENCE images_metadata_id_seq TO scrapy;"
    """
    run_command(grant_seq_privileges_cmd)

if __name__ == "__main__":
    create_database()
    create_user()
    grant_privileges()
    create_table()
    grant_table_privileges()