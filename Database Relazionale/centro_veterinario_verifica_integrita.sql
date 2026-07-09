-- VERIFICA INTEGRITÀ: Centro Veterinario
USE centro_veterinario;

-- ------------------------------------------------------------
-- 1. Animali che referenziano un cliente inesistente
SELECT a.CodiceAnimale, a.Nome, a.CodiceCliente
FROM Animale a
LEFT JOIN Cliente c ON c.CodiceCliente = a.CodiceCliente
WHERE c.CodiceCliente IS NULL;


-- ------------------------------------------------------------
-- 2. Visite che referenziano un animale inesistente
SELECT v.CodiceVisita, v.CodiceAnimale
FROM Visita v
LEFT JOIN Animale a ON a.CodiceAnimale = v.CodiceAnimale
WHERE a.CodiceAnimale IS NULL;


-- ------------------------------------------------------------
-- 3. Visite che referenziano un veterinario inesistente
SELECT v.CodiceVisita, v.CodiceVeterinario
FROM Visita v
LEFT JOIN Veterinario vet ON vet.CodiceVeterinario = v.CodiceVeterinario
WHERE vet.CodiceVeterinario IS NULL;


-- ------------------------------------------------------------
-- 4. Email duplicate tra clienti diversi
SELECT Email, COUNT(*) AS Occorrenze
FROM Cliente
GROUP BY Email
HAVING COUNT(*) > 1;


-- ------------------------------------------------------------
-- 5. Visite con data precedente alla nascita dell'animale
SELECT v.CodiceVisita, v.Data AS DataVisita, a.CodiceAnimale, a.DataNascita
FROM Visita v
JOIN Animale a ON a.CodiceAnimale = v.CodiceAnimale
WHERE a.DataNascita IS NOT NULL
  AND v.Data < a.DataNascita;


-- ------------------------------------------------------------
-- 6. Visite assegnate a un veterinario non più attivo
SELECT v.CodiceVisita, v.Data, vet.CodiceVeterinario, vet.Nome, vet.Cognome
FROM Visita v
JOIN Veterinario vet ON vet.CodiceVeterinario = v.CodiceVeterinario
WHERE vet.Attivo = FALSE
  AND v.Data > CURDATE();


-- ------------------------------------------------------------
-- 7. Costi negativi nelle visite
SELECT CodiceVisita, Costo
FROM Visita
WHERE Costo < 0;


-- ------------------------------------------------------------
-- 8. Animali con data di nascita nel futuro
SELECT CodiceAnimale, Nome, DataNascita
FROM Animale
WHERE DataNascita > CURDATE();


-- ------------------------------------------------------------
-- 9. Campi NOT NULL che risultano comunque NULL
SELECT CodiceCliente, Nome, Cognome, Telefono, Email
FROM Cliente
WHERE Nome IS NULL OR Cognome IS NULL OR Telefono IS NULL OR Email IS NULL;

SELECT CodiceAnimale, Nome, Specie, Sesso, CodiceCliente
FROM Animale
WHERE Nome IS NULL OR Specie IS NULL OR Sesso IS NULL OR CodiceCliente IS NULL;

SELECT CodiceVisita, Data, Motivo, CodiceAnimale, CodiceVeterinario
FROM Visita
WHERE Data IS NULL OR Motivo IS NULL OR CodiceAnimale IS NULL OR CodiceVeterinario IS NULL;


-- ------------------------------------------------------------
-- 10. Verifica integrità referenziale tra Animale e Cliente
-- Le due colonne devono avere lo stesso valore.
SELECT
    (SELECT COUNT(*) FROM Animale) AS TotaleAnimali,
    (SELECT COUNT(DISTINCT a.CodiceAnimale)
     FROM Animale a
     JOIN Cliente c ON c.CodiceCliente = a.CodiceCliente) AS AnimaliConClienteValido;
