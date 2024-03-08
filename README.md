### Note: This Project Is Not Finished Yet, It Is Under Development.

# Overview:
Python API application designed to handle user registration, sign-in, and dynamic subdomain creation using CloudFlare API. It utilizes a MySQL database to store user information and interacts with the local Apache server to manage virtual host configurations.

# Components:
## 1-Imports:

The script imports necessary modules including pymysql for MySQL database connectivity, Flask for web server functionalities, CloudFlare for managing DNS records, and os for interacting with the operating system.
## 2-Configuration:

Database Connection: The script establishes a connection to a MySQL database using the pymysql.connect method. Database credentials such as host, username, and password are hardcoded in the script.
CloudFlare API: It initializes a CloudFlare client using an email address and API token. The API token is stored as a global variable.
## 3-Flask Application:

The script initializes a Flask application instance.
## 4-Endpoints:

Registration Endpoint (/reg):

Handles POST requests for user registration.
Checks if the provided email, username, or subdomain already exist in the database. If not, it inserts the user details into the database and creates a subdomain record using CloudFlare API. It also creates Apache virtual host configurations for the subdomain.
Responds with a success message if registration is successful or appropriate error messages if user or subdomain already exists.
Sign-in Endpoint (/signin):

Handles POST requests for user sign-in.
Verifies the provided email and password against the database. If the credentials match, it responds with a success message; otherwise, it responds with an error message.
## 5-Database Operations:

The script performs database operations using raw SQL queries. It checks for existing users during registration and verifies credentials during sign-in.
## 6-CloudFlare Integration:

It interacts with the CloudFlare API to manage DNS records for subdomains dynamically. It checks for the existence of a CloudFlare zone, creates DNS records for new subdomains, and handles errors appropriately.
## 7-Apache Integration:

It creates Apache virtual host configurations for new subdomains dynamically, writes configurations to disk, creates directories for subdomain content, and reloads Apache service to apply changes.




~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


<pre>
mv domain.ao.conf /etc/apache2/sites-available
</pre>

<pre>
sudo systemctl restart apache2 
</pre>

<pre>
cd /
pip install virtualenv
virtualenv venv
source ./venv/bin/activate
python reg.py 
</pre>




Mahdi Jaber | 8 / 3 / 2024 12:30 PM
