# Simulation du Réseau Bitcoin

Ce projet propose une implémentation visuelle du réseau Bitcoin. L'interface est visible en éxecutant le code "interface_gemini.py". On explique ici le fonctionnement de la blockchain derrière le réseau Bitcoin (et d'autres cryptomonnaies).


### **1. Signature numérique**

Pour sécuriser les transactions, la blockchain Bitcoin utilise un système de cryptographie asymétrique permettant de démontrer que l’on connaît un secret sans avoir à dévoiler ce secret. Elle est basée sur un système à **clé privée** et **clé publique**.

Chaque utilisateur possède :
* **une clé privée** : un nombre aléatoire secret,
* **une clé publique** : dérivée de la clé privée.

Lorsqu’un utilisateur A envoie 3 BTC à un utilisateur B, on peut encoder cette transaction sous la forme du **Message** suivant : "cle_publique(A) -> 3 -> cle_publique(B)".

1. L'utilisateur A signe la transaction avec sa clé privée. Seul lui peut générer cette Signature car il est le seul à connaitre sa clé privée.
   → Sign(**Message**, clé privée A) = Signature

2. N’importe qui peut vérifier la signature d'une personne avec le message qu'elle a signé et sa clé publique.
    → Verify(**Message**, Signature, clé publique A) = True/Flase

Les deux fonctions Sign et Verify sont présentes dans la classe Utilisateur du code. Cela permet de confirmer l’authenticité de la transaction à partir de la clé publique de A et donc sans révéler sa clé privée. Ce mécanisme repose sur ECDSA (Elliptic Curve Digital Signature Algorithm).



### **2. Génération de la clé publique**

La clé publique (K) est calculée à partir de la clé privée (k) : K = k × G

avec :

* k = clé privée (entier),
* G = point générateur de la courbe,
* × = multiplication de point sur la courbe elliptique.


Bitcoin utilise la courbe elliptique secp256k1, définie par : y^2 = x^3 + 7 mod p
où p est un nombre premier très grand : 2^{256}−2^{32}−977 

Retrouver la clé privée (k) à partir de la clé publique (K) est équivalent à résoudre le problème du logarithme discret elliptique, réputé incalculable (dans des temps humainement raisonables) avec les moyens informatiques actuels.
C’est ce qui rend la clé privée impossible à deviner et protège la sécurité des transactions.




## Sécurisation de la Blockchain

### **1. Principe du Proof of Work**

Le réseau Bitcoin est sécurisé par un mécanisme de consensus appelé preuve de travail (Proof of work).
Des milliers de serveurs (mineurs) reçoivent les transactions et tentent de produire un bloc valide en résolvant un problème cryptographique : trouver un hash suffisamment petit. 

Une fonction de hachage prend une entrée du texte de taille arbitraire et produit une sortie de taille fixe. Cette sortie est déterministe (même entée = même sortie) et non reversible : il est impossible en pratique de retrouver l'entrée à partir de la sortie.


### **2. Rôle des mineurs**

Les mineurs regroupent les transactions récentes dans un bloc candidat et font varier un nombre (le nonce) pour obtenir un hash qui respecte la cible de difficulté.

Le calcul à satisfaire est : SHA256(SHA256(header du bloc + nonce)) < cible

Ils répètent donc :
while True:
    hash_val = SHA256(SHA256(block_header(nonce)))
    if hash_val < target:
        break
    else:
        nonce += 1

Exemple conceptuel : Cible = 0000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF  
Il faut trouver un hash (la cible) commençant par au moins quatre zéros (qu'importe les digits suivants). Les mineurs vont tester un grand nombre de valeurs du nonce jusqu'à ce qu'ils trouve celui qui permet d'atteindre le nombre de zéros du hash désiré. Trouver un tel hash est purement probabiliste : chaque essai a une probabilité de réussite d’environ 1 / 2^(nombre_de_bits_difficulté). Donc plus le nombre de zéros est grand, plus il faut d’essais. Le protocole Bitcoin ajuste la difficulté tous les 2016 blocs (environ toutes les deux semaines) pour maintenir un rythme d’un bloc toutes les 10 minutes en moyenne.


### **3. Structure d’un bloc**

Un bloc contient notamment :
* une liste de transactions (incluant la récompense du mineur),
* le hash du bloc précédent,
* un timestamp,
* une racine de Merkle (résumé cryptographique des transactions),
* un champ bits (difficulté encodée),
* un nonce.

Le mineur modifie le nonce pour tenter de rendre le hash du header inférieur à la cible.


### **4. Validation et récompense**

Lorsqu’un mineur trouve un bloc valide, il le diffuse au réseau. Il est ensuite facile pour les autres mineurs de vérifier que ce nonce est correct, et que donc ce bloc a été validé.

Le mineur reçoit alors :

* la **récompense de bloc** (3,125 BTC depuis le halving de 2024),
* les **frais de transaction** inclus dans ce bloc.


### **5. Comment cela garantit la sécurité**

Le Proof of Work rend les attaques énergétiquement coûteuses. Exemple : une tentative de falsification de la blockchain.
Si un attaquant veut modifier un bloc déjà validé :
    Il change une transaction → change le hash du bloc.
    Donc le lien avec le bloc suivant devient invalide.
    Il doit recalculer les hashs de tous les blocs suivants pour rattraper la chaîne honnête.

Mais pendant ce temps, le reste du réseau continue d’avancer. Modifier un bloc impliquerait de refaire tout ce calcul pour ce bloc et tous les suivants.
L’attaquant devrait donc disposer de > 50 % de la puissance de calcul totale pour espérer rattraper et surpasser la chaîne valide — c’est la fameuse attaque des 51 %, en pratique impossible à mener à grande échelle.