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
        return f"Transaction : {self.expediteur[:10]}... -> {self.destinataire[:10]}... : {self.montant} BTC"


