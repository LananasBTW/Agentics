import requests
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from duckduckgo_search import DDGS

# ==========================================
# 1. LE CERVEAU
# ==========================================
llm_local = LLM(
    model="ollama/qwen3.5:9b",
    base_url="http://localhost:11434"
)

# ==========================================
# 2. LES OUTILS DES AGENTS
# ==========================================

@tool("Recherche Web DuckDuckGo")
def outil_recherche(query: str) -> str:
    """Recherche des actualités récentes sur internet."""
    with DDGS() as ddgs:
        results = [r for r in ddgs.news(query, max_results=3)]
        return str(results) if results else "Aucune actualité trouvée."

@tool("Obtenir le prix actuel de la Crypto")
def obtenir_prix_crypto(crypto_id: str) -> str:
    """Obtient le prix actuel d'une cryptomonnaie en USD. Ex: 'bitcoin', 'ethereum'."""
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd"
    reponse = requests.get(url)
    return str(reponse.json())

# ==========================================
# 3. L'ÉQUIPE DU HEDGE FUND
# ==========================================
analyste = Agent(
    role='Analyste de Marché Crypto',
    goal='Récupérer le prix actuel exact et analyser le sentiment général des actualités du jour.',
    backstory='Tu es un expert en analyse de données. Tu ne prends aucune décision financière. Tu te contentes de donner les faits (le prix) et de résumer si les actualités sont positives (bullish) ou négatives (bearish).',
    verbose=True,
    allow_delegation=False,
    tools=[obtenir_prix_crypto, outil_recherche],
    llm=llm_local
)

trader = Agent(
    role='Trader Quantitatif Senior',
    goal='Prendre une décision claire (ACHETER, VENDRE ou ATTENDRE) basée sur le rapport de l\'analyste.',
    backstory='Tu es un trader d\'élite très prudent. Tu détestes perdre de l\'argent. Si les actualités sont mitigées ou mauvaises, tu préfères ATTENDRE. Tu justifies toujours ta décision en quelques phrases.',
    verbose=True,
    allow_delegation=False,
    llm=llm_local
)

# ==========================================
# 4. LA MISSION (Le marché d'aujourd'hui)
# ==========================================

crypto_cible = "bitcoin"

tache_analyse = Task(
    description=f'Trouve le prix actuel du {crypto_cible} en USD, puis cherche les 3 dernières actualités sur le {crypto_cible}. Fais un résumé du sentiment du marché.',
    expected_output='Un rapport contenant le prix exact, les titres des actualités, et le sentiment général (Peur, Neutre, ou Euphorie).',
    agent=analyste
)

tache_trading = Task(
    description='Lis le rapport de l\'analyste. Choisis une action parmi : [ACHETER, VENDRE, ATTENDRE]. Explique pourquoi en 3 lignes maximum.',
    expected_output='Action: [Ton choix]\nJustification: [Ton explication]',
    agent=trader
)

equipe_crypto = Crew(
    agents=[analyste, trader],
    tasks=[tache_analyse, tache_trading],
    process=Process.sequential
)

# ============================================
# 5. REPONSE
# ============================================

print(f"Démarrage de l'analyse pour le {crypto_cible.upper()}...")
resultat = equipe_crypto.kickoff()

print("\n\n================================================")
print("DÉCISION DU BOT DE TRADING :")
print("================================================")
print(resultat)
