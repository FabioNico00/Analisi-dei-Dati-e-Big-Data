-- SCHEMA DATABASE: Centro Veterinario

DROP DATABASE IF EXISTS centro_veterinario;
CREATE DATABASE centro_veterinario CHARACTER SET utf8mb4;
USE centro_veterinario;

-- Entità: Cliente
CREATE TABLE Cliente (
    CodiceCliente   INT AUTO_INCREMENT PRIMARY KEY,
    Nome            VARCHAR(50)  NOT NULL,
    Cognome         VARCHAR(50)  NOT NULL,
    Indirizzo       VARCHAR(150),
    Telefono        VARCHAR(20)  NOT NULL,
    Email           VARCHAR(100) NOT NULL,
    CONSTRAINT uq_cliente_email UNIQUE (Email)
) ENGINE=InnoDB;

-- Entità: Veterinario
CREATE TABLE Veterinario (
    CodiceVeterinario  INT AUTO_INCREMENT PRIMARY KEY,
    Nome               VARCHAR(50) NOT NULL,
    Cognome            VARCHAR(50) NOT NULL,
    Specializzazione   VARCHAR(100),
    Attivo             BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

-- Entità: Animale
CREATE TABLE Animale (
    CodiceAnimale       INT AUTO_INCREMENT PRIMARY KEY,
    Nome                VARCHAR(50) NOT NULL,
    Specie              VARCHAR(50) NOT NULL,
    Razza               VARCHAR(50),
    DataNascita         DATE NULL,
    DataNascitaStimata  BOOLEAN NOT NULL DEFAULT FALSE,
    Sesso               CHAR(1) NOT NULL,
    Attivo              BOOLEAN NOT NULL DEFAULT TRUE,
    CodiceCliente       INT NOT NULL,

    CONSTRAINT chk_animale_sesso
        CHECK (Sesso IN ('M', 'F'))
) ENGINE=InnoDB;

-- Entità: Visita
CREATE TABLE Visita (
    CodiceVisita        INT AUTO_INCREMENT PRIMARY KEY,
    Data                DATE NOT NULL,
    Motivo              VARCHAR(200) NOT NULL,
    Diagnosi            VARCHAR(500),
    Costo               DECIMAL(8,2),
    Terapia             VARCHAR(500),
    CodiceAnimale       INT NOT NULL,
    CodiceVeterinario   INT NOT NULL,

    CONSTRAINT chk_visita_costo
        CHECK (Costo IS NULL OR Costo >= 0)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------
-- COSTRUZIONE DELLE RELAZIONI TRA ENTITÀ


-- Relazione "Possiede": Cliente (1,N) --- Animale (1,1)
-- Un cliente può possedere più animali; ogni animale ha esattamente un proprietario, sempre presente.
ALTER TABLE Animale
    ADD CONSTRAINT fk_animale_cliente
    FOREIGN KEY (CodiceCliente) REFERENCES Cliente(CodiceCliente)
    ON DELETE RESTRICT   -- non si cancella un cliente con animali registrati
    ON UPDATE CASCADE;

-- Relazione "Riguarda": Animale (1,N) --- Visita (1,1)
-- Un animale può avere più visite nel tempo (storico clinico).
ALTER TABLE Visita
    ADD CONSTRAINT fk_visita_animale
    FOREIGN KEY (CodiceAnimale) REFERENCES Animale(CodiceAnimale)
    ON DELETE RESTRICT   -- non si cancella un animale con visite registrate
    ON UPDATE CASCADE;

-- Relazione "Esegue": Veterinario (1,N) --- Visita (1,1)
-- Un veterinario può eseguire più visite, ogni visita è eseguita da esattamente un veterinario.
ALTER TABLE Visita
    ADD CONSTRAINT fk_visita_veterinario
    FOREIGN KEY (CodiceVeterinario) REFERENCES Veterinario(CodiceVeterinario)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- ---------------------------------------------------------------
-- INDICI DI SUPPORTO
CREATE INDEX idx_visita_animale ON Visita(CodiceAnimale, Data);

-- TRIGGER: la data della visita non può precedere la nascita dell'animale.
DELIMITER $$

CREATE TRIGGER trg_check_data_visita_insert
BEFORE INSERT ON Visita
FOR EACH ROW
BEGIN
    DECLARE v_nascita DATE;
    SELECT DataNascita INTO v_nascita
    FROM Animale
    WHERE CodiceAnimale = NEW.CodiceAnimale;

    IF v_nascita IS NOT NULL AND NEW.Data < v_nascita THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La data della visita non può precedere la data di nascita dell''animale';
    END IF;
END$$

CREATE TRIGGER trg_check_data_visita_update
BEFORE UPDATE ON Visita
FOR EACH ROW
BEGIN
    DECLARE v_nascita DATE;
    SELECT DataNascita INTO v_nascita
    FROM Animale
    WHERE CodiceAnimale = NEW.CodiceAnimale;

    IF v_nascita IS NOT NULL AND NEW.Data < v_nascita THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La data della visita non può precedere la data di nascita dell''animale';
    END IF;
END$$

DELIMITER ;


-- TRIGGER: impedisce di assegnare una nuova visita a un veterinario segnato come non più attivo 
DELIMITER $$

CREATE TRIGGER trg_check_veterinario_attivo
BEFORE INSERT ON Visita
FOR EACH ROW
BEGIN
    DECLARE v_attivo BOOLEAN;
    SELECT Attivo INTO v_attivo
    FROM Veterinario
    WHERE CodiceVeterinario = NEW.CodiceVeterinario;

    IF v_attivo = FALSE THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Impossibile assegnare una visita a un veterinario non più attivo';
    END IF;
END$$

DELIMITER ;
