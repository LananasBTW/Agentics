from crewai import Agent, Task, Crew, Process
from langchain_community.chat_models import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun

# ==========================================
# BLOC 1 : LE MOTEUR ET OUTILS
# ==========================================

llm_local = ChatOllama(model="qwen2.5-coder:32b", base_url="http://localhost:11434")

# On prépare l'outil de recherche Web (gratuit, pas besoin de clé API)
outil_recherche = DuckDuckGoSearchRun()


# ==========================================
# BLOC 2 : AGENTS
# ==========================================
chercheur = Agent(
    role='Chercheur Senior en Technologies',
    goal='Trouver les documentations et informations les plus récentes sur internet pour résoudre le problème.',
    backstory='Tu es un expert pour fouiller le web, lire des documentations techniques et en extraire la substantifique moelle. Tu ne codes pas, tu analyses.',
    verbose=True,
    allow_delegation=False,
    tools=[outil_recherche],
    llm=llm_local
)

codeur = Agent(
    role='Développeur Senior & Architecte Python',
    goal='Écrire un code parfait, optimisé et commenté en se basant EXCLUSIVEMENT sur les recherches du Chercheur.',
    backstory='Tu es un développeur d\'élite. Tu ne codes jamais à l\'aveugle. Tu lis le rapport de recherche, tu réfléchis, et tu produis un code robuste.',
    verbose=True,
    allow_delegation=False,
    llm=llm_local
)


# ==========================================
# BLOC 3 : LA CRÉATION DES TÂCHES
# ==========================================
# Ce que le chercheur doit faire :
tache_recherche = Task(
    description='Cherche sur le web comment créer un script Python qui récupère le prix actuel du Bitcoin via une API publique et gratuite.',
    expected_output='Un résumé clair de l\'API à utiliser et les étapes pour faire la requête en Python.',
    agent=chercheur
)

# Ce que le codeur doit faire avec le travail du chercheur :
tache_code = Task(
    description='En utilisant le résumé fourni par le chercheur, écris le code Python complet, propre et commenté pour afficher le prix du Bitcoin.',
    expected_output='Le code source complet en Python, prêt à être exécuté par l\'utilisateur.',
    agent=codeur
)


# ==========================================
# BLOC 4 : LE LANCEMENT (Le workflow)
# ==========================================
# On rassemble les agents et les tâches dans une "Crew" (une équipe)
equipe = Crew(
    agents=[chercheur, codeur],
    tasks=[tache_recherche, tache_code],
    process=Process.sequential
)
resultat = equipe.kickoff()
print(resultat)