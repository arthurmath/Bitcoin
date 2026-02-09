


def afficher_soldes(simulation):
    print(f"\n{'-'*60}\n💰 SOLDES :\n{'-'*60}")
    print("\nUtilisateurs:")
    for user in simulation.utilisateurs:
        print(f"  {user.nom}: {simulation.mineurs[0].calculer_solde(simulation.blockchain, user.cle_publique):.2f} BTC")
    print("\nMineurs:")
    for mineur in simulation.mineurs:
        print(f"  {mineur.nom}: {simulation.mineurs[0].calculer_solde(simulation.blockchain, mineur.cle_publique):.2f} BTC")
    print()



def sauvegarder_blockchain(chain, fichier='blockchain.txt'):
    """Sauvegarde la blockchain dans un fichier texte"""
    
    with open(fichier, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("BLOCKCHAIN BITCOIN\n")
        f.write("="*80 + "\n\n")
        
        for bloc in chain:
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
    
    print(f"\n💾 Blockchain sauvegardée dans {fichier}")
    
