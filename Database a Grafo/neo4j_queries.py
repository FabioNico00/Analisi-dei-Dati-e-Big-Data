"""
Interazione del database "Piattaforma di Formazione" con Neo4j.

Contiene 6 query:
  - 3 query Cypher standard
  - 3 query basate su Graph Data Science (GDS)

Esecuzione: python neo4j_queries.py
"""
import os
from neo4j import GraphDatabase

# --------------------------------------------------------------------------- #
# Configurazione connessione con Neo4j
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")

# ---------------------------------------------------------------------- #

class Neo4jConnector:
    """Wrapper per l'esecuzione delle query sul knowledge graph."""

    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def _run(self, query: str, parameters: dict = None):
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    # QUERY CYPHER STANDARD (1-3) #

    def corsi_collegati_ad_argomento(self, nome_argomento: str, max_hop: int = 3):
        """
        Query 1 (Cypher standard).
        Trova tutti i corsi collegati a un certo argomento, sia direttamente
        sia tramite catene di prerequisiti (fino a max_hop salti).
        """
        query = """
        MATCH (target:Argomento {nome: $nome_argomento})
        OPTIONAL MATCH (prereq:Argomento)-[:PREREQUISITO_DI*1..%d]->(target)
        WITH target, collect(DISTINCT prereq) + target AS argomentiRilevanti
        UNWIND argomentiRilevanti AS a
        MATCH (c:Corso)-[:TRATTA]->(a)
        RETURN DISTINCT c.id AS corso_id, c.titolo AS titolo, c.categoria AS categoria,
               c.livello AS livello, a.nome AS argomento_collegato
        ORDER BY c.categoria, c.titolo
        """ % max_hop
        return self._run(query, {"nome_argomento": nome_argomento})

    def corsi_consigliati_per_studente(self, matricola: str):
        """
        Query 2 (Cypher standard).
        Suggerisce corsi non ancora seguiti, il cui argomento è uno sviluppo
        naturale (prerequisito successivo) di ciò che lo studente ha già completato.
        """
        query = """
        MATCH (s:Studente {matricola: $matricola})-[:ISCRITTO_A {stato: "completato"}]->(:Corso)-[:TRATTA]->(a:Argomento)
        MATCH (a)-[:PREREQUISITO_DI]->(next:Argomento)<-[:TRATTA]-(consigliato:Corso)
        WHERE NOT (s)-[:ISCRITTO_A]->(consigliato)
        RETURN DISTINCT consigliato.id AS corso_id, consigliato.titolo AS titolo,
               consigliato.categoria AS categoria, next.nome AS argomento_da_approfondire
        """
        return self._run(query, {"matricola": matricola})

    def tasso_completamento_per_categoria(self):
        """
        Query 3 (Cypher standard).
        Calcola il tasso di completamento dei corsi raggruppato per categoria,
        utile come indicatore amministrativo generale.
        """
        query = """
        MATCH (s:Studente)-[r:ISCRITTO_A]->(c:Corso)
        WITH c.categoria AS categoria, r.stato AS stato, count(*) AS totale
        WITH categoria,
             sum(CASE WHEN stato = "completato" THEN totale ELSE 0 END) AS completati,
             sum(totale) AS iscrizioni_totali
        RETURN categoria, completati, iscrizioni_totali,
               round(100.0 * completati / iscrizioni_totali) AS percentuale_completamento
        ORDER BY percentuale_completamento DESC
        """
        return self._run(query)

    # QUERY GDS (4-6) #

    def _drop_graph_if_exists(self, graph_name: str):
        """Utility: elimina una proiezione GDS se già presente in memoria."""
        query = """
        CALL gds.graph.exists($graph_name) YIELD exists
        WITH exists
        WHERE exists
        CALL gds.graph.drop($graph_name) YIELD graphName
        RETURN graphName
        """
        self._run(query, {"graph_name": graph_name})

    def studenti_simili_node_similarity(self, top_n: int = 20):
        """
        Query 4 (GDS - Node Similarity).
        Individua studenti simili perché hanno seguito corsi che condividono
        gli stessi argomenti/corsi, usando l'algoritmo Node Similarity (Jaccard)
        al posto di un doppio MATCH manuale: più scalabile su grafi grandi.
        """
        graph_name = "studentiCorsi"
        self._drop_graph_if_exists(graph_name)

        project_query = """
        CALL gds.graph.project(
            $graph_name,
            ['Studente', 'Corso'],
            { ISCRITTO_A: { orientation: 'UNDIRECTED' } }
        )
        YIELD graphName, nodeCount, relationshipCount
        RETURN graphName, nodeCount, relationshipCount
        """
        self._run(project_query, {"graph_name": graph_name})

        similarity_query = """
        CALL gds.nodeSimilarity.stream($graph_name)
        YIELD node1, node2, similarity
        WITH gds.util.asNode(node1) AS s1, gds.util.asNode(node2) AS s2, similarity
        WHERE s1:Studente AND s2:Studente AND s1.matricola < s2.matricola
        RETURN s1.matricola AS matricola_1, s1.nome AS nome_1,
               s2.matricola AS matricola_2, s2.nome AS nome_2,
               similarity
        ORDER BY similarity DESC
        LIMIT $top_n
        """
        result = self._run(similarity_query, {"graph_name": graph_name, "top_n": top_n})

        self._drop_graph_if_exists(graph_name)
        return result

    def argomenti_centrali_pagerank(self, top_n: int = 10):
        """
        Query 5 (GDS - PageRank).
        Individua gli argomenti più "centrali" nella rete di prerequisiti:
        un argomento ha punteggio alto se è prerequisito (diretto o indiretto)
        di molti altri argomenti a loro volta importanti.
        """
        graph_name = "grafoArgomenti"
        self._drop_graph_if_exists(graph_name)

        project_query = """
        CALL gds.graph.project(
            $graph_name,
            'Argomento',
            'PREREQUISITO_DI'
        )
        YIELD graphName, nodeCount, relationshipCount
        RETURN graphName, nodeCount, relationshipCount
        """
        self._run(project_query, {"graph_name": graph_name})

        pagerank_query = """
        CALL gds.pageRank.stream($graph_name)
        YIELD nodeId, score
        RETURN gds.util.asNode(nodeId).nome AS argomento, score
        ORDER BY score DESC
        LIMIT $top_n
        """
        result = self._run(pagerank_query, {"graph_name": graph_name, "top_n": top_n})

        self._drop_graph_if_exists(graph_name)
        return result

    def comunita_corsi_louvain(self):
        """
        Query 6 (GDS - Louvain).
        Rileva comunità di corsi affini in base agli argomenti condivisi,
        anche oltre le categorie assegnate manualmente: utile per scoprire
        raggruppamenti tematici emergenti nel curriculum.
        """
        graph_name = "corsiArgomenti"
        self._drop_graph_if_exists(graph_name)

        project_query = """
        CALL gds.graph.project(
            $graph_name,
            ['Corso', 'Argomento'],
            { TRATTA: { orientation: 'UNDIRECTED' } }
        )
        YIELD graphName, nodeCount, relationshipCount
        RETURN graphName, nodeCount, relationshipCount
        """
        self._run(project_query, {"graph_name": graph_name})

        louvain_query = """
        CALL gds.louvain.stream($graph_name)
        YIELD nodeId, communityId
        WITH gds.util.asNode(nodeId) AS n, communityId
        WHERE n:Corso
        RETURN communityId, collect(n.titolo) AS corsi_nella_comunita
        ORDER BY size(corsi_nella_comunita) DESC
        """
        result = self._run(louvain_query, {"graph_name": graph_name})

        self._drop_graph_if_exists(graph_name)
        return result


