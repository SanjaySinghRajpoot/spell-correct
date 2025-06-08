
from app.models import models
from app.models.models import NameArchieve, Metaphone 
import jellyfish
from pathlib import Path



class DB_service():

    def __init__(self):
        from app.routes.routes import get_db
        db_gen = get_db()
        self.db = next(db_gen)
        
    def initialize_database(self):
        """Initialize database and load name data from files"""

        COUNTRIES = ["Denmark", "Finland", "Iceland", "Norway", "Sweden"]
    
        
        try:
            # Load data from files
            for country in COUNTRIES:
                file_path = Path(f"static/{country}.txt")
                if not file_path.exists():
                    continue
                    
                with open(file_path, 'r') as f:
                    names = [line.strip() for line in f if line.strip()]
                    
                    for name in names:
                        # Check if name exists
                        existing = self.db.query(NameArchieve).filter(
                            NameArchieve.name == name,
                            NameArchieve.country == country
                        ).first()
                        
                        if not existing:
                            # Create new name record
                            new_name = NameArchieve(name=name, country=country)
                            self.db.add(new_name)
                            self.db.flush()  # To get the ID
                            
                            # Generate and store metaphone
                            meta = jellyfish.metaphone(name)
                            new_metaphone = Metaphone(name_id=new_name.id, metaphone=meta)
                            self.db.add(new_metaphone)
            
            self.db.commit()
        except Exception as e:
            print(f"Error saving data: {e}")
            return None
        
    def save_metadata(name, country, matches):
        try: 
            pass


        except Exception as e:
            print(f"Error saving data: {e}")
            return None

