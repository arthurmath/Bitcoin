import json
from bloc import Bloc
from transaction import Transaction


class Blockchain:
    def __init__(self, difficulte=4):
        self.chaine = []
        self.transactions_en_attente = []
        self.difficulte = difficulte
        self.creer_bloc_genesis()
    
    def creer_bloc_genesis(self):
        """Crée le premier bloc de la blockchain (bloc genesis)"""
        print("\n" + "="*60)
        print("🌟 Création du bloc Genesis")
        print("="*60)
        
        # Transaction genesis
        transaction_genesis = Transaction(
            expediteur_adresse="GENESIS",
            destinataire_adresse="GENESIS",
            montant=0,
            cle_publique_expediteur="SYSTEM"
        )
        transaction_genesis.hash_transaction = transaction_genesis.calculer_hash()
        
        bloc_genesis = Bloc(
            index=0,
            transactions=[transaction_genesis],
            hash_precedent="0" * 64,
            difficulte=self.difficulte
        )
        
        bloc_genesis.miner_bloc()
        self.chaine.append(bloc_genesis)
    
    def obtenir_dernier_bloc(self):
        """Retourne le dernier bloc de la chaîne"""
        return self.chaine[-1]
    
    def ajouter_transaction(self, transaction):
        """Ajoute une transaction à la liste des transactions en attente"""
        if transaction.est_valide():
            self.transactions_en_attente.append(transaction)
            print(f"✅ Transaction ajoutée: {transaction}")
            return True
        else:
            print(f"❌ Transaction invalide: {transaction}")
            return False
    
    def ajouter_bloc(self, bloc):
        """Ajoute un bloc à la chaîne après validation"""
        if bloc.est_valide() and bloc.hash_precedent == self.obtenir_dernier_bloc().hash:
            self.chaine.append(bloc)
            # Vider les transactions en attente qui ont été incluses
            self.transactions_en_attente = []
            print(f"✅ Bloc ajouté à la blockchain: {bloc}")
            return True
        else:
            print(f"❌ Bloc invalide, rejeté")
            return False
    
    def valider_chaine(self):
        """Vérifie l'intégrité de toute la blockchain"""
        print("\n🔍 Validation de la blockchain...")
        
        for i in range(1, len(self.chaine)):
            bloc_actuel = self.chaine[i]
            bloc_precedent = self.chaine[i-1]
            
            # Vérifier que le bloc est valide
            if not bloc_actuel.est_valide():
                print(f"❌ Bloc #{i} invalide")
                return False
            
            # Vérifier le chaînage
            if bloc_actuel.hash_precedent != bloc_precedent.hash:
                print(f"❌ Chaînage rompu au bloc #{i}")
                return False
        
        print(f"✅ Blockchain valide ({len(self.chaine)} blocs)")
        return True
    
    # def calculer_solde(self, adresse):
    #     """Calcule le solde d'une adresse en parcourant toute la blockchain"""
    #     solde = 0.0
        
    #     for bloc in self.chaine:
    #         for transaction in bloc.transactions:
    #             if transaction.destinataire == adresse:
    #                 solde += transaction.montant
    #             if transaction.expediteur == adresse:
    #                 solde -= transaction.montant
        
    #     return solde
    
    def sauvegarder(self, fichier='blockchain.txt'):
        """Sauvegarde la blockchain dans un fichier texte"""
        print(f"\n💾 Sauvegarde de la blockchain dans {fichier}...")
        
        with open(fichier, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("BLOCKCHAIN BITCOIN - SIMULATION\n")
            f.write("="*80 + "\n\n")
            
            for bloc in self.chaine:
                f.write(f"\n{'='*80}\n")
                f.write(f"BLOC #{bloc.index}\n")
                f.write(f"{'='*80}\n")
                f.write(f"Hash: {bloc.hash}\n")
                f.write(f"Hash précédent: {bloc.hash_precedent}\n")
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
        
        print(f"✅ Blockchain sauvegardée ({len(self.chaine)} blocs)")
    
    def afficher_resume(self):
        """Affiche un résumé de la blockchain"""
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DE LA BLOCKCHAIN")
        print("="*60)
        print(f"Nombre de blocs: {len(self.chaine)}")
        print(f"Difficulté: {self.difficulte}")
        print(f"Transactions en attente: {len(self.transactions_en_attente)}")
        print("\nDerniers blocs:")
        for bloc in self.chaine[-3:]:
            print(f"  - {bloc}")