def stampa_risultati(titolo: str, risultati: list):
    print(f"\n{'=' * 70}\n{titolo}\n{'=' * 70}")
    if not risultati:
        print("Nessun risultato.")
        return
    for riga in risultati:
        print(riga)


def main():
    connector = Neo4jConnector(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

    try:
        #  Query Cypher standard #
        stampa_risultati(
            "1. Corsi collegati all'argomento 'Query Cypher' (diretti o via prerequisiti)",
            connector.corsi_collegati_ad_argomento("Query Cypher"),
        )

        stampa_risultati(
            "2. Corsi consigliati per lo studente STU20230042",
            connector.corsi_consigliati_per_studente("STU20230042"),
        )

        stampa_risultati(
            "3. Tasso di completamento per categoria di corso",
            connector.tasso_completamento_per_categoria(),
        )

        #  Query GDS #
        stampa_risultati(
            "4. [GDS - Node Similarity] Studenti simili per argomenti condivisi",
            connector.studenti_simili_node_similarity(top_n=20),
        )

        stampa_risultati(
            "5. [GDS - PageRank] Argomenti più centrali nella rete di prerequisiti",
            connector.argomenti_centrali_pagerank(top_n=10),
        )

        stampa_risultati(
            "6. [GDS - Louvain] Comunità di corsi affini per argomenti condivisi",
            connector.comunita_corsi_louvain(),
        )

    finally:
        connector.close()


if __name__ == "__main__":
    main()
