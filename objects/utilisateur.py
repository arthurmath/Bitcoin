import hashlib
from ecdsa import SigningKey, VerifyingKey, SECP256k1
import binascii
import random


class Utilisateur:
    def __init__(self, nom, adresse=None):
        self.nom = nom
        # Génération de la clé privée (nombre aléatoire secret)
        self.cle_privee = SigningKey.generate(curve=SECP256k1)
        # Dérivation de la clé publique à partir de la clé privée
        self.cle_publique = self.cle_privee.get_verifying_key()
        # Clé publique en format hexadécimal
        self.cle_publique_hex = binascii.hexlify(self.cle_publique.to_string()).decode('ascii')
        # Génération de l'adresse Bitcoin 
        if adresse:
            self.adresse = adresse
        else:
            self.adresse = hashlib.sha256(self.cle_publique.to_string()).hexdigest()
    
    def signe(self, transaction):
        """
        Signer une transaction avec la clé privée (ECDSA)
        """
        # Créer le message à partir des données de la transaction
        message = f"{transaction.expediteur}{transaction.destinataire}{transaction.montant}{transaction.timestamp}"
        message_bytes = message.encode('utf-8')
        signature = self.cle_privee.sign(message_bytes)
        # Stocker la signature dans la transaction
        transaction.signature = binascii.hexlify(signature).decode('ascii')
    
    def verifier_signature(cle_publique_hex, message, signature):
        """
        Vérifie une signature avec la clé publique
        Méthode statique car n'importe qui peut vérifier
        """
        try:
            cle_pub_bytes = binascii.unhexlify(cle_publique_hex)
            cle_publique = VerifyingKey.from_string(cle_pub_bytes, curve=SECP256k1)
            signature_bytes = binascii.unhexlify(signature)
            message_bytes = message.encode('utf-8')
            return cle_publique.verify(signature_bytes, message_bytes)
        except:
            return False
    
    def __str__(self):
        return f"{self.nom} ({self.adresse[:20]}...)"

