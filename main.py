import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    model='llama-3.3-70b-versatile',
    temperature=0.2
)

# Prompt for explaining the SQL queries
explain_system_prompt = """
You are a senior SQL engineer and instructor.

Your task is to explain SQL queries in a clear, beginner-friendly, and educational way.
Assume the user is new to SQL and wants to understand what each part of the query does.

Rules:
- Do NOT execute the query
- Do NOT assume any table data or actual results
- Do NOT guess schemas beyond what is written
- Explain the query step-by-step
- If joins, filters, aggregations, or subqueries exist, explain them clearly
- If aliases are used, explain what they refer to
- When appropriate, explain the purpose of individual SQL keywords

Explanation Guidelines:
1. First, identify the overall intent of the query.
2. Then list the tables involved.
3. Then explain the query clause-by-clause in execution order.
4. For simple queries, explain the role of each SQL keyword (e.g., SELECT, FROM).
5. End with a clear description of what the query would return conceptually.

Output format:
1. Query Intent
2. Tables Involved
3. Keyword / Clause Explanation
4. Final Result Description

------------------------------------
Example:

SQL Query:
SELECT name FROM employee;

Explanation:

1. Query Intent:
The intent of this query is to retrieve the names of employees from the employee table.

2. Tables Involved:
- employee: This table is expected to store employee-related information.

3. Keyword / Clause Explanation:
- SELECT: This keyword specifies which columns should be retrieved from the table.
- name: This is the column being requested; it represents the employee's name.
- FROM: This keyword specifies the table from which the data should be fetched.
- employee: This is the table that contains the requested column.

4. Final Result Description:
The query will return a list of employee names from the employee table.

------------------------------------

Now, explain the user-provided SQL query following the same structure and level of detail.
"""


# Prompt for Generating the SQL Query from natural language
nlp_to_sql_system_prompt = """
You are a senior SQL engineer. 
Generate SQL queries based on natural language descriptions.

Since you don't have the actual database schema, you'll need to make reasonable assumptions about:
1. Table names (use the tables mentioned in the explanation)
2. Column names (use logical names based on the context)
3. Database structure (create a plausible schema based on the query's purpose)


Important:
-FIRST, list ALL assumptions you made in a clear numbered list
- Generate ONLY the SQL query 
- End the query with a semicolon

Format your output exactly like this:

Assumptions:
1. [Your first assumption]
2. [Your second assumption]
3. [Your third assumption]

SQL Query:
[Your clean SQL query here]

"""


explain_prompt = ChatPromptTemplate.from_messages([
    ('system', explain_system_prompt),
    ('human', "Explain this SQL Query: {input}")
])

nlp_to_sql_prompt = ChatPromptTemplate.from_messages([
    ('system', nlp_to_sql_system_prompt),
    ('human', "Generate an SQL query for: {input}")
])

parser = StrOutputParser()
explain_chain = explain_prompt | llm | parser
nlp_to_sql_chain = nlp_to_sql_prompt | llm | parser

JSON_FILE = "sql_queries.json"

def parse_generated_output(output):

    if "Assumptions:" in output:
        parts = output.split("SQL Query:")
        if len(parts) == 2:
            assumptions = parts[0].replace("Assumptions:", "").strip()
            sql_query = parts[1].strip()
            return assumptions, sql_query

    lines = output.split('\n')
    assumptions_lines = []
    sql_lines = []
    in_sql = False
    
    for line in lines:
        if line.strip().startswith("SELECT") or line.strip().startswith("select") or line.strip().startswith("WITH"):
            in_sql = True
        if in_sql:
            sql_lines.append(line)
        else:
            assumptions_lines.append(line)
    
    assumptions = '\n'.join(assumptions_lines).strip()
    sql_query = '\n'.join(sql_lines).strip()
    
    return assumptions, sql_query

def save_to_json(mode, user_input, output, assumptions=None, sql_query=None):
    data = []
    
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = []
    
    if mode == "generate_sql" and assumptions and sql_query:
        # For SQL generation
        entry = {
            "mode": mode,
            "user_input": user_input.strip(),
            "assumptions": assumptions,
            "sql_query": sql_query
        }
    else:
        # For SQL explanation
        entry = {
            "mode": mode,
            "user_input": user_input.strip(),
            "output": output.strip()
        }
    
    data.append(entry)
    
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def explain_sql_mode():
    print("MODE 1: EXPLAIN SQL QUERY")
    print("\nEnter an SQL query to explain (end with ;):")
    
    query = ""
    while True:
        line = input()
        if line.strip().lower() == 'back':
            return
        query += line + '\n'
        if ';' in line:
            break

    print("EXPLANATION:")  
    explanation = explain_chain.invoke({"input": query})
    print(explanation)
    
    save_to_json("explain_sql", query, explanation)


def generate_sql_mode():
    print("MODE 2: GENERATE SQL FROM NATURAL LANGUAGE")
    print("\nEnter the description:")
    
    description = input()
    
    if description.strip().lower() == 'back':
        return

    print("GENERATED SQL QUERY:")
    raw_output = nlp_to_sql_chain.invoke({"input": description})
    assumptions, sql_query = parse_generated_output(raw_output)

    print("ASSUMPTIONS:")
    print(assumptions)

    print("\nSQL QUERY:")
    print(sql_query)
    
    save_to_json("generate_sql", description, raw_output, assumptions, sql_query)

def main_menu():
    while True:
        print("SQL ASSISTANT")
        print("\nChoose mode:")
        print("1. Explain an SQL Query")
        print("2. Generate SQL from Natural Language")
        print("3. View History")
        print("4 Exit")
        
        choice = input("\nEnter choice (1-4)").strip()
        
        if choice == "1":
            explain_sql_mode()
        elif choice == "2":
            generate_sql_mode()
        elif choice == "3":
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()