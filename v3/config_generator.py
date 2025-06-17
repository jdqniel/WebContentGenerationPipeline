import json
import os
import random
from typing import Dict, Any, List

class ConfigGenerator:
    """
    Loads all possible configuration components from the v3/data directory
    and can generate a random, valid request configuration on demand.
    """
    def __init__(self, data_path: str):
        self.data_path = data_path
        self._load_data()

    def _load_data(self):
        """Loads all JSON data files into memory."""
        with open(os.path.join(self.data_path, 'document_types.json'), 'r', encoding='utf-8') as f:
            self.document_types: List[str] = json.load(f)

        with open(os.path.join(self.data_path, 'partners.json'), 'r', encoding='utf-8') as f:
            self.partners: List[Dict[str, str]] = json.load(f)

        with open(os.path.join(self.data_path, 'content_strategies_and_categories.json'), 'r', encoding='utf-8') as f:
            self.strategies: Dict[str, List[str]] = json.load(f)

        with open(os.path.join(self.data_path, 'content_context_and_settings.json'), 'r', encoding='utf-8') as f:
            settings = json.load(f)
            self.target_audiences: List[str] = settings['targetAudience']
            self.content_goals: List[str] = settings['contentGoals']
            self.content_tones: List[str] = settings['contentTones']
        
        print("✅ ConfigGenerator initialized with all data from v3/data.")

    def generate_random_config(self) -> Dict[str, Any]:
        """Dynamically builds a randomized request configuration."""
        
        # Select strategy
        strategy_category = random.choice(list(self.strategies.keys()))
        specific_focus = random.choice(self.strategies[strategy_category])

        # Select a random number of partners
        num_partners = random.randint(1, min(4, len(self.partners)))
        selected_partners = random.sample(self.partners, num_partners)

        # Build the final configuration object
        config = {
            "documentType": random.choice(self.document_types),
            "strategy": {
                "category": strategy_category,
                "specificFocus": specific_focus
            },
            "partners": selected_partners,
            "generationConfig": {
                "creationMethod": "AI-Generated",
                "targetAudience": random.choice(self.target_audiences),
                "contentGoal": random.choice(self.content_goals),
                "contentTone": random.choice(self.content_tones)
            }
        }
        return config