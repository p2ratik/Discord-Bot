from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np

class EmbeddingManager:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model_name = str(model_name)
        self.model = SentenceTransformer(model_name)


    async def embed_pairs(self, parsed):
        """Function to embed the incoming texts"""
        # Returns a numpy arr . 
        for pair in parsed['pairs']:
            pair['embedding'] = self.model.encode(pair['incoming']).tolist()
        
        return parsed
    