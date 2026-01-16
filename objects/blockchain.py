from objects.bloc import Bloc
from typing import List


class Blockchain:
    def __init__(self):
        self.chain: List[Bloc] = []
    
    def ajouter_bloc(self, bloc):
        self.chain.append(bloc)
        print(f"✅ Bloc ajouté à la blockchain: {bloc}\n")

    def sauvegarder(self, fichier='blockchain.txt'):
        """Sauvegarde la blockchain dans un fichier texte"""
        print(f"\n💾 Sauvegarde de la blockchain dans {fichier}...")
        
        with open(fichier, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("BLOCKCHAIN BITCOIN\n")
            f.write("="*80 + "\n\n")
            
            for bloc in self.chain:
                f.write(f"\n{'='*80}\n")
                f.write(f"BLOC #{bloc.index}\n")
                f.write(f"{'='*80}\n")
                f.write(f"Hash précédent: {bloc.hash_precedent}\n")
                f.write(f"Hash bloc: {bloc.hash}\n")
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
    






    