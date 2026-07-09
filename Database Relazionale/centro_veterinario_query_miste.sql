-- QUERY DI PROVA: Centro Veterinario

USE centro_veterinario;

-- ------------------------------------------------------------
-- 1. Storico clinico di un animale (in ordine cronologico)
SELECT a.Nome AS Animale, v.Data, v.Motivo, v.Diagnosi, v.Costo, v.Terapia,
       vet.Nome AS NomeVeterinario, vet.Cognome AS CognomeVeterinario
FROM Visita v
JOIN Animale a ON a.CodiceAnimale = v.CodiceAnimale
JOIN Veterinario vet ON vet.CodiceVeterinario = v.CodiceVeterinario
WHERE v.CodiceAnimale = 1
ORDER BY v.Data;

-- ------------------------------------------------------------
-- 2. Numero di visite effettuate da ciascun veterinario
SELECT vet.CodiceVeterinario, vet.Nome, vet.Cognome, COUNT(*) AS NumVisite
FROM Visita v
JOIN Veterinario vet ON vet.CodiceVeterinario = v.CodiceVeterinario
GROUP BY vet.CodiceVeterinario, vet.Nome, vet.Cognome
ORDER BY NumVisite DESC;

-- ------------------------------------------------------------
-- 3. Elenco degli animali posseduti da un determinato cliente
SELECT a.CodiceAnimale, a.Nome, a.Specie, a.Razza, a.DataNascita
FROM Animale a
WHERE a.CodiceCliente = 1;

-- ------------------------------------------------------------
-- 4. Spesa totale sostenuta da ciascun cliente 
SELECT c.CodiceCliente, c.Nome, c.Cognome, 
       COALESCE(SUM(v.Costo), 0) AS SpesaTotale
FROM Cliente c
LEFT JOIN Animale a ON a.CodiceCliente = c.CodiceCliente
LEFT JOIN Visita v ON v.CodiceAnimale = a.CodiceAnimale
GROUP BY c.CodiceCliente, c.Nome, c.Cognome
ORDER BY SpesaTotale DESC;

-- ------------------------------------------------------------
-- 5. Animali che non hanno mai effettuato alcuna visita
SELECT a.CodiceAnimale, a.Nome, a.Specie, c.Nome AS NomeProprietario, c.Cognome AS CognomeProprietario
FROM Animale a
JOIN Cliente c ON c.CodiceCliente = a.CodiceCliente
LEFT JOIN Visita v ON v.CodiceAnimale = a.CodiceAnimale
WHERE v.CodiceVisita IS NULL;

-- ------------------------------------------------------------
-- 6. Il veterinario con il maggior numero di visite effettuate
SELECT vet.CodiceVeterinario, vet.Nome, vet.Cognome, COUNT(*) AS NumVisite
FROM Visita v
JOIN Veterinario vet ON vet.CodiceVeterinario = v.CodiceVeterinario
GROUP BY vet.CodiceVeterinario, vet.Nome, vet.Cognome
ORDER BY NumVisite DESC
LIMIT 1;

-- ------------------------------------------------------------
-- 7. Clienti che possiedono più di un animale
SELECT c.CodiceCliente, c.Nome, c.Cognome, COUNT(*) AS NumAnimali
FROM Cliente c
JOIN Animale a ON a.CodiceCliente = c.CodiceCliente
GROUP BY c.CodiceCliente, c.Nome, c.Cognome
HAVING COUNT(*) > 1
ORDER BY NumAnimali DESC;


-- ------------------------------------------------------------
-- 8. Costo medio delle visite per specializzazione del veterinario
SELECT vet.Specializzazione, ROUND(AVG(v.Costo), 2) AS CostoMedio, COUNT(*) AS NumVisite
FROM Visita v
JOIN Veterinario vet ON vet.CodiceVeterinario = v.CodiceVeterinario
GROUP BY vet.Specializzazione
ORDER BY CostoMedio DESC;

-- ------------------------------------------------------------
-- 9. Animali con data di nascita stimata (non certa)
SELECT CodiceAnimale, Nome, Specie, DataNascita
FROM Animale
WHERE DataNascitaStimata = TRUE;

-- ------------------------------------------------------------
-- 10. Ultima visita registrata per ciascun animale
SELECT a.CodiceAnimale, a.Nome, MAX(v.Data) AS UltimaVisita
FROM Animale a
JOIN Visita v ON v.CodiceAnimale = a.CodiceAnimale
GROUP BY a.CodiceAnimale, a.Nome
ORDER BY UltimaVisita DESC;

-- ------------------------------------------------------------
-- 11. Veterinari non più attivi che hanno comunque visite registrate in passato 
SELECT vet.CodiceVeterinario, vet.Nome, vet.Cognome, COUNT(v.CodiceVisita) AS NumVisitePassate
FROM Veterinario vet
JOIN Visita v ON v.CodiceVeterinario = vet.CodiceVeterinario
WHERE vet.Attivo = FALSE
GROUP BY vet.CodiceVeterinario, vet.Nome, vet.Cognome;

-- ------------------------------------------------------------
-- 12. Numero di visite per specie animale 
SELECT a.Specie, COUNT(*) AS NumVisite
FROM Visita v
JOIN Animale a ON a.CodiceAnimale = v.CodiceAnimale
GROUP BY a.Specie
ORDER BY NumVisite DESC;

-- ------------------------------------------------------------
-- 13. Animali attualmente non attivi (es. deceduti) con relativo storico clinico completo
SELECT a.CodiceAnimale, a.Nome, a.Specie, v.Data, v.Motivo, v.Diagnosi
FROM Animale a
JOIN Visita v ON v.CodiceAnimale = a.CodiceAnimale
WHERE a.Attivo = FALSE
ORDER BY a.CodiceAnimale, v.Data;
