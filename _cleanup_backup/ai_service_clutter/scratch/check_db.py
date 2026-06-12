import psycopg2

def check_table():
    try:
        conn = psycopg2.connect('postgresql://postgres:Surya%40123@localhost:5432/resume_parser')
        cur = conn.cursor()
        cur.execute("""
            SELECT column_name, data_type, udt_name 
            from information_schema.columns 
            where table_name='parsing_jobs'
        """)
        rows = cur.fetchall()
        print("Columns in parsing_jobs details:")
        for r in rows:
            print(f"  {r[0]}: {r[1]} (udt: {r[2]})")
            
        cur.close()
        conn.close()
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    check_table()
