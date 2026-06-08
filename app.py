from flask import Flask, request, jsonify, render_template
import os
import sqlite3
import schema_manager
import sql_generator

app = Flask(__name__)

# Track active database session (default is ecommerce)
active_db = "ecommerce"

# Initialize databases on server startup
schema_manager.init_databases()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/databases", methods=["GET"])
def get_databases():
    return jsonify({
        "active": active_db,
        "databases": list(schema_manager.DATABASES.keys())
    })

@app.route("/api/select_db", methods=["POST"])
def select_db():
    global active_db
    data = request.json or {}
    db_key = data.get("db_key")
    if db_key not in schema_manager.DATABASES:
        return jsonify({"success": False, "error": f"Database '{db_key}' is invalid"}), 400
    
    active_db = db_key
    try:
        schema = schema_manager.get_database_schema(active_db)
        return jsonify({
            "success": True,
            "active": active_db,
            "schema": schema
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/schema", methods=["GET"])
def get_schema():
    try:
        schema = schema_manager.get_database_schema(active_db)
        return jsonify({
            "success": True,
            "schema": schema
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/query", methods=["POST"])
def run_query():
    data = request.json or {}
    query_sql = data.get("query")
    if not query_sql:
        return jsonify({"success": False, "error": "No SQL query provided"}), 400
    
    result = schema_manager.execute_query(active_db, query_sql)
    return jsonify(result)

@app.route("/api/generate_sql", methods=["POST"])
def generate_sql():
    data = request.json or {}
    question = data.get("question")
    api_key = data.get("api_key") # From custom user settings
    
    if not question:
        return jsonify({"success": False, "error": "No question provided"}), 400
        
    try:
        # Generate using our smart engine (Gemini API or Heuristic fallback)
        sql, explanation = sql_generator.generate_llm_sql(active_db, question, api_key)
        return jsonify({
            "success": True,
            "sql": sql,
            "explanation": explanation
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/explain_sql", methods=["POST"])
def explain_sql():
    data = request.json or {}
    sql = data.get("sql")
    api_key = data.get("api_key")
    
    if not sql:
        return jsonify({"success": False, "error": "No SQL provided"}), 400
        
    try:
        explanation = sql_generator.explain_sql_locally(sql)
        return jsonify({
            "success": True,
            "explanation": explanation
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/custom_db", methods=["POST"])
def create_custom_db():
    global active_db
    data = request.json or {}
    ddl_script = data.get("sql_script")
    
    if not ddl_script:
        return jsonify({"success": False, "error": "No SQL script provided"}), 400
        
    db_path = schema_manager.DATABASES["custom"]
    
    # Drop and recreate custom database file
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to reset custom DB: {str(e)}"}), 500
            
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON;")
        # Execute script (contains DDL/DML statement sequence)
        cursor.executescript(ddl_script)
        conn.commit()
        
        active_db = "custom"
        schema = schema_manager.get_database_schema(active_db)
        return jsonify({
            "success": True,
            "active": active_db,
            "schema": schema,
            "message": "Custom database created and activated successfully."
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Error executing custom DB script: {str(e)}"}), 400
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Start flask application locally on port 5000 (standard port)
    app.run(debug=True, port=5000)
