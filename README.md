## SQL  Explanator and Generator Bot ##

## Overview
A dual-mode SQL tool that helps you understand and generate SQL queries using AI. This application allows you to either explain existing SQL queries or generate SQL queries from natural language descriptions.

# Features

 # Mode 1: SQL Query Explainer
 
- Upload any SQL query for detailed, educational explanations
- Step-by-step breakdown of query components
- Beginner-friendly explanations of SQL keywords and concepts
- Ideal for learning SQL or understanding complex queries

# Mode 2: SQL Query Generator

- Convert natural language descriptions into SQL queries
- AI makes reasonable assumptions about database schema
- Clear separation of assumptions from executable SQL code
- Perfect for quickly generating queries based on business requirements

# Additional Features
- History tracking of all queries and explanations
- JSON export of all interactions

# File Structure
- main.py          # Main application file
- sql_queries.json # JSON file storing history (auto-generated)

#  Data Storage
All interactions are saved to sql_queries.json:

- For SQL Explanations:
  {
  "mode": "explain_sql",
  "user_input": "SELECT * FROM users;",
  "output": "1. Query Intent: ..."
}

- For SQL Generation:
  {
  "mode": "generate_sql",
  "user_input": "Show out of stock products",
  "assumptions": "1. There's a table named 'products'...",
  "sql_query": "SELECT id, name FROM products WHERE quantity = 0;"
}

# Limitations & Notes

- Assumption-based Generation: The SQL generator makes educated guesses about table/column names. You may need to adjust the generated SQL to match your actual database schema.
- Groq API Key is used.
- No Database Connection: This tool doesn't connect to actual databases. It only explains and generates SQL syntax.

# Quick Test Queries
- For Mode 1 (Explain SQL):
  SELECT * FROM employees WHERE salary > 50000 ORDER BY hire_date DESC;
  
- For Mode 2 (Generate SQL):
   - "Find customers who haven't ordered in the last 30 days"
   - "Show top 10 products by sales"
