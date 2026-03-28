from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from duckduckgo_search import DDGS

# ==========================================
# 1. CONNEXION À OLLAMA
# ==========================================
llm_local = LLM(
    model="ollama/qwen2.5-coder:32b",
    base_url="http://localhost:11434"
)

# ==========================================
# 2. CRÉATION DE L'OUTIL DE RECHERCHE
# ==========================================
@tool("Recherche Web DuckDuckGo")
def outil_recherche(query: str) -> str:
    """Utile pour rechercher des informations récentes sur internet. Prends en entrée une requête de recherche (string)."""
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, max_results=3)]
        return str(results) if results else "Aucun résultat trouvé."

# ==========================================
# 3. L'ÉQUIPE (Les Agents)
# ==========================================
chercheur = Agent(
    role='Chercheur Senior en Technologies',
    goal='Trouver les documentations et informations les plus récentes sur internet pour résoudre le problème.',
    backstory='Tu es un expert pour fouiller le web. Tu ne codes pas, tu analyses les docs techniques.',
    verbose=True,
    allow_delegation=False,
    tools=[outil_recherche],
    llm=llm_local
)

codeur = Agent(
    role='Développeur Senior & Architecte Python',
    goal='Écrire un code parfait et commenté en se basant EXCLUSIVEMENT sur les recherches du Chercheur.',
    backstory='Tu es un développeur d\'élite. Tu ne codes jamais à l\'aveugle. Tu produis un code robuste basé sur le rapport.',
    verbose=True,
    allow_delegation=False,
    llm=llm_local
)

# ==========================================
# 4. LES TÂCHES ET LE LANCEMENT
# ==========================================
tache_recherche = Task(
    description='Cherche sur le web comment créer un script Python qui récupère le prix actuel du Bitcoin via une API publique et gratuite.',
    expected_output='Un résumé clair de l\'API à utiliser et les étapes pour faire la requête en Python.',
    agent=chercheur
)

tache_code = Task(
    description='En utilisant le résumé fourni par le chercheur, écris le code Python complet, propre et commenté pour afficher le prix du Bitcoin.',
    expected_output='Le code source complet en Python, prêt à être exécuté par l\'utilisateur.',
    agent=codeur
)

equipe = Crew(
    agents=[chercheur, codeur],
    tasks=[tache_recherche, tache_code],
    process=Process.sequential
)

print("Démarrage de l'équipe d'agents...")
resultat = equipe.kickoff()

print("\n\n================================================")
print("RÉSULTAT FINAL PRODUIT PAR TON ÉQUIPE :")
print("================================================")
print(resultat)
