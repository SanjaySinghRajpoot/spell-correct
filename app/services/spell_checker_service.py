import time
import random

from fastapi import Path
from app.models.models import CorrectedNames, InputNames, NameArchieve, Metaphone 
from functools import lru_cache
import jellyfish
from typing import List, Optional, Tuple, Union

from typing import List, Tuple, Dict
import jellyfish
from functools import lru_cache
import string

from app.services.db_interaction import COUNTRIES
from app.utils.utils import convert_to_pydantic_response

class SpellCheck:
    def __init__(self):
        self.THRESHOLD = 2
        self.MAX_DISTANCE = 3
        self.PHONETIC_WEIGHT = 0.4
        self.EDIT_DISTANCE_WEIGHT = 0.3
        self.JARO_WINKLER_WEIGHT = 0.3

        from app.services.db_interaction import DB_service
        self.db_obj = DB_service()

    @lru_cache(maxsize=1000)
    def get_phonetic_candidates(self, name: str, country: str = None) -> List[str]:
        """
        Get phonetic candidates from database with optional country filter
        """
        target_metaphone = jellyfish.metaphone(name)
        
        try:
            query = self.db_obj.db.query(NameArchieve.name).join(Metaphone).filter(
                Metaphone.metaphone == target_metaphone
            )
            
            if country in COUNTRIES:
                query = query.filter(NameArchieve.country == country)
            
            return [row[0] for row in query.all()]
        except Exception as e:
            return []
        finally:
            self.db_obj.db.close()

    def _normalize_name(self, name: str) -> str:
        """Normalize names by removing punctuation and standardizing case"""
        return name.translate(str.maketrans('', '', string.punctuation)).lower().strip()

    def calculate_similarity_scores(self, original: str, candidate: str) -> Dict[str, float]:
        """
        Calculate multiple similarity metrics between two names
        Returns dictionary of scores
        """
        norm_original = self._normalize_name(original)
        norm_candidate = self._normalize_name(candidate)
        
        # Edit distance score (inverted and normalized)
        edit_distance = jellyfish.levenshtein_distance(norm_original, norm_candidate)
        max_len = max(len(norm_original), len(norm_candidate))
        edit_score = 1 - (edit_distance / max_len) if max_len > 0 else 0
        
        # Jaro-Winkler similarity (good for typos)
        jaro_score = jellyfish.jaro_winkler_similarity(norm_original, norm_candidate)
        
        # Phonetic similarity
        original_meta = jellyfish.metaphone(norm_original)
        candidate_meta = jellyfish.metaphone(norm_candidate)
        phonetic_score = 1.0 if original_meta == candidate_meta else 0.5 if original_meta.startswith(candidate_meta[:2]) else 0
        
        return {
            'edit_distance': edit_score,
            'jaro_winkler': jaro_score,
            'phonetic': phonetic_score
        }

    def get_suggestions(self, name: str, country: str = None) -> List[Dict[str, float]]:
        """
        Get ranked name suggestions with similarity scores
        Returns list of dictionaries with name and composite similarity score
        """
        candidates = self.get_phonetic_candidates(name, country)
        suggestions = []
        
        for candidate in candidates:
            scores = self.calculate_similarity_scores(name, candidate)
            
            # Composite score calculation
            composite_score = (
                (scores['phonetic'] * self.PHONETIC_WEIGHT) +
                (scores['edit_distance'] * self.EDIT_DISTANCE_WEIGHT) +
                (scores['jaro_winkler'] * self.JARO_WINKLER_WEIGHT)
            )
            
            suggestions.append({
                "name": candidate,
                "similarity_score": round(composite_score, 4),
                "score_breakdown": {
                    "phonetic": scores['phonetic'],
                    "edit_distance": scores['edit_distance'],
                    "jaro_winkler": scores['jaro_winkler']
                }
            })
        
        # Sort by composite score (descending)
        suggestions.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return [{"name": s["name"], "similarity_score": s["similarity_score"]} for s in suggestions]
    
    def evaluate_suggestions(
        self,
        suggestions: List[Dict[str, float]],
        min_score: float = 0.85,
        min_top_score: float = 0.9,
        min_count: int = 1
    ) -> Dict[str, Union[bool, List[Dict[str, float]]]]:
        """
        Evaluate name suggestions to determine if there are good matches
        
        Args:
            suggestions: List of suggestions from get_suggestions()
            min_score: Minimum similarity score to consider as a potential match
            min_top_score: Minimum score for the top suggestion to be considered a good match
            min_count: Minimum number of suggestions meeting min_score threshold
        
        Returns:
            Dictionary containing:
            - is_good_match: Boolean indicating if good matches were found
            - filtered_suggestions: List of suggestions that meet the criteria
        """
        if not suggestions:
            return {
                "is_good_match": False,
                "filtered_suggestions": []
            }
        
        # Filter suggestions that meet minimum score
        filtered = [s for s in suggestions if s['similarity_score'] >= min_score]
        
        # Determine if we have a good match
        has_min_count = len(filtered) >= min_count
        has_strong_top_match = suggestions[0]['similarity_score'] >= min_top_score
        
        is_good_match = has_strong_top_match or (has_min_count and len(filtered) > 0)
        
        return {
            "is_good_match": is_good_match,
            "filtered_suggestions": filtered
        }
    
    def name_exist_check(self, name: str, country: Optional[str] = None) -> tuple[bool, list[dict[str, float]]]:
        """
        Check if name exists in database and return suggestions if found
        
        Args:
            name: Name to check
            country: Country to filter by (optional)
            
        Returns:
            tuple: (exists: bool, suggestions: list[dict])
                suggestions format: [{"name": suggested_name, "similarity_score": score}]
        """
        try:
            # Build the base query for input names
            query = self.db_obj.db.query(InputNames).filter(
                InputNames.name == name
            )

            # Add country filter only if country is provided
            if country is not None:
                query = query.filter(InputNames.country == country)

            input_name = query.first()

            if not input_name:
                return False, []

            # Get all corrected names for this input name
            corrected_names = self.db_obj.db.query(CorrectedNames).filter(
                CorrectedNames.input_name_id == input_name.id
            ).order_by(CorrectedNames.similarity_score.desc()).all()

            # Format the response
            suggestions = [{
                "name": cn.suggested_name,
                "similarity_score": float(cn.similarity_score) if cn.similarity_score is not None else 0.0
            } for cn in corrected_names]

            return True, suggestions

        except Exception as e:
            return False, []
   

