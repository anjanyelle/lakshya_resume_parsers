# Database Migration Script for Complete Resume JSON Format

"""
Migration script to add new tables and fields for complete resume JSON format
Run this to update your database schema
"""

from sqlalchemy import create_engine, text
from app.core.database import engine
from app.models.additional_models import Project, Publication, Volunteer, Award, Reference, AdditionalText

def create_new_tables():
    """
    Create new tables for complete resume format
    """
    # Use existing engine from database.py
    from app.core.database import Base
    
    # Create new tables
    Base.metadata.create_all(engine, tables=[
        Project.__table__,
        Publication.__table__,
        Volunteer.__table__,
        Award.__table__,
        Reference.__table__,
        AdditionalText.__table__
    ])
    
    print("✅ New tables created successfully")

def add_candidate_fields():
    """
    Add new fields to candidates table
    """
    engine = create_engine("your_database_url")  # Replace with your actual DB URL
    
    # SQL statements to add new columns
    alter_statements = [
        "ALTER TABLE candidates ADD COLUMN first_name VARCHAR(200)",
        "ALTER TABLE candidates ADD COLUMN last_name VARCHAR(200)",
        "ALTER TABLE candidates ADD COLUMN title_before_name VARCHAR(100)",
        "ALTER TABLE candidates ADD COLUMN title_after_name VARCHAR(100)",
        "ALTER TABLE candidates ADD COLUMN date_of_birth DATE",
        "ALTER TABLE candidates ADD COLUMN street VARCHAR(500)",
        "ALTER TABLE candidates ADD COLUMN city VARCHAR(200)",
        "ALTER TABLE candidates ADD COLUMN country VARCHAR(200)",
        "ALTER TABLE candidates ADD COLUMN postal VARCHAR(50)",
        "ALTER TABLE candidates ADD COLUMN web JSON",
        "ALTER TABLE candidates ADD COLUMN profile TEXT",
        "ALTER TABLE candidates ADD COLUMN hobbies JSON"
    ]
    
    with engine.connect() as conn:
        for statement in alter_statements:
            try:
                conn.execute(text(statement))
                print(f"✅ Added: {statement}")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"⚠️  Already exists: {statement}")
                else:
                    print(f"❌ Error: {statement} - {e}")
    
    print("✅ Candidate table fields added successfully")

def update_candidate_relationships():
    """
    Update Candidate model relationships
    """
    # This would require updating your existing Candidate model
    # You would add these relationships to your existing model:
    
    relationships_code = '''
    # Add to your existing Candidate model:
    
    # New relationships
    projects = relationship("Project", back_populates="candidate")
    publications = relationship("Publication", back_populates="candidate")
    volunteer_experience = relationship("Volunteer", back_populates="candidate")
    awards = relationship("Award", back_populates="candidate")
    references = relationship("Reference", back_populates="candidate")
    additional_texts = relationship("AdditionalText", back_populates="candidate")
    '''
    
    print("📝 Add these relationships to your existing Candidate model:")
    print(relationships_code)

def create_indexes():
    """
    Create indexes for performance
    """
    engine = create_engine("your_database_url")  # Replace with your actual DB URL
    
    index_statements = [
        "CREATE INDEX IF NOT EXISTS idx_projects_candidate_id ON projects(candidate_id)",
        "CREATE INDEX IF NOT EXISTS idx_publications_candidate_id ON publications(candidate_id)",
        "CREATE INDEX IF NOT EXISTS idx_volunteer_candidate_id ON volunteer_experience(candidate_id)",
        "CREATE INDEX IF NOT EXISTS idx_awards_candidate_id ON awards(candidate_id)",
        "CREATE INDEX IF NOT EXISTS idx_references_candidate_id ON references(candidate_id)",
        "CREATE INDEX IF NOT EXISTS idx_additional_texts_candidate_id ON additional_texts(candidate_id)"
    ]
    
    with engine.connect() as conn:
        for statement in index_statements:
            try:
                conn.execute(text(statement))
                print(f"✅ Created: {statement}")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"⚠️  Already exists: {statement}")
                else:
                    print(f"❌ Error: {statement} - {e}")
    
    print("✅ Indexes created successfully")

def run_full_migration():
    """
    Run complete migration
    """
    print("🚀 Starting Complete Resume JSON Migration...")
    print("=" * 60)
    
    try:
        create_new_tables()
        print()
        add_candidate_fields()
        print()
        update_candidate_relationships()
        print()
        create_indexes()
        print()
        print("🎉 Migration completed successfully!")
        print("=" * 60)
        print("📋 Next Steps:")
        print("1. Update your Candidate model with new fields and relationships")
        print("2. Update your schemas with new Pydantic models")
        print("3. Add API endpoints for new sections")
        print("4. Test the complete JSON format")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("Please check your database connection and permissions")

if __name__ == "__main__":
    run_full_migration()
