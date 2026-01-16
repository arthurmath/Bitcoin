from objects.transaction import Transaction
import hashlib
import time
from typing import List


class Bloc:
    def __init__(self, index, transactions, hash_precedent, difficulte=4):
        self.index = index
        self.transactions: List[Transaction] = transactions
        self.hash_precedent = hash_precedent
        self.timestamp = time.time()
        self.difficulte = difficulte
        self.hash = None
        # Calcul simplifié de la racine de Merkle
        merkle_content = ''.join(tx.hash_transaction for tx in self.transactions)
        self.racine_merkle = hashlib.sha256(merkle_content.encode()).hexdigest()
            
    def __str__(self):
        return f"Bloc #{self.index} | Hash: {self.hash[:20]}... | Transactions: {len(self.transactions)}"

