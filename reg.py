# Importing necessary modules
import pymysql
from flask import Flask, render_template, request
import CloudFlare
import os
import dotenv

# Defining Flask application
app = Flask(__name__)

# Setting up MySQL connection
conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password="",
    db='',
)

# Initializing Cloudflare client
API_KEY = ''
cf = CloudFlare.CloudFlare(
    email="@gmail.com",
    token=API_KEY
)

# Route for user registration
@app.route('/reg', methods=['POST'])
def register():
    # Receiving user's data from the form
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    subdomain = request.form['subdomain']
    
    # Checking if user already exists in the database
    query = f"SELECT 1 FROM Users.Users WHERE email = %s OR username = %s OR subdomain = %s"
    conn.ping()  # Reconnecting MySQL
    with conn.cursor() as cursor:
        cursor.execute(query, (email, username, subdomain))
        existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return "User exists"
    else:
        # If user doesn't exist, insert user data into the database
        query = f"INSERT INTO Users.Users (email, username, password, subdomain) VALUES (%s, %s, %s, %s)"
        conn.ping()  # Reconnecting MySQL
        with conn.cursor() as cursor:
            cursor.execute(query, (email, username, password, subdomain))
            conn.commit()  # Commit the transaction
            conn.close()

        # Setting up Cloudflare DNS record for the subdomain
        headers = {
            'Authorization': 'Bearer {}'.format(API_KEY),
            'Content-Type': 'application/json'
        }
        hostname = subdomain + ".domain.ao"
        zone = ".".join(hostname.split(".")[-2:])
        zones = cf.zones.get(params={"name": zone})
        if len(zones) == 0:
            print(f"Could not find CloudFlare zone {zone}, please check domain {hostname}")
            return "Could not find CloudFlare zone, please check the domain"
        ZONE_ID = zones[0]["id"]
        a_records = cf.zones.dns_records.get(ZONE_ID, params={"name": subdomain, "type": "A"})
        if len(a_records):
            return "Subdomain already exists."
        else:
            # If subdomain doesn't exist, create DNS record and set up Apache configuration
            print("Record doesn't exist, creating new record...")
            a_record = {
                "type": "A",
                "name": subdomain,
                "ttl": 1,
                "content": "0.0.0.0"
            }
            # Apache virtual host configuration
            vh = f"""
                <VirtualHost {subdomain}.domain.ao:80>
                    DocumentRoot "/var/www/html/{subdomain}/public"
                    <Directory /var/www/html/{subdomain}/public>
                        Order allow,deny
                        Allow from all
                        Require all granted
                    </Directory>
                </VirtualHost>
            """
            # Execute MySQL queries and copy files to set up new Laravel instance
            query1 = f"mysql -u root -p'' -e 'CREATE DATABASE IF NOT EXISTS laravel;'"
            query2 = f"mysql -u root -p'' laravel < laravel_dump.sql;"
            query3 = f"mysqldump -u root -p'' laravel > laravel_tables.sql;"
            query4 = f"mysql -u root -p'' -e 'CREATE DATABASE IF NOT EXISTS {subdomain};'"
            query5 = f"mysql -u root -p'' {subdomain} < laravel_tables.sql;"
            os.system(query1)
            os.system(query2)
            os.system(query3)
            os.system(query4)
            os.system(query5)
            os.system(f"cp -r ErpLite /var/www/html/{subdomain}")
            os.system(f"chmod -R a+rwx /var/www/html/{subdomain}")
            # Create Apache site configuration file
            cf.zones.dns_records.post(ZONE_ID, data=a_record)
            directory = "/etc/apache2/sites-available/"
            with open(f"{directory}{subdomain}.domain.ao.conf", "w") as file:
                file.write(vh)

            # Load existing variables from the .env file if it exists
            if os.path.exists(".env"):
                dotenv.load_dotenv(".env")
                
            # Update or add the new variables
            with open(".env", "a") as file:
                file.write(f"\nDB_DATABASE={subdomain}\n")
                file.write(f"DB_USERNAME=\n")
                file.write(f"DB_PASSWORD=\n")
                file.write(f"DB_HOST=localhost\n")
            os.system("npm run watch")
            os.system(f"a2ensite {subdomain}.domain.ao.conf")
            os.system("systemctl reload apache2")
            os.system("systemctl restart apache2")
            return f"user and subdomain created | {subdomain}.domain.ao"

# Route for user sign-in
@app.route('/signin', methods=['POST'])
def signin():
    email = request.form['email']
    password = request.form['password']
    cur = conn.cursor()
    query = f"SELECT 1 FROM Users.Users WHERE email = %s AND password = %s"
    conn.ping()  # Reconnecting MySQL
    with conn.cursor() as cursor:
        cursor.execute(query, (email, password))
        existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return "Signed in"
    else:
        return "Email or Password is incorrect"

# Driver Code
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
