import hashlib
import time


class Transaction:
    def __init__(self, expediteur_adresse, destinataire_adresse, montant, cle_publique_expediteur):
        self.expediteur = expediteur_adresse
        self.destinataire = destinataire_adresse
        self.montant = montant
        self.cle_publique = cle_publique_expediteur
        self.timestamp = time.time()
        self.contenu = f"{self.expediteur}{self.destinataire}{self.montant}{self.timestamp}"
        self.hash_transaction = hashlib.sha256(self.contenu.encode()).hexdigest()
        self.signature = None
    
    def est_valide(self):
        """Vérifie que la transaction est valide"""
        # Transaction de récompense (coinbase) ou genesis n'a pas d'expéditeur réel
        if self.expediteur in ["COINBASE", "GENESIS"]:
            return True
        
        # Vérifier que la transaction est signée
        if not self.signature:
            return False
        
        # Vérifier la signature avec la clé publique
        from objects.utilisateur import Utilisateur
        return Utilisateur.verifier_signature(self.cle_publique, self.contenu, self.signature)
    
    def to_dict(self):
        """Convertit la transaction en dictionnaire"""
        return {
            'expediteur': self.expediteur,
            'destinataire': self.destinataire,
            'montant': self.montant,
            'cle_publique': self.cle_publique,
            'timestamp': self.timestamp,
            'signature': self.signature,
            'hash': self.hash_transaction
        }
    
    def __str__(self):
        return f"{self.expediteur[:10]}... -> {self.destinataire[:10]}... : {self.montant} BTC"







# def calculer_hash(self):
#     """Calcule le hash de la transaction"""
#     contenu = f"{self.expediteur}{self.destinataire}{self.montant}{self.timestamp}"
#     return hashlib.sha256(contenu.encode()).hexdigest()