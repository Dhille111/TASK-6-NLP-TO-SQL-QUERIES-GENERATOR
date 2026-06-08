import unittest
import schema_manager
import sql_generator
import os

class TestNLPSQLSystem(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Ensure fresh databases are initialized
        schema_manager.init_databases()

    def test_database_files_exist(self):
        """Verify that SQLite database files are successfully created in the workspace."""
        for db_key, path in schema_manager.DATABASES.items():
            if db_key == "custom":
                continue # Custom DB is created dynamically, skipped on startup
            self.assertTrue(os.path.exists(path), f"Database file {path} should exist.")

    def test_schema_extraction_ecommerce(self):
        """Assert that E-Commerce schema is correctly parsed and contains columns/keys."""
        schema = schema_manager.get_database_schema("ecommerce")
        
        self.assertIn("customers", schema["tables"])
        self.assertIn("products", schema["tables"])
        self.assertIn("orders", schema["tables"])
        self.assertIn("order_items", schema["tables"])
        
        # Check rows count is set
        self.assertGreater(schema["tables"]["customers"]["row_count"], 0)
        
        # Check columns
        cols = [c["name"] for c in schema["tables"]["customers"]["columns"]]
        self.assertIn("customer_id", cols)
        self.assertIn("first_name", cols)
        
        # Check PK key is detected
        pk_col = next(c for c in schema["tables"]["customers"]["columns"] if c["name"] == "customer_id")
        self.assertTrue(pk_col["pk"])
        
        # Check relationship count is detected
        self.assertGreater(len(schema["relationships"]), 0)

    def test_schema_extraction_company(self):
        """Assert that Company schema is parsed and contains projects/employees structure."""
        schema = schema_manager.get_database_schema("company")
        self.assertIn("employees", schema["tables"])
        self.assertIn("departments", schema["tables"])
        self.assertIn("projects", schema["tables"])
        self.assertIn("employee_projects", schema["tables"])
        
        # Verify foreign keys detection
        fk_col = next(c for c in schema["tables"]["employees"]["columns"] if c["name"] == "dept_id")
        self.assertIsNotNone(fk_col["fk"])
        self.assertEqual(fk_col["fk"]["table"], "departments")

    def test_heuristic_generator_ecommerce(self):
        """Test keyword-matching heuristics on preset questions for E-Commerce."""
        sql, explanation = sql_generator.generate_heuristic_sql("ecommerce", "show all customers")
        self.assertTrue(sql.strip().upper().startswith("SELECT"))
        self.assertIn("customers", sql.lower())
        
        sql_cat, _ = sql_generator.generate_heuristic_sql("ecommerce", "list all products in electronics category")
        self.assertIn("products", sql_cat.lower())
        self.assertIn("electronics", sql_cat.lower())

    def test_heuristic_generator_company(self):
        """Test query heuristics on preset questions for Company HR."""
        sql, explanation = sql_generator.generate_heuristic_sql("company", "What is the average salary of employees in each department?")
        self.assertTrue("AVG(" in sql.upper())
        self.assertTrue("GROUP BY" in sql.upper())
        
    def test_safe_query_execution_read(self):
        """Execute selective SELECT statements and assert column and row fields."""
        res = schema_manager.execute_query("company", "SELECT first_name, salary FROM employees WHERE salary > 90000;")
        self.assertTrue(res["success"])
        self.assertEqual(res["type"], "read")
        self.assertIn("first_name", res["columns"])
        self.assertIn("salary", res["columns"])
        self.assertGreater(len(res["rows"]), 0)
        
    def test_safe_query_execution_error(self):
        """Assert error tracking and returning for invalid syntax."""
        res = schema_manager.execute_query("company", "SELECT invalid_column_name FROM employees;")
        self.assertFalse(res["success"])
        self.assertIn("error", res)

if __name__ == "__main__":
    unittest.main()
