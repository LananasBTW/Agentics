import ccxt
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from duckduckgo_search import DDGS

# ==========================================
# 1. NOTRE PORTFEUILLE VIRTUEL
# ==========================================
class KrakenPaperTrader:
    def __init__(self, solde_initial_usd=5000.0):
        self.exchange = ccxt.kraken()
        self.portfolio = {"USD": solde_initial_usd, "BTC": 0.0}

    def obtenir_prix_actuel(self, symbole="BTC/USD"):
        ticker = self.exchange.fetch_ticker(symbole)
        return ticker['last']

    def executer_ordre(self, action: str, montant_usd: float, symbole="BTC/USD"):
        prix_actuel = self.obtenir_prix_actuel(symbole)
        action = action.upper()

        if action == "ACHETER":
            if self.portfolio["USD"] >= montant_usd:
                quantite = montant_usd / prix_actuel
                self.portfolio["USD"] -= montant_usd
                self.portfolio["BTC"] += quantite
                return f"SUCCÈS : Achat de {quantite:.4f} BTC pour {montant_usd}$. Prix unitaire: {prix_actuel}$"
            return "ÉCHEC : Fonds en USD insuffisants."
            
        elif action == "VENDRE":
            quantite = montant_usd / prix_actuel
            if self.portfolio["BTC"] >= quantite:
                self.portfolio["BTC"] -= quantite
                self.portfolio["USD"] += montant_usd
                return f"SUCCÈS : Vente de {quantite:.4f} BTC pour {montant_usd}$. Prix unitaire: {prix_actuel}$"
            return "ÉCHEC : Fonds en BTC insuffisants."
            
        return "Le mot doit être ACHETER ou VENDRE."

    def afficher_statut(self):
        prix_btc = self.obtenir_prix_actuel()
        valeur_totale = self.portfolio["USD"] + (self.portfolio["BTC"] * prix_btc)
        print("\n" + "="*40)
        print("🏦 STATUT FINAL DU PORTEFEUILLE 🏦")
        print("="*40)
        print(f"💵 USD Restants : {self.portfolio['USD']:.2f} $")
        print(f"🪙 BTC Possédés : {self.portfolio['BTC']:.4f} BTC")
        print(f"💰 VALEUR TOTALE: {valeur_totale:.2f} $")
        print("="*40 + "\n")

# On instancie notre broker avec 5000$
broker = KrakenPaperTrader()


# ==========================================
# 2. LES OUTILS DES AGENTS
# ==========================================

@tool("Recherche Actualites Crypto")
def outil_recherche(query: str) -> str:
    """Cherche les actualités récentes sur internet."""
    with DDGS() as ddgs:
        results = [r for r in ddgs.news(query, max_results=3)]
        return str(results) if results else "Aucune actualité."

@tool("Obtenir Prix Kraken")
def outil_prix(symbole: str) -> str:
    """Obtient le prix actuel exact d'une crypto sur Kraken (ex: 'BTC/USD')."""
    return str(broker.obtenir_prix_actuel(symbole))

@tool("Passer un Ordre de Trading")
def outil_trading(action: str, montant_usd: float) -> str:
    """
    Exécute un trade virtuel. 
    L'action DOIT être 'ACHETER' ou 'VENDRE'. 
    Le montant_usd est la somme en dollars à investir (ex: 500.0).
    """
    # L'agent IA va déclencher cette fonction tout seul !
    return broker.executer_ordre(action, float(montant_usd))


# ==========================================
# 3. LE CERVEAU ET LES AGENTS
# ==========================================

# Utilisation du modèle Qwen3.5:9b
llm_local = LLM(model="ollama/qwen3.5:9b", base_url="http://localhost:11434")

analyste = Agent(
    role='Analyste de Marché',
    goal='Récupérer le prix du BTC/USD et analyser les 3 dernières actualités sur le Bitcoin.',
    backstory='Tu es un expert data. Tu donnes les faits : le prix actuel et le sentiment du marché (Peur ou Confiance).',
    verbose=True,
    allow_delegation=False,
    tools=[outil_prix, outil_recherche],
    llm=llm_local
)

trader = Agent(
    role='Trader Quantitatif',
    goal='Lire le rapport de l\'analyste et exécuter un trade si l\'opportunité est bonne.',
    backstory='Tu es un trader agressif mais intelligent. Tu as 5000$ de budget. Si les nouvelles sont bonnes, tu utilises l\'outil de trading pour ACHETER pour 500$. Si elles sont mauvaises, tu VENDS ou tu ne fais rien.',
    verbose=True,
    allow_delegation=False,
    tools=[outil_trading],
    llm=llm_local
)

# ==========================================
# 4. LES MISSIONS
# ==========================================

tache_analyse = Task(
    description='Utilise tes outils pour trouver le prix actuel de "BTC/USD" et les actus "Bitcoin crypto". Rédige un résumé du sentiment du marché.',
    expected_output='Rapport complet avec le prix et la tendance du marché.',
    agent=analyste
)

tache_trading = Task(
    description='Lis le rapport de l\'analyste. Si la tendance est positive, utilise l\'outil de trading pour ACHETER 500$ de Bitcoin. Explique ton choix ensuite.',
    expected_output='Explication de la décision prise et confirmation de l\'utilisation de l\'outil.',
    agent=trader
)

equipe = Crew(
    agents=[analyste, trader],
    tasks=[tache_analyse, tache_trading],
    process=Process.sequential
)

# ==========================================
# 5. LE LANCEMENT
# ==========================================

print("Lancement de la simulation de Trading...")
equipe.kickoff()

# Combien le broker nous renvoie 
broker.afficher_statut()
