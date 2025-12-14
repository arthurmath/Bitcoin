"""Code to measure the influence of difficulty on mining time """

from objects.utilisateur import Utilisateur
from objects.transaction import Transaction
from objects.blockchain import Blockchain
from objects.mineur import Mineur
from typing import List
import random
import time
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np





# Configuration
difficulte = 5
recompense_bloc = 3.125
max_transactions_par_bloc = 10

# Créer 10 utilisateurs
noms = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Satoshi", "Henry", "Iris", "Jack"]
utilisateurs = [Utilisateur(nom) for nom in noms]

# Créer 4 mineurs
mineurs = [
    Mineur("Mineur_Alpha"),
    Mineur("Mineur_Beta"),
    Mineur("Mineur_Gamma"),
    Mineur("Mineur_Delta")
]

# Initialiser la blockchain
blockchain = Blockchain()
bloc_genesis = blockchain.creer_bloc_genesis(utilisateurs)
bloc_genesis = mineurs[0].miner_bloc(bloc_genesis.transactions)
blockchain.ajouter_bloc(bloc_genesis)

# Liste des transactions en attente
mempool: List[Transaction] = []



expediteur = random.choice(utilisateurs)
destinataire = random.choice([u for u in utilisateurs if u != expediteur])
montant = 1
tx = Transaction(expediteur, destinataire, montant, expediteur.cle_publique_hex)
expediteur.signe(tx)
mempool.append(tx)


    




n = 4
exec_times: List[List] = []

for i in range(1, n+1):
    print(f"\n\nItération {i}/{n}\n")
    exec_times_i = []
    for _ in range(10):
        start = time.time()
        bloc = mineurs[0].miner_bloc(
            transactions_en_attente=mempool,
            hash_dernier_bloc=blockchain.chaine[-1].hash,
            index_bloc=len(blockchain.chaine),
            difficulte=i,
        )
        exec_times_i.append(time.time() - start)
    exec_times.append(exec_times_i)






# Calculer la moyenne/min/max sur les temps d'exécution
means = [np.mean(t) for t in exec_times]
stds = [np.std(t) for t in exec_times]
mins = [min(t) for t in exec_times]
maxs = [max(t) for t in exec_times]
x = np.arange(1, len(exec_times) + 1)

fig, ax = plt.subplots()

# Afficher l'écart-type des temps d'exécution sous forme de barre verticale
for i, (xi, mean, std, min_val, max_val) in enumerate(zip(x, means, stds, mins, maxs)):
    ax.vlines(xi, max(min_val, mean - std), min(max_val, mean + std), color='purple', alpha=0.7, linewidth=2, label="Moyenne ± Écart-type" if i == 0 else "")

# Scatter sur min/max
ax.scatter(x, mins, color='tab:red', marker='_', s=100, label="Min" if any(mins) else "")
ax.scatter(x, maxs, color='tab:green', marker='_', s=100, label="Max" if any(maxs) else "")

ax.xaxis.set_major_locator(MaxNLocator(integer=True))
ax.plot(x, means, marker='o', label="Durée Moyenne", color="tab:blue")
ax.set_yscale('log')
ax.set_xlabel('Difficulté')
ax.set_ylabel('Durée (en s)')
ax.tick_params(axis='y')
ax.legend()
plt.grid(True, which="both", ls="-", alpha=0.5)
plt.title("Durée moyenne & écarts types")
# plt.savefig("images/execution_times_difficulty_log.png")
plt.show()

