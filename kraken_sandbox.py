import ccxt
import json

class KrakenPaperTrader:
    def __init__(self, solde_initial_usd=10000.0):
        self.exchange = ccxt.kraken()
        
        self.portfolio = {
            "USD": solde_initial_usd,
            "BTC": 0.0
        }
        self.historique_ordres = []

    def obtenir_prix_actuel(self, symbole="BTC/USD"):
        """Récupère le VRAI prix actuel sur Kraken"""
        ticker = self.exchange.fetch_ticker(symbole)
        return ticker['last']

    def executer_ordre(self, action: str, montant_usd: float, symbole="BTC/USD"):
        """Simule un achat ou une vente avec nos faux dollars"""
        prix_actuel = self.obtenir_prix_actuel(symbole)
        action = action.upper()

        if action == "ACHETER":
            if self.portfolio["USD"] >= montant_usd:
                quantite_crypto = montant_usd / prix_actuel
                self.portfolio["USD"] -= montant_usd
                self.portfolio["BTC"] += quantite_crypto
                message = f"ACHAT SIMULÉ : {quantite_crypto:.4f} BTC pour {montant_usd}$ (Prix: {prix_actuel}$/BTC)"
            else:
                message = "ERREUR : Fonds en USD insuffisants."

        elif action == "VENDRE":
            # On vend la quantité de BTC équivalente au montant en USD demandé
            quantite_a_vendre = montant_usd / prix_actuel
            if self.portfolio["BTC"] >= quantite_a_vendre:
                self.portfolio["BTC"] -= quantite_a_vendre
                self.portfolio["USD"] += montant_usd
                message = f"VENTE SIMULÉE : {quantite_a_vendre:.4f} BTC pour {montant_usd}$ (Prix: {prix_actuel}$/BTC)"
            else:
                message = "ERREUR : Fonds en BTC insuffisants."
        
        else:
            message = "Action ignorée (ATTENDRE)."

        # On enregistre pour un potentiel dashboard (TODO)
        self.historique_ordres.append({"action": action, "detail": message, "portefeuille": self.portfolio.copy()})
        return message

    def afficher_statut(self):
        prix_btc = self.obtenir_prix_actuel()
        valeur_totale = self.portfolio["USD"] + (self.portfolio["BTC"] * prix_btc)
        print("\n--- 🏦 STATUT DU PORTEFEUILLE VIRTUEL ---")
        print(f"💵 USD en caisse : {self.portfolio['USD']:.2f} $")
        print(f"🪙 BTC en caisse : {self.portfolio['BTC']:.4f} BTC")
        print(f"💰 VALEUR TOTALE : {valeur_totale:.2f} $")
        print("-----------------------------------------\n")


# Test si on lance le fichier
# Intialisation avec 1000 dollars
if __name__ == "__main__":
    broker = KrakenPaperTrader(solde_initial_usd=5000)
    print(f"Prix du Bitcoin sur Kraken : {broker.obtenir_prix_actuel()} $")
    print(broker.executer_ordre("ACHETER", 1000))
    broker.afficher_statut()
