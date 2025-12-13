from objects.bloc import Bloc
from objects.transaction import Transaction
from objects.utilisateur import Utilisateur
import random


class Blockchain:
    def __init__(self):
        self.chaine = []
    

    def creer_bloc_genesis(self, utilisateurs=None):
        """Crée le premier bloc de la blockchain (bloc genesis) sans le miner"""
        print("\n" + "="*60)
        print("🌟 Création du bloc Genesis")
        print("="*60)
        
        # Transactions Genesis permettent d'initialiser les soldes des utilisateurs
        transactions_genesis = [Transaction(
            expediteur=Utilisateur("GENESIS"),
            destinataire=user,
            montant=random.uniform(10, 100),
            cle_publique_expediteur="SYSTEM"
        ) for user in utilisateurs]
         
        bloc_genesis = Bloc(
            index=0,
            transactions=transactions_genesis,
            hash_precedent="0" * 64,
            difficulte=2
        )

        return bloc_genesis
    
    def ajouter_bloc(self, bloc):
        """Ajoute un bloc à la chaîne après validation"""
        self.chaine.append(bloc)
        print(f"✅ Bloc ajouté à la blockchain: {bloc}\n")

    
    def calculer_solde(self, adresse):
        """Calcule le solde d'une adresse en parcourant toute la blockchain"""
        solde = 0.0
        
        for bloc in self.chaine:
            for transaction in bloc.transactions:
                if transaction.destinataire.adresse == adresse:
                    solde += transaction.montant
                if transaction.expediteur.adresse == adresse:
                    solde -= transaction.montant
        
        return solde
    

    def sauvegarder(self, fichier='blockchain.txt'):
        """Sauvegarde la blockchain dans un fichier texte"""
        print(f"\n💾 Sauvegarde de la blockchain dans {fichier}...")
        
        with open(fichier, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("BLOCKCHAIN BITCOIN\n")
            f.write("="*80 + "\n\n")
            
            for bloc in self.chaine:
                f.write(f"\n{'='*80}\n")
                f.write(f"BLOC #{bloc.index}\n")
                f.write(f"{'='*80}\n")
                f.write(f"Hash précédent: {bloc.hash_precedent}\n")
                f.write(f"Hash: {bloc.hash}\n")
                f.write(f"Timestamp: {bloc.timestamp}\n")
                f.write(f"Nonce: {bloc.nonce}\n")
                f.write(f"Difficulté: {bloc.difficulte}\n")
                f.write(f"Racine Merkle: {bloc.racine_merkle}\n")
                f.write(f"\nTransactions ({len(bloc.transactions)}):\n")
                f.write("-"*80 + "\n")
                
                for i, tx in enumerate(bloc.transactions, 1):
                    f.write(f"\nTransaction #{i}:\n")
                    f.write(f"  Expéditeur: {tx.expediteur}\n")
                    f.write(f"  Destinataire: {tx.destinataire}\n")
                    f.write(f"  Montant: {tx.montant} BTC\n")
                    f.write(f"  Hash: {tx.hash_transaction}\n")
                    if tx.signature:
                        f.write(f"  Signature: {tx.signature[:50]}...\n")
                f.write("\n")
        
        print(f"✅ Blockchain sauvegardée")
    






    