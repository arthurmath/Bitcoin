from objects.bloc import Bloc
from objects.transaction import Transaction


class Blockchain:
    def __init__(self, difficulte=4):
        self.chaine = []
        self.transactions_en_attente = []
        self.difficulte = difficulte
        self.bloc_temporaire = None
    

    def creer_bloc_genesis(self, utilisateurs=None):
        """Crée le premier bloc de la blockchain (bloc genesis) sans le miner"""
        print("\n" + "="*60)
        print("🌟 Création du bloc Genesis")
        print("="*60)
        
        # Transactions Genesis permettent d'initialiser les soldes des utilisateurs
        transactions_genesis = [Transaction(
            expediteur_adresse="GENESIS",
            destinataire_adresse=user.adresse,
            montant=user.solde_btc,
            cle_publique_expediteur="SYSTEM"
        ) for user in utilisateurs]
         
        bloc_genesis = Bloc(
            index=0,
            transactions=transactions_genesis,
            hash_precedent="0" * 64,
            difficulte=self.difficulte
        )

        return bloc_genesis
    
    def _initialiser_bloc_temporaire(self):
        """Crée ou recrée le bloc temporaire pour accumuler les transactions"""
        if len(self.chaine) > 0:
            self.bloc_temporaire = Bloc(
                index=len(self.chaine),
                transactions=[],
                hash_precedent=self.chaine[-1].hash,
                difficulte=self.difficulte
            )
    
    def ajouter_bloc(self, bloc):
        """Ajoute un bloc à la chaîne après validation"""
        self.chaine.append(bloc)
        # Vider le mempool
        self.transactions_en_attente = []
        # Réinitialiser le bloc temporaire
        self._initialiser_bloc_temporaire()
        print(f"✅ Bloc ajouté à la blockchain: {bloc}\n")
    

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
        
        print(f"✅ Blockchain sauvegardée")
    





    # def valider_chaine(self):
    #     """Vérifie l'intégrité de toute la blockchain"""
    #     print("\n🔍 Validation de la blockchain...")
        
    #     for i in range(1, len(self.chaine)):
    #         bloc_actuel = self.chaine[i]
    #         bloc_precedent = self.chaine[i-1]
            
    #         # Vérifier que le bloc est valide
    #         if not bloc_actuel.est_valide():
    #             print(f"\n❌ Bloc #{i} invalide")
    #             return False
            
    #         # Vérifier le chaînage
    #         if bloc_actuel.hash_precedent != bloc_precedent.hash:
    #             print(f"\n❌ Chaînage rompu au bloc #{i}")
    #             return False
        
    #     print(f"\n✅ Blockchain valide ({len(self.chaine)} blocs)\n")
    #     return True
    
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
    