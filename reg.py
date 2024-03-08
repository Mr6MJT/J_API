
import pymysql
from flask import Flask, render_template, request
import CloudFlare
import os
#from dotenv import dotenv_values, set_key


app = Flask(__name__)
conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password = "",
    db='Users',
)
API_KEY = ''
cf = CloudFlare.CloudFlare(
    email="@gmail.com",
    token=API_KEY
)

@app.route('/reg', methods=['POST'])
def register():
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    subdomain = request.form['subdomain']
    query = f"SELECT 1 FROM Users.Users WHERE email = %s OR username = %s OR subdomain = %s"

    conn.ping()  # Reconnecting MySQL
    with conn.cursor() as cursor:
       cursor.execute(query, (email, username, subdomain))  # Pass email and username variables directly
       existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return "User exists"
    else:
        query = f"INSERT INTO Users.Users (email, username, password, subdomain) VALUES (%s, %s, %s, %s)"
        conn.ping()  # Reconnecting MySQL
        with conn.cursor() as cursor:
             cursor.execute(query, (email, username, password, subdomain))  # Pass email and username variables directly
             existing_user = cursor.fetchone()
             conn.commit()  # Commit the transaction
             conn.close()
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
            print("Record doesn't exist, creating new record...")
            a_record = {
                "type": "A",
                "name": subdomain,
                "ttl": 1,
                "content": "0.0.0.0"
            }
            vh = f"""
                    <VirtualHost {subdomain}.domain.ao:80>
                            DocumentRoot "/var/www/html/{subdomain}"
                            ServerName {subdomain}.domain.ao
                    </VirtualHost>
            """
            cf.zones.dns_records.post(ZONE_ID, data=a_record)
            directory = "/etc/apache2/sites-available/"
            with open(f"{directory}{subdomain}.domain.ao.conf", "w") as file:
                file.write(vh)
            ddirectory = f"/var/www/html/{subdomain}"
            if not os.path.exists(ddirectory):
                os.makedirs(ddirectory)
            with open(f"{ddirectory}/index.html", "w") as file:
                file.write(f"<h1>{subdomain}</h1>")
            os.system(f"a2ensite {subdomain}.domain.ao.conf")
            os.system("systemctl reload apache2")
            os.system("systemctl restart apache2")
            return f"user and subdomain created | {subdomain}.domain.ao"

@app.route('/signin', methods=['POST'])
def signin():
    email = request.form['email']
    password = request.form['password']
    cur = conn.cursor()
    query = f"SELECT 1 FROM Users.Users WHERE email = %s AND password = %s"
    conn.ping()  # Reconnecting MySQL
    with conn.cursor() as cursor:
       cursor.execute(query, (email, password))  # Pass email and username variables directly
       existing_user = cursor.fetchone()


    if existing_user:
        conn.close()
        return "Signed in"
    else:
        return "Email or Password is incorrect"

# Driver Code
if __name__ == "__main__" :
    app.run(debug=True, host='0.0.0.0', port=8000)


