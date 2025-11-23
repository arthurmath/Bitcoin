import hashlib
import time
import json


class Bloc:
    def __init__(self, index, transactions, hash_precedent, difficulte=4):
        self.index = index
        self.transactions = transactions
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
        
        hashes_transactions = []
        for tx in self.transactions:
            if tx.hash_transaction:
                hashes_transactions.append(tx.hash_transaction)
            else:
                hashes_transactions.append(tx.calculer_hash())
        
        # Combinaison des hashes (version simplifiée de l'arbre de Merkle)
        merkle_content = ''.join(hashes_transactions)
        return hashlib.sha256(merkle_content.encode()).hexdigest()
    
    def calculer_header(self):
        """
        Construit le header du bloc :
        version || hash_bloc_précédent || racine_Merkle || timestamp || bits || nonce
        """
        version = "1"
        bits = str(self.difficulte)
        header = f"{version}{self.hash_precedent}{self.racine_merkle}{self.timestamp}{bits}{self.nonce}"
        return header
    
    def calculer_hash(self):
        """
        Calcule le hash du bloc avec double SHA256
        SHA256(SHA256(header))
        """
        header = self.calculer_header()
        hash1 = hashlib.sha256(header.encode()).digest()
        hash2 = hashlib.sha256(hash1).hexdigest()
        return hash2
    
    def miner_bloc(self):
        """
        Proof of Work : trouve un nonce tel que le hash commence par 'difficulte' zéros
        SHA256(SHA256(header)) < cible
        """
        cible = '0' * self.difficulte
        print(f"\n⛏️  Mining bloc {self.index}... (difficulté: {self.difficulte} zéros)")
        
        tentatives = 0
        while True:
            self.hash = self.calculer_hash()
            tentatives += 1
            
            # Vérifier si le hash commence par le nombre requis de zéros
            if self.hash.startswith(cible):
                print(f"✅ Bloc miné ! Hash: {self.hash}")
                print(f"   Nonce trouvé: {self.nonce} après {tentatives} tentatives")
                return self.hash
            
            self.nonce += 1
            
            # Affichage de progression
            if tentatives % 100000 == 0:
                print(f"   {tentatives} tentatives...")
    
    def est_valide(self):
        """Vérifie que le bloc est valide"""
        # Vérifier que le hash commence par le bon nombre de zéros
        cible = '0' * self.difficulte
        if not self.hash.startswith(cible):
            return False
        
        # Vérifier que le hash calculé correspond au hash stocké
        if self.calculer_hash() != self.hash:
            return False
        
        # Vérifier que toutes les transactions sont valides
        for tx in self.transactions:
            if not tx.est_valide():
                return False
        
        return True
    
    def to_dict(self):
        """Convertit le bloc en dictionnaire pour sauvegarde"""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'hash_precedent': self.hash_precedent,
            'hash': self.hash,
            'nonce': self.nonce,
            'difficulte': self.difficulte,
            'racine_merkle': self.racine_merkle,
            'transactions': [tx.to_dict() for tx in self.transactions]
        }
    
    def __str__(self):
        return f"Bloc #{self.index} | Hash: {self.hash[:20]}... | Transactions: {len(self.transactions)}"

