# Script di interazione con il database centro_veterinario.

import mysql.connector

def connect_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="centro_veterinario"
    )
    return conn



# 1. Storico clinico di un animale (in ordine cronologico)

def storico_animale(conn, animale_id):
    query = """
        SELECT a.Nome AS Animale, c.Nome AS NomeProprietario, c.Cognome AS CognomeProprietario,
               v.Data, v.Motivo, v.Diagnosi, v.Costo, v.Terapia,
               vet.Nome AS NomeVeterinario, vet.Cognome AS CognomeVeterinario
        FROM Visita v
        JOIN Animale a ON a.CodiceAnimale = v.CodiceAnimale
        JOIN Cliente c ON c.CodiceCliente = a.CodiceCliente
        JOIN Veterinario vet ON vet.CodiceVeterinario = v.CodiceVeterinario
        WHERE v.CodiceAnimale = %s
        ORDER BY v.Data;
    """
    cur = conn.cursor(dictionary=True)
    cur.execute(query, (animale_id,))
    results = cur.fetchall()

    print(f"\nStorico clinico dell'animale {animale_id}:")
    if not results:
        print("Nessuna visita trovata per questo animale.")
        return
    for row in results:
        print(f"- {row['Data']} | {row['Animale']} ({row['NomeProprietario']} {row['CognomeProprietario']}) "
              f"| Motivo: {row['Motivo']} | Diagnosi: {row['Diagnosi']} | Costo: {row['Costo']} "
              f"| Terapia: {row['Terapia']} | Veterinario: {row['NomeVeterinario']} {row['CognomeVeterinario']}")



# 2. Numero di visite per ciascun veterinario 

def visite_per_veterinario(conn):
    query = """
        SELECT vet.CodiceVeterinario, vet.Nome, vet.Cognome, vet.Attivo, COUNT(*) AS NumVisite
        FROM Visita v
        JOIN Veterinario vet ON vet.CodiceVeterinario = v.CodiceVeterinario
        GROUP BY vet.CodiceVeterinario, vet.Nome, vet.Cognome, vet.Attivo
        ORDER BY NumVisite DESC;
    """
    cur = conn.cursor(dictionary=True)
    cur.execute(query)
    results = cur.fetchall()

    print("\nNumero di visite per veterinario:")
    for row in results:
        stato = "attivo" if row["Attivo"] else "non attivo"
        print(f"- {row['Nome']} {row['Cognome']} ({row['CodiceVeterinario']}) | Stato: {stato} "
              f"| Visite: {row['NumVisite']}")


# 3. Animali di un determinato cliente 

def animali_del_cliente(conn, cliente_id):
    query = """
        SELECT a.CodiceAnimale, a.Nome, a.Specie, a.Razza, a.DataNascita,
               c.Nome AS NomeProprietario, c.Cognome AS CognomeProprietario
        FROM Animale a
        JOIN Cliente c ON c.CodiceCliente = a.CodiceCliente
        WHERE a.CodiceCliente = %s;
    """
    cur = conn.cursor(dictionary=True)
    cur.execute(query, (cliente_id,))
    results = cur.fetchall()

    if not results:
        print(f"\nIl cliente {cliente_id} non possiede animali (o non esiste).")
        return

    print(f"\nAnimali del cliente {cliente_id} ({results[0]['NomeProprietario']} {results[0]['CognomeProprietario']}):")
    for row in results:
        print(f"- {row['CodiceAnimale']} | {row['Nome']} | {row['Specie']} | {row['Razza']} | Nato il: {row['DataNascita']}")



# 4. Clienti che possiedono più di un animale

def clienti_con_piu_animali(conn):
    query = """
        SELECT c.CodiceCliente, c.Nome, c.Cognome, COUNT(*) AS NumAnimali
        FROM Cliente c
        JOIN Animale a ON a.CodiceCliente = c.CodiceCliente
        GROUP BY c.CodiceCliente, c.Nome, c.Cognome
        HAVING COUNT(*) > 1
        ORDER BY NumAnimali DESC;
    """
    cur = conn.cursor(dictionary=True)
    cur.execute(query)
    results = cur.fetchall()

    print("\nClienti con più di un animale:")
    for row in results:
        print(f"- {row['Nome']} {row['Cognome']} ({row['CodiceCliente']}) | Animali: {row['NumAnimali']}")


# 5. Spesa totale sostenuta da ciascun cliente

def spesa_per_cliente(conn):
    query = """
        SELECT c.CodiceCliente, c.Nome, c.Cognome, COALESCE(SUM(v.Costo), 0) AS SpesaTotale
        FROM Cliente c
        LEFT JOIN Animale a ON a.CodiceCliente = c.CodiceCliente
        LEFT JOIN Visita v ON v.CodiceAnimale = a.CodiceAnimale
        GROUP BY c.CodiceCliente, c.Nome, c.Cognome
        ORDER BY SpesaTotale DESC;
    """
    cur = conn.cursor(dictionary=True)
    cur.execute(query)
    results = cur.fetchall()

    print("\nSpesa totale per cliente:")
    for row in results:
        print(f"- {row['Nome']} {row['Cognome']} ({row['CodiceCliente']}) | Spesa totale: {row['SpesaTotale']}")


# 6. Costo medio delle visite per specializzazione del veterinario

def costo_medio_per_specializzazione(conn):
    query = """
        SELECT vet.Specializzazione, ROUND(AVG(v.Costo), 2) AS CostoMedio, COUNT(*) AS NumVisite
        FROM Visita v
        JOIN Veterinario vet ON vet.CodiceVeterinario = v.CodiceVeterinario
        GROUP BY vet.Specializzazione
        ORDER BY CostoMedio DESC;
    """
    cur = conn.cursor(dictionary=True)
    cur.execute(query)
    results = cur.fetchall()

    print("\nCosto medio delle visite per specializzazione:")
    for row in results:
        print(f"- {row['Specializzazione']} | Costo medio: {row['CostoMedio']} | Visite: {row['NumVisite']}")


# Esecuzione delle singole query

if __name__ == "__main__":
    conn = connect_db()

    storico_animale(conn, 1)              # Query 1: storico clinico animale (ID a scelta)
    # visite_per_veterinario(conn)          # Query 2: visite per veterinario
    # animali_del_cliente(conn, 1)         # Query 3: animali del cliente (ID a scelta)
    # clienti_con_piu_animali(conn)         # Query 4: clienti con più di un animale
    #spesa_per_cliente(conn)               # Query 5: spesa totale per cliente
    # costo_medio_per_specializzazione(conn)  # Query 6: costo medio per specializzazione

    conn.close()
