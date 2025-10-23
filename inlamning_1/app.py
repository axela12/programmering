from flask import Flask, render_template, request, session
import mysql.connector
from mysql.connector import Error
import secrets

app = Flask(__name__)

app.secret_key = secrets.token_hex(16)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Ändra detta till ditt MySQL-användarnamn
    'password': '',  # Ändra detta till ditt MySQL-lösenord
    'database': 'inlamning_1'  # TODO: Ändra detta till ditt databasnamn
}

def get_db_connection():
    """Skapa och returnera en databasanslutning"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Fel vid anslutning till MySQL: {e}")
        return None

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    # hantera POST request från inloggningsformuläret
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Anslut till databasen
        connection = get_db_connection()
        if connection is None:
            return "Databasanslutning misslyckades", 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            # Kontrollera om användaren fanns i databasen och lösenordet är korrekt.
            # Om lösenordet är korrekt så sätt sessionsvariabler och skicka tillbaka en hälsning med användarens namn.
            # Om lösenordet inte är korrekt skicka tillbaka ett felmeddelande med http-status 401.
            
            if user and user['password'] == password:
                # Inloggning lyckades - spara användarinfo i session
                session['user_id'] = user['id']
                session['username'] = user['username']
                return f"Inloggning lyckades! Välkommen {session['username']}!"
            else:
                # Inloggning misslyckades, skicka http status 401 (Unauthorized)
                return ('Ogiltigt användarnamn eller lösenord', 401)

        except Error as e:
            print(f"Databasfel: {e}")
            return "Databasfel inträffade", 500
        
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

if __name__ == '__main__':
    app.run(debug=True)