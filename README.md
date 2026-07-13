# Analisi-dei-Dati-e-Big-Data

Questo progetto mostra come gestire e analizzare i dati usando tre tipi di database diversi (relazionale, a grafo e documentale).

## 1. Centro Veterinario: Database Relazionale (MySQL)

### Il Contesto

Una clinica veterinaria necessita di un'infrastruttura centralizzata per gestire l'operatività quotidiana: l'anagrafica dei clienti, lo stato dei pazienti, l'organizzazione del personale medico interno e, come vincolo critico, il mantenimento di uno storico clinico integro e coerente nel tempo, eliminando i rischi di dati orfani o incongruenze temporali.

### Scelte architetturali

Il sistema adotta un modello normalizzato che distribuisce le informazioni su quattro entità principali: clienti, animali, veterinari e visite. Questa scomposizione previene la ridondanza informativa e organizza in modo rigido le relazioni basate su chiavi esterne.

I dati anagrafici dei clienti applicano un vincolo di unicità sulle informazioni di contatto. Per gli animali viene tracciata la data di nascita (anche stimata per i casi di randagismo) e lo stato di attività. I veterinari sono suddivisi per specializzazione medica e monitorati secondo lo stato del loro rapporto lavorativo. L'entità delle visite rappresenta il punto di intersezione transazionale, registrando i dettagli clinici, le diagnosi, le terapie e i costi delle singole prestazioni.

#### Logiche di Automazione (Trigger)

Le logiche procedurali avanzate intervengono prima della scrittura fisica dei dati sul database tramite trigger. Un controllo `BEFORE INSERT` verifica la coerenza temporale bloccando l'inserimento di visite antecedenti alla nascita del paziente. Un secondo automatismo impedisce l'assegnazione di appuntamenti a medici non più attivi. Infine, l'architettura implementa la cancellazione logica per evitare la perdita accidentale dello storico clinico in seguito al decesso di un animale o alla cessazione del contratto di un medico.

### Query Analitiche

* Analisi dettagliata dello storico clinico dei singoli pazienti e monitoraggio dei motivi di visita ricorrenti.


* Valutazione del carico di lavoro e della distribuzione delle prestazioni tra i diversi medici veterinari.


* Monitoraggio economico del fatturato accumulato per singolo cliente e calcolo della spesa complessiva.


* Business Intelligence sui costi medi delle prestazioni sanitarie segmentati in base alla specializzazione medica.



## 2. Piattaforma di E-Learning: Database a Grafo (Neo4j)

### Il Contesto

Una piattaforma di formazione online richiede uno strumento per mappare e navigare il proprio network didattico. L'esigenza non si concentra su entità isolate, ma sull'esplorazione profonda e ricorsiva delle connessioni tra studenti, docenti e contenuti, per far emergere percorsi di apprendimento personalizzati e vincoli di propedeuticità.

### Struttura del database a grafo

Nelle tabelle tradizionali (SQL), per trovare catene di collegamenti e percorsi formativi complessi servirebbero operazioni di incrocio molto pesanti che rallentano il sistema. Con Neo4j, i dati e le loro interconnessioni sono trattati allo stesso livello di importanza, collegando i nodi direttamente tramite relazioni esplicite.

* I Nodi: Corsi, Docenti, Studenti, Argomenti e Certificati.


* I Collegamenti: Un docente insegna un determinato corso; uno studente è iscritto a un corso tracciando il suo avanzamento; uno studente consegue un certificato autonomo; un certificato attesta il completamento di un corso; un corso tratta specifici argomenti; un argomento è prerequisito di un altro argomento tramite una relazione ricorsiva.



### Query Analitiche (Cypher)

* Analisi Strutturale e di Audit: query dedicate alla verifica della coerenza della rete per escludere la presenza di cicli infiniti nelle propedeuticità o anomalie nelle iscrizioni.


* Sistemi di Raccomandazione: elaborazione di suggerimenti didattici personalizzati per gli studenti, basati sullo storico delle competenze già acquisite e sulle affinità del network.


* Algoritmi Predittivi e di Rete (Opportunità): utilizzo della libreria Graph Data Science per calcolare la centralità degli argomenti cardine tramite PageRank e rilevare comunità tematiche latenti nella rete attraverso l'algoritmo di Louvain.



## 3. Sentiment Analysis: Database non Relazionale (Elasticsearch)

### Il Contesto

Una piattaforma di social listening vuole monitorare la reputazione di un brand tecnologico analizzando le opinioni e i commenti testuali (dati non strutturati) lasciati dagli utenti sui canali digitali. L'esigenza critica è l'indicizzazione e la ricerca immediata all'interno di testi liberi soggetti a variazioni morfologiche ed errori ortografici.

### Scelte Tecniche e Configurazione dell'Indice

I database normali fanno fatica a cercare parole dentro testi lunghi e non strutturati. Elasticsearch è un motore di ricerca ottimizzato per distribuire e scansionare rapidamente grandi volumi di dati semistrutturati all'interno di un unico indice denormalizzato, dove ogni documento JSON contiene tutte le informazioni del feed. Ciascun record unisce dati anagrafici, piattaforma social, testo libero, un array di hashtag, metriche di engagement e punteggi continui di sentiment analysis.

* Indice Invertito ed Elisione Linguistica: L'indice adotta un analizzatore nativo per la lingua italiana che applica lo stemming per ridurre i termini alla loro radice linguistica, normalizzando le varianti morfologiche ed intercettando espressioni naturali correlate. Il motore applica inoltre parametri di tolleranza agli errori ortografici (fuzziness) per gestire i refusi di battitura degli utenti.



### Query Analitiche (ElasticSearch)

Elasticsearch estrae insight in tempo reale attraverso query avanzate ed aggregazioni:

* Monitoraggio del Brand: calcolo del sentiment medio e del livello di gradimento complessivo attraverso aggregazioni basate sulla piattaforma social e sotto-aggregazioni metriche sui punteggi dei commenti.


* Crisis Management e Customer Care: costrutti booleani che isolano tempestivamente i feedback negativi associati a un alto tasso di engagement per rilevare disservizi o problemi critici segnalati dagli utenti.


* Focus Tematico e Temporale: query strutturate per filtrare i flussi di dati all'interno di specifici intervalli temporali, combinando ricerche full-text su gruppi di sinonimi acustici o criticità operative per analizzare i trend di discussione.


* Focus sulla Qualità Globale: interrogazioni full-text estese a tutto lo storico annuale per mappare la percezione generale degli utenti, scansionando simultaneamente termini positivi e negativi all'interno dei testi liberi.



## Conclusione

L'architettura complessiva di questo progetto evidenzia l'efficacia strategica dei diversi database, dimostrando come il superamento del modello a database unico permetta di valorizzare al massimo ogni singola tipologia di dato a seconda del contesto di business. La robustezza transazionale di MySQL garantisce l'assoluta coerenza e l'integrità dei dati clinici del centro veterinario; l'espressività nativa di Neo4j permette di mappare ed esplorare relazioni ricorsive complesse sulla piattaforma di e-learning attraverso algoritmi predittivi; la reattività di Elasticsearch trasforma i testi non strutturati dei social media in metriche analitiche immediate.

Un elemento unificante e fondamentale dell'intero progetto è l'implementazione di uno strato applicativo esterno in Python per tutti e tre i database. Attraverso l'integrazione dei rispettivi driver e client ufficiali, Python ha permesso di automatizzare e gestire in modo centralizzato sia le operazioni di popolamento e manutenzione dei dati, sia l'esecuzione delle query analitiche avanzate. 
