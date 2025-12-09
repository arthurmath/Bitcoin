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
        print(f"Transaction: {transaction}")
        return True
            
    def __str__(self):
        return f"Bloc #{self.index} | Hash: {self.hash[:20]}... | Transactions: {len(self.transactions)}"









    # def est_valide(self):
    #     """Vérifie que le bloc est valide"""
    #     # Vérifier que le hash commence par le bon nombre de zéros
    #     cible = '0' * self.difficulte
    #     if not self.hash.startswith(cible):
    #         return False
        
    #     # # Vérifier que le hash calculé correspond au hash stocké
    #     # if self.calculer_hash() != self.hash:
    #     #     return False
        
    #     # Vérifier que toutes les transactions sont valides
    #     for tx in self.transactions:
    #         if not tx.est_valide():
    #             return False
        
    #     return True

        
    # def to_dict(self):
    #     """Convertit le bloc en dictionnaire pour sauvegarde"""
    #     return {
    #         'index': self.index,
    #         'timestamp': self.timestamp,
    #         'hash_precedent': self.hash_precedent,
    #         'hash': self.hash,
    #         'nonce': self.nonce,
    #         'difficulte': self.difficulte,
    #         'racine_merkle': self.racine_merkle,
    #         'transactions': [tx.to_dict() for tx in self.transactions]
    #     }
    
