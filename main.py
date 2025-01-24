import os
import sys

def choisir_et_executer_script():
    fichiers = sorted(f for f in os.listdir()
                      if f.endswith('.py') and f != 'main.py')
    if not fichiers:
        return print("\033[91m\nAucun script disponible.\033[0m")

    print("\n\033[90m===== Scripts Disponibles =====\033[0m")
    for i, f in enumerate(fichiers, 1):
        print(f"\033[94m{i}.\033[0m \033[31;5;150m{f}\033[0m")
    print("\033[90m===============================\033[0m")
    print("\n\033[90m============ Infos ============\033[0m")
    print("\033[90mLe script 'classique' contient le jeu avec les cartes rectangulaires comme initialement demandé. \nLe script 'formes' contient une version du jeu avec des formes de cartes variées. \033[0m")


    try:
        choix = int(
            input("\n\033[94mEntrez le numéro du script à exécuter : \033[0m")
        ) - 1
        if choix < 0 or choix >= len(fichiers):
            raise ValueError
        print(f"\n\033[95mExécution de {fichiers[choix]}...\033[0m\n")

        # Utilisez "python" ou "python3" selon la plateforme
        commande_python = "python3" if sys.platform != "win32" else "python"
        os.system(f'{commande_python} "{fichiers[choix]}"')
    except (ValueError, IndexError):
        print("\033[91m\nEntrée invalide. Veuillez réessayer.\033[0m")


if __name__ == "__main__":
    choisir_et_executer_script()