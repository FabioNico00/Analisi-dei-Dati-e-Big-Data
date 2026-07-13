"""
Script di interazione con Elasticsearch per Sentiment Analysis su commenti social (indice "commenti_social").

6 query relative a temi di interesse per l'ente committente:
  1 - Reputazione generale e sua evoluzione nel tempo
  2 - Gestione delle crisi reputazionali (crisis management)
  3 - Individuazione dei "pain point" ricorrenti per reparto aziendale
  4 - Confronto tra piattaforme (channel performance)
  5 - Efficacia delle iniziative aziendali (pre/post release, promozioni)
  6 - Identificazione degli utenti più impattanti (influencer/detrattori)
"""



# ---------------------------------------------------------------------
from elasticsearch import Elasticsearch
from datetime import datetime

# ---------------------------------------------------------------------
# Configurazione connessione
ES_HOST = "http://localhost:9200"
INDEX = "commenti_social"

es = Elasticsearch(ES_HOST)

def stampa_intestazione(titolo):
    print("\n" + "=" * 70)
    print(titolo)
    print("=" * 70)


# ---------------------------------------------------------------------
# TEMA 1: Reputazione generale e sua evoluzione nel tempo
def query_1_andamento_mensile():
    stampa_intestazione("TEMA 1 - Andamento mensile del sentiment")

    body = {
        "size": 0,
        "aggs": {
            "andamento_mensile": {
                "date_histogram": {
                    "field": "data_commento",
                    "calendar_interval": "month",
                    "format": "yyyy-MM"
                },
                "aggs": {
                    "sentiment_medio": {
                        "avg": {"field": "punteggio_sentiment"}
                    },
                    "distribuzione_sentiment": {
                        "terms": {"field": "sentiment"}
                    },
                    "volume_commenti": {
                        "value_count": {"field": "id_commento"}
                    }
                }
            }
        }
    }

    risposta = es.search(index=INDEX, body=body)
    buckets = risposta["aggregations"]["andamento_mensile"]["buckets"]

    for b in buckets:
        mese = b["key_as_string"]
        volume = b["volume_commenti"]["value"]
        media = round(b["sentiment_medio"]["value"], 3) if b["sentiment_medio"]["value"] is not None else None
        distribuzione = {d["key"]: d["doc_count"] for d in b["distribuzione_sentiment"]["buckets"]}
        print(f"{mese} | volume: {volume:3d} | sentiment medio: {media:+.3f} | {distribuzione}")


# ---------------------------------------------------------------------
# TEMA 2: Gestione delle crisi reputazionali
def query_2_crisi(soglia_sentiment=-0.5, soglia_like=100):
    stampa_intestazione("TEMA 2 - Commenti critici ad alto impatto")

    body = {
        "query": {
            "bool": {
                "filter": [
                    {"range": {"punteggio_sentiment": {"lte": soglia_sentiment}}},
                    {"range": {"num_like": {"gte": soglia_like}}}
                ]
            }
        },
        "sort": [
            {"num_like": "desc"},
            {"punteggio_sentiment": "asc"}
        ]
    }

    risposta = es.search(index=INDEX, body=body)
    hits = risposta["hits"]["hits"]

    print(f"Trovati {len(hits)} commenti critici (sentiment <= {soglia_sentiment}, like >= {soglia_like})\n")
    for h in hits:
        s = h["_source"]
        print(f"[{s['piattaforma']:9s}] {s['num_like']:4d} like | score {s['punteggio_sentiment']:+.2f} "
              f"| {s['utente_handle']}: {s['testo_commento'][:80]}...")


# ---------------------------------------------------------------------
# TEMA 3: Individuazione dei "pain point" ricorrenti per reparto
# ---------------------------------------------------------------------
def query_3_pain_point():
    stampa_intestazione("TEMA 3 - Pain point ricorrenti (topic più associati a sentiment negativo)")

    body = {
        "size": 0,
        "query": {
            "term": {"sentiment": "negativo"}
        },
        "aggs": {
            "pain_point_per_hashtag": {
                "terms": {
                    "field": "hashtag",
                    "size": 20,
                    "order": {"_count": "desc"}
                },
                "aggs": {
                    "sentiment_medio_topic": {
                        "avg": {"field": "punteggio_sentiment"}
                    }
                }
            }
        }
    }

    risposta = es.search(index=INDEX, body=body)
    buckets = risposta["aggregations"]["pain_point_per_hashtag"]["buckets"]

    # Esclude l'hashtag del brand stesso (es. "TechNova")

    buckets_topic = [b for b in buckets if b["key"].lower() != "technova"]

    print(f"{'Topic':20s} | {'Commenti negativi':18s} | Sentiment medio topic")
    print("-" * 65)
    for b in buckets_topic:
        topic = b["key"]
        volume_negativo = b["doc_count"]
        media = round(b["sentiment_medio_topic"]["value"], 3)
        print(f"{topic:20s} | {volume_negativo:18d} | {media:+.3f}")

    stampa_intestazione("TEMA 3b - Incidenza negativa per topic (su volume totale)")

    body_generale = {
        "size": 0,
        "aggs": {
            "topic_generale": {
                "terms": {
                    "field": "hashtag",
                    "size": 20,
                    "order": {"_count": "desc"}
                },
                "aggs": {
                    "sentiment_medio": {"avg": {"field": "punteggio_sentiment"}},
                    "percentuale_negativi": {
                        "filter": {"term": {"sentiment": "negativo"}}
                    }
                }
            }
        }
    }

    risposta = es.search(index=INDEX, body=body_generale)
    buckets = risposta["aggregations"]["topic_generale"]["buckets"]
    buckets_topic = [b for b in buckets if b["key"].lower() != "technova"]

    print(f"{'Topic':20s} | {'Volume tot.':11s} | {'% negativi':10s} | Sentiment medio")
    print("-" * 65)
    for b in buckets_topic:
        topic = b["key"]
        volume_totale = b["doc_count"]
        volume_negativo = b["percentuale_negativi"]["doc_count"]
        percentuale = round((volume_negativo / volume_totale) * 100, 1) if volume_totale else 0
        media = round(b["sentiment_medio"]["value"], 3)
        print(f"{topic:20s} | {volume_totale:11d} | {percentuale:9.1f}% | {media:+.3f}")


# ---------------------------------------------------------------------
# TEMA 4: Confronto tra piattaforme
# ---------------------------------------------------------------------
def query_4_confronto_piattaforme():
    stampa_intestazione("TEMA 4 - Confronto tra piattaforme")

    body = {
        "size": 0,
        "aggs": {
            "per_piattaforma": {
                "terms": {"field": "piattaforma"},
                "aggs": {
                    "sentiment_medio": {"avg": {"field": "punteggio_sentiment"}},
                    "distribuzione_sentiment": {"terms": {"field": "sentiment"}},
                    "engagement_medio": {"avg": {"field": "num_like"}}
                }
            }
        }
    }

    risposta = es.search(index=INDEX, body=body)
    buckets = risposta["aggregations"]["per_piattaforma"]["buckets"]

    for b in buckets:
        piattaforma = b["key"]
        volume = b["doc_count"]
        media = round(b["sentiment_medio"]["value"], 3)
        engagement = round(b["engagement_medio"]["value"], 1)
        distribuzione = {d["key"]: d["doc_count"] for d in b["distribuzione_sentiment"]["buckets"]}
        print(f"{piattaforma:10s} | volume: {volume:3d} | sentiment medio: {media:+.3f} "
              f"| like medi: {engagement:6.1f} | {distribuzione}")


# ---------------------------------------------------------------------
# TEMA 5: Efficacia delle iniziative aziendali
# ---------------------------------------------------------------------
def query_5_efficacia_iniziative(data_release="2026-09-10"):
    stampa_intestazione(f"TEMA 5a/5b - Sentiment su 'update' prima/dopo {data_release}")

    def sentiment_periodo(operatore, valore_data):
        body = {
            "size": 0,
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"hashtag": "update"}},
                        {"range": {"data_commento": {operatore: valore_data}}}
                    ]
                }
            },
            "aggs": {
                "sentiment_medio": {"avg": {"field": "punteggio_sentiment"}}
            }
        }
        risposta = es.search(index=INDEX, body=body)
        return risposta["hits"]["total"]["value"], risposta["aggregations"]["sentiment_medio"]["value"]

    volume_pre, media_pre = sentiment_periodo("lt", data_release)
    volume_post, media_post = sentiment_periodo("gte", data_release)

    print(f"PRIMA della release  | volume: {volume_pre:3d} | sentiment medio: "
          f"{media_pre:+.3f}" if media_pre is not None else "PRIMA della release  | nessun dato")
    print(f"DOPO  la release     | volume: {volume_post:3d} | sentiment medio: "
          f"{media_post:+.3f}" if media_post is not None else "DOPO la release      | nessun dato")

    stampa_intestazione("TEMA 5c - Efficacia percepita delle promozioni (hashtag 'offerta')")

    body = {
        "size": 0,
        "query": {"term": {"hashtag": "offerta"}},
        "aggs": {
            "sentiment_medio_offerte": {"avg": {"field": "punteggio_sentiment"}},
            "engagement_medio_offerte": {"avg": {"field": "num_like"}}
        }
    }
    risposta = es.search(index=INDEX, body=body)
    volume = risposta["hits"]["total"]["value"]
    sentiment_medio = risposta["aggregations"]["sentiment_medio_offerte"]["value"]
    engagement_medio = risposta["aggregations"]["engagement_medio_offerte"]["value"]

    print(f"Commenti su offerte/promozioni: {volume} | sentiment medio: {sentiment_medio:+.3f} "
          f"| like medi: {engagement_medio:.1f}")


# ---------------------------------------------------------------------
# TEMA 6: Identificazione degli utenti più impattanti (identificazione di influencer)
def query_6_utenti_impattanti():
    stampa_intestazione("TEMA 6a - Top utenti per engagement totale")

    body = {
        "size": 0,
        "aggs": {
            "per_utente": {
                "terms": {
                    "field": "utente_handle",
                    "size": 15,
                    "order": {"engagement_totale": "desc"}
                },
                "aggs": {
                    "engagement_totale": {"sum": {"field": "num_like"}},
                    "sentiment_medio_utente": {"avg": {"field": "punteggio_sentiment"}},
                    "numero_commenti": {"value_count": {"field": "id_commento"}}
                }
            }
        }
    }

    risposta = es.search(index=INDEX, body=body)
    buckets = risposta["aggregations"]["per_utente"]["buckets"]

    for b in buckets:
        utente = b["key"]
        engagement = int(b["engagement_totale"]["value"])
        media = round(b["sentiment_medio_utente"]["value"], 3)
        n_commenti = b["numero_commenti"]["value"]
        etichetta = "detrattore" if media < 0 else ("promotore" if media > 0 else "neutro")
        print(f"{utente:20s} | commenti: {n_commenti:2d} | like totali: {engagement:4d} "
              f"| sentiment medio: {media:+.3f} ({etichetta})")

    stampa_intestazione("TEMA 6b - Top detrattori per engagement (solo sentiment negativo)")

    body_detrattori = {
        "size": 0,
        "query": {"term": {"sentiment": "negativo"}},
        "aggs": {
            "detrattori_top": {
                "terms": {
                    "field": "utente_handle",
                    "size": 10,
                    "order": {"engagement_totale": "desc"}
                },
                "aggs": {
                    "engagement_totale": {"sum": {"field": "num_like"}}
                }
            }
        }
    }

    risposta = es.search(index=INDEX, body=body_detrattori)
    buckets = risposta["aggregations"]["detrattori_top"]["buckets"]

    for b in buckets:
        print(f"{b['key']:20s} | commenti negativi: {b['doc_count']:2d} "
              f"| like totali: {int(b['engagement_totale']['value']):4d}")


# ---------------------------------------------------------------------
# Main
if __name__ == "__main__":
    if not es.ping():
        print(f"Impossibile connettersi a Elasticsearch su {ES_HOST}. "
              f"Verifica che il servizio sia avviato.")
        exit(1)

    query_1_andamento_mensile()
    query_2_crisi()
    query_3_pain_point()
    query_4_confronto_piattaforme()
    query_5_efficacia_iniziative()
    query_6_utenti_impattanti()
