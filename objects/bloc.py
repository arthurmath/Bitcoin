import hashlib
import time
from typing import List
from objects.transaction import Transaction


class Bloc:
    def __init__(self, index, transactions, hash_precedent, difficulte=4):
        self.index = index
        self.transactions: List[Transaction] = transactions
        self.hash_precedent = hash_precedent
        self.timestamp = time.time()
        self.difficulte = difficulte
        self.nonce = 0
        self.racine_merkle = self._calculer_racine_merkle()
        self.hash = None
    
    def _calculer_racine_merkle(self):
        """
        Calcule la racine de Merkle (résumé cryptographique des transactions)
        Simplifié : hash de la concaténation des hash de toutes les transactions
        """
        if not self.transactions:
            return hashlib.sha256(b'').hexdigest()
        
        hashes_transactions = [tx.hash_transaction for tx in self.transactions]
        
        # Combinaison des hashes (version simplifiée de l'arbre de Merkle)
        merkle_content = ''.join(hashes_transactions)
        return hashlib.sha256(merkle_content.encode()).hexdigest()
    
    def header(self, nonce):
        """
        Construit le header du bloc :
        version || hash_bloc_précédent || racine_Merkle || timestamp || bits || nonce
        """
        version = "1"
        bits = str(self.difficulte)
        header = f"{version}{self.hash_precedent}{self.racine_merkle}{self.timestamp}{bits}{nonce}"
        return header.encode()
    
    def ajouter_transaction(self, transaction):
        """Ajoute une transaction au bloc et recalcule la racine de Merkle"""
        self.transactions.append(transaction)
        self.racine_merkle = self._calculer_racine_merkle()
        return True
            
    def __str__(self):
        return f"Bloc #{self.index} | Hash: {self.hash[:20]}... | Transactions: {len(self.transactions)}"


