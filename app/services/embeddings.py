from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np

class EmbeddingManager:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model_name = str(model_name)
        self.model = None
        self._loadModel()

    def _loadModel(self): 
        "Function to load the Embedding Model using Sentence Transformer"
        try:
            print(f"Loading the {self.model_name} .....")
            self.model = SentenceTransformer(self.model_name)
            print(f"Model loaded successfully. Embedding dimension ✔: {self.model.get_sentence_embedding_dimension()}")
        except Exception as e:
            print(f"Failed to load the model {e}")

    async def embed_pairs(self, pairs:List[Dict]):
        """Function to embed the incoming texts"""

        for pair in pairs:
            pair['embed'] = self.model.encode(pair['incoming"'])

        return pairs
    