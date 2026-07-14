from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import pyodbc

app = Flask(__name__)
CORS(app)

# Dossier racine du projet (D:\Attestation)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONN_STR = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost\\sqlserver;"
    "Database=AttestationDb_RDC;"
    "Trusted_Connection=yes;"
)

def get_db_connection():
    return pyodbc.connect(CONN_STR)

# 1. ROUTE : Affiche la page d'administration directement via le serveur
@app.route('/admin')
def serve_admin():
    return send_from_directory(BASE_DIR, 'admin.html')

# 2. ROUTE : Affiche la page de félicitations directement via le serveur
@app.route('/')
def serve_attestation():
    return send_from_directory(BASE_DIR, 'attestation.html')

# 3. ROUTE API : Récupérer un candidat par son ID
@app.route('/api/candidat/<string:candidat_id>', methods=['GET'])
def get_candidat(candidat_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nom_complet FROM candidats WHERE id = ?", candidat_id)
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return jsonify({"nom_complet": row[0]}), 200
        else:
            return jsonify({"error": "Candidat introuvable"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 4. ROUTE API : Ajouter un nouveau candidat
@app.route('/api/candidat', methods=['POST'])
def add_candidat():
    try:
        data = request.get_json()
        if not data or 'nom_complet' not in data:
            return jsonify({"error": "Le nom complet est obligatoire"}), 400
        
        nom_complet = data['nom_complet'].strip().upper()
        
        if not nom_complet:
            return jsonify({"error": "Le nom ne peut pas être vide"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO candidats (nom_complet) OUTPUT Inserted.id VALUES (?)", 
            nom_complet
        )
        new_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Candidat ajouté avec succès !",
            "id": str(new_id),
            "nom_complet": nom_complet
        }), 201
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Serveur d'attestation démarré sur http://127.0.0.1:5000")
    app.run(debug=True, port=5000)