import time
import random

from fastapi import Path
from app.models.models import NameArchieve, Metaphone 
from functools import lru_cache
import jellyfish
from typing import List, Tuple

class SpellCheck():

 
    @lru_cache(maxsize=1000)
    def get_phonetic_candidates(self, name: str, country: str) -> List[str]:
        """
        Get phonetic candidates from database, fallback to global search if 
        country not found
        """
        target_metaphone = jellyfish.metaphone(name)

        from app.services.db_interaction import DB_service
        db_obj = DB_service()
        
        try:
            query = db_obj.db.query(NameArchieve.name).join(Metaphone).filter(
                Metaphone.metaphone == target_metaphone
            )
            
            if country != None:
                query = query.filter(NameArchieve.country == country)
            
            candidates = [row[0] for row in query.all()]
            return candidates
        except Exception as e:
            return []
        finally:
             db_obj.db.close()


    def get_closest_matches(self, name: str, candidates: List[str]) -> Tuple[List[Tuple[str, int]], bool]:
        """
        Find closest matches by edit distance with quality threshold
        Returns:
            - Tuple of (matches, is_good_match)
            - matches: sorted list of (candidate, distance) tuples
            - is_good_match: True if at least one match with distance <= THRESHOLD exists
        """
        MAX_DISTANCE = 3  # Max allowed edit distance
        THRESHOLD = 2     # Distance threshold for good matches
        
        matches = []
        min_distance = float('inf')
        is_good_match = False
        
        try:
            for candidate in candidates:
                try:
                    distance = jellyfish.levenshtein_distance(
                        name.lower(), 
                        candidate.lower()
                    )
                    
                    if distance <= MAX_DISTANCE:
                        matches.append((candidate, distance))
                        if distance <= THRESHOLD:
                            is_good_match = True
                        min_distance = min(min_distance, distance)
                
                except Exception as e:
                    # Log individual candidate processing errors if needed
                    continue
            
            # Sort by distance (lower is better)
            matches.sort(key=lambda x: x[1])
            
            return matches, is_good_match
        
        except Exception as e:
            # Log the overall error if needed
            return [], False
        
   

