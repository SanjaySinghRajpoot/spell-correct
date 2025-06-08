
from app.models import models
from app.models.models import CorrectedNames, InputNames, NameArchieve, Metaphone 
import jellyfish
from pathlib import Path

COUNTRIES = ["Denmark", "Finland", "Iceland", "Norway", "Sweden"]


class DB_service():

    def __init__(self):
        from app.routes.routes import get_db
        db_gen = get_db()
        self.db = next(db_gen)
        
    def initialize_database(self):
        """Using bulk insert operations for maximum performance"""
        
        try:
            for country in COUNTRIES:
                file_path = Path(f"static/{country}.txt")
                if not file_path.exists():
                    continue
                    
                with open(file_path, 'r') as f:
                    names = [line.strip() for line in f if line.strip()]
                    
                    # Get existing names in one query
                    existing_names = {n.name for n in self.db.query(NameArchieve.name)
                                    .filter(NameArchieve.country == country)
                                    .all()}
                    
                    # Filter new names
                    new_names = [name for name in names if name not in existing_names]
                    
                    if not new_names:
                        continue
                    
                    # Bulk insert names
                    name_records = [{"name": name, "country": country} for name in new_names]
                    self.db.bulk_insert_mappings(NameArchieve, name_records)
                    self.db.flush()
                    
                    # Get IDs for the new names
                    inserted = self.db.query(NameArchieve).filter(
                        NameArchieve.country == country,
                        NameArchieve.name.in_(new_names)
                    ).all()
                    
                    # Bulk insert metaphones
                    metaphones = [
                        {"name_id": n.id, "metaphone": jellyfish.metaphone(n.name)}
                        for n in inserted
                    ]
                    self.db.bulk_insert_mappings(Metaphone, metaphones)
                    
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"Error in bulk operation: {e}")
        
    def save_name_metadata(self, name, country, suggestions):
        try: 
            new_name = InputNames(name=name, country=country)
            self.db.add(new_name)
            self.db.flush()
    
            for suggestion in suggestions:
                corrected_name = CorrectedNames(
                    input_name_id = new_name.id,
                    suggested_name = suggestion.get("name"),
                    similarity_score = suggestion.get("similarity_score")
                )
                self.db.add(corrected_name)

            self.db.commit()
            
        except Exception as e:
            print(f"Error saving data: {e}")
            return None
