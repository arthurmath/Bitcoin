from objects.utilisateur import Utilisateur
from objects.transaction import Transaction
from objects.blockchain import Blockchain
from objects.mineur import Mineur
import random


def main():
    print("\n" + "="*80)
    print("🚀 SIMULATION DU RÉSEAU BITCOIN")
    print("="*80)
    
    # Configuration
    difficulte = 5  # Nombre de zéros requis au début du hash
    recompense_bloc = 3.125  # BTC

    # Création des utilisateurs
    alice = Utilisateur("Alice")
    bob = Utilisateur("Bob")
    charlie = Utilisateur("Charlie")
    diana = Utilisateur("Diana")
    
    utilisateurs = [alice, bob, charlie, diana]

    # Création des mineurs
    mineur1 = Mineur("Mineur_Alpha", alice.adresse)
    mineur2 = Mineur("Mineur_Beta", bob.adresse)
    
    mineurs = [mineur1, mineur2]

    # Création de la blockchain
    blockchain = Blockchain(difficulte=difficulte)
    
    # Création et minage du bloc genesis par le premier mineur avec les utilisateurs
    bloc_genesis = blockchain.creer_bloc_genesis(utilisateurs)
    bloc_genesis = mineur1.miner_bloc_genesis(bloc_genesis)
    blockchain.ajouter_bloc(bloc_genesis)


    print("\n" + "="*60)
    print("👥 Création des utilisateurs")
    print("="*60)
    
    for user in utilisateurs:
        user.afficher_info()
    
    print("\n" + "="*60)
    print("⛏️  Création des mineurs")
    print("="*60)
    
    for mineur in mineurs:
        mineur.afficher_info()



    
    # Simulation de transactions
    print("\n" + "="*80)
    print("📤 SIMULATION DE TRANSACTIONS")
    print("="*80)
    
    # Transaction 1: Alice envoie 1.5 BTC à Bob
    print("\n--- Transaction 1: Alice -> Bob (1.5 BTC) ---")
    tx1 = Transaction(alice.adresse, bob.adresse, 1.5, alice.cle_publique_hex)
    alice.signe(tx1)
    if blockchain.bloc_temporaire.ajouter_transaction(tx1):
        blockchain.transactions_en_attente.append(tx1)
        alice.solde_btc -= 1.5
        bob.solde_btc += 1.5
    
    # Transaction 2: Bob envoie 0.5 BTC à Charlie
    print("\n--- Transaction 2: Bob -> Charlie (0.5 BTC) ---")
    tx2 = Transaction(bob.adresse, charlie.adresse, 0.5, bob.cle_publique_hex)
    bob.signe(tx2)
    if blockchain.bloc_temporaire.ajouter_transaction(tx2):
        blockchain.transactions_en_attente.append(tx2)
        bob.solde_btc -= 0.5
        charlie.solde_btc += 0.5
    
    # Transaction 3: Charlie envoie 1.0 BTC à Diana
    print("\n--- Transaction 3: Charlie -> Diana (1.0 BTC) ---")
    tx3 = Transaction(charlie.adresse, diana.adresse, 1.0, charlie.cle_publique_hex)
    charlie.signe(tx3)
    if blockchain.bloc_temporaire.ajouter_transaction(tx3):
        blockchain.transactions_en_attente.append(tx3)
        charlie.solde_btc -= 1.0
        diana.solde_btc += 1.0
    
    # Transaction 4: Diana envoie 0.8 BTC à Alice
    print("\n--- Transaction 4: Diana -> Alice (0.8 BTC) ---")
    tx4 = Transaction(diana.adresse, alice.adresse, 0.8, diana.cle_publique_hex)
    diana.signe(tx4)
    if blockchain.bloc_temporaire.ajouter_transaction(tx4):
        blockchain.transactions_en_attente.append(tx4)
        diana.solde_btc -= 0.8
        alice.solde_btc += 0.8


    
    # Miner un bloc avec ces transactions
    print("\n" + "="*80)
    print("⛏️  MINAGE DES TRANSACTIONS")
    print("="*80)
    
    mineur_choisi = random.choice(mineurs)
    bloc = mineur_choisi.miner_bloc(
        transactions_en_attente=blockchain.transactions_en_attente.copy(),
        hash_dernier_bloc=blockchain.chaine[-1].hash,
        index_bloc=len(blockchain.chaine),
        recompense=recompense_bloc,
        difficulte=difficulte
    )
    
    # Les autres mineurs valident le bloc
    print("\n" + "="*60)
    print("✅ Validation par les autres mineurs")
    print("="*60)
    
    for mineur in mineurs:
        if mineur != mineur_choisi:
            mineur.valider(bloc, difficulte)
    
    # Ajouter le bloc à la blockchain
    blockchain.ajouter_bloc(bloc)




    
    # Quelques transactions supplémentaires
    print("\n" + "="*80)
    print("📤 NOUVELLES TRANSACTIONS")
    print("="*80)
    
    # Transaction 5: Alice envoie 2.0 BTC à Charlie
    print("\n--- Transaction 5: Alice -> Charlie (2.0 BTC) ---")
    tx5 = Transaction(alice.adresse, charlie.adresse, 2.0, alice.cle_publique_hex)
    alice.signe(tx5)
    if blockchain.bloc_temporaire.ajouter_transaction(tx5):
        blockchain.transactions_en_attente.append(tx5)
        alice.solde_btc -= 2.0
        charlie.solde_btc += 2.0
    
    # Transaction 6: Bob envoie 1.0 BTC à Diana
    print("\n--- Transaction 6: Bob -> Diana (1.0 BTC) ---")
    tx6 = Transaction(bob.adresse, diana.adresse, 1.0, bob.cle_publique_hex)
    bob.signe(tx6)
    if blockchain.bloc_temporaire.ajouter_transaction(tx6):
        blockchain.transactions_en_attente.append(tx6)
        bob.solde_btc -= 1.0
        diana.solde_btc += 1.0
    
    # Miner un autre bloc
    print("\n" + "="*80)
    print("⛏️  MINAGE DU BLOC SUIVANT")
    print("="*80)
    
    mineur_choisi = random.choice(mineurs)
    bloc = mineur_choisi.miner_bloc(
        transactions_en_attente=blockchain.transactions_en_attente.copy(),
        hash_dernier_bloc=blockchain.chaine[-1].hash,
        index_bloc=len(blockchain.chaine),
        recompense=recompense_bloc,
        difficulte=difficulte
    )
    blockchain.ajouter_bloc(bloc)





    
    # Affichage des soldes finaux
    print("\n" + "="*80)
    print("💰 SOLDES FINAUX")
    print("="*80)
    
    print("\nUtilisateurs:")
    for user in utilisateurs:
        print(f"  {user.nom}: {user.solde_btc:.2f} BTC")
    
    print("\nMineurs:")
    for mineur in mineurs:
        print(f"  {mineur.nom}: {mineur.solde_btc:.2f} BTC")
    
    # Sauvegarde de la blockchain
    blockchain.sauvegarder('blockchain.txt')
    
    print("\n" + "="*80)
    print("✅ SIMULATION TERMINÉE")
    print("="*80)


if __name__ == "__main__":
    main()
















# TODO : on doit vérifier si Alice possède assez de BTC sur la blockchain pour faire la transaction

# # Donner des BTC initiaux aux utilisateurs (simulé via minage)
# print("\n" + "="*60)
# print("💰 Distribution initiale de BTC via minage")
# print("="*60)

# # Miner quelques blocs pour donner des BTC aux utilisateurs
# for i in range(2):
#     mineur = random.choice(mineurs)
#     bloc = mineur.miner_bloc(
#         transactions_en_attente=[],
#         hash_dernier_bloc=blockchain.chaine[-1].hash,
#         index_bloc=len(blockchain.chaine),
#         recompense=recompense_bloc,
#         difficulte=difficulte
#     )
#     blockchain.ajouter_bloc(bloc)

# # Donner des BTC aux utilisateurs depuis les mineurs
# alice.solde_btc = 5.0
# bob.solde_btc = 3.0
# charlie.solde_btc = 2.0
# diana.solde_btc = 1.5


# print("\n" + "="*60)
# print("💸 Soldes initiaux des utilisateurs")
# print("="*60)
# for user in utilisateurs:
#     print(f"{user.nom}: {user.solde_btc} BTC")