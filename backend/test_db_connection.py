# Database Connection Test

"""
Test script to verify database connection and table creation
"""

def test_database_connection():
    """
    Test database connection and show all tables
    """
    print("🔍 Testing Database Connection...")
    print("=" * 60)
    
    try:
        from app.core.database import engine
        from sqlalchemy import text
        
        print("✅ Database engine created")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test")).scalar()
            print(f"✅ Database connection successful: {result}")
        
        # Check all tables
        print("\n📋 Checking all tables in database...")
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name, table_type 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            
            tables = result.fetchall()
            print(f"📊 Total tables found: {len(tables)}")
            
            for table in tables:
                table_name = table[0]
                table_type = table[1]
                print(f"   - {table_name} ({table_type})")
                
                # Check if it's one of our new tables
                new_tables = ['projects', 'publications', 'volunteer_experience', 'awards', 'additional_texts', 'references']
                if table_name in new_tables:
                    print(f"     ✅ NEW TABLE DETECTED!")
        
        print("\n🎯 Checking specific new tables...")
        
        with engine.connect() as conn:
            for table_name in ['projects', 'publications', 'volunteer_experience', 'awards', 'additional_texts', 'references']:
                try:
                    result = conn.execute(text(f"""
                        SELECT COUNT(*) as row_count 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = '{table_name}'
                    """)).scalar()
                    
                    if result > 0:
                        print(f"   ✅ {table_name}: EXISTS")
                        
                        # Get row count
                        try:
                            row_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                            print(f"      📊 Rows: {row_count}")
                        except Exception as e:
                            print(f"      ❌ Cannot count rows: {e}")
                    else:
                        print(f"   ❌ {table_name}: NOT FOUND")
                        
                except Exception as e:
                    print(f"   ❌ Error checking {table_name}: {e}")
        
        print("\n🔧 Testing table creation...")
        
        # Test creating a simple table
        with engine.connect() as conn:
            try:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS test_table (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100)
                    )
                """))
                print("✅ Test table creation successful")
                
                # Check if it exists
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'test_table'
                """)).scalar()
                
                if result > 0:
                    print("✅ Test table visible in information_schema")
                    
                    # Clean up
                    conn.execute(text("DROP TABLE test_table"))
                    print("✅ Test table cleaned up")
                else:
                    print("❌ Test table not visible in information_schema")
                    
            except Exception as e:
                print(f"❌ Table creation test failed: {e}")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n🔧 Possible causes:")
        print("   - Database connection string incorrect")
        print("   - Database server not running")
        print("   - Insufficient permissions")
        print("   - Wrong database name")
        print("   - Network connectivity issues")

if __name__ == "__main__":
    test_database_connection()
