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


    def __str__(self):
        return f"{self.expediteur[:10]}... -> {self.destinataire[:10]}... : {self.montant} BTC"










    # def to_dict(self):
    #     """Convertit la transaction en dictionnaire"""
    #     return {
    #         'expediteur': self.expediteur,
    #         'destinataire': self.destinataire,
    #         'montant': self.montant,
    #         'cle_publique': self.cle_publique,
    #         'timestamp': self.timestamp,
    #         'signature': self.signature,
    #         'hash': self.hash_transaction
    #     }
    

