/*
 * Script de la base de données de gestion des absences de professeurs
 */
BEGIN TRANSACTION;
	CREATE TABLE intervenant(
		id INTEGER PRIMARY KEY,
		nom VARCHAR(100) UNIQUE NOT NULL,
		telephone VARCHAR(100) NOT NULL,
		email VARCHAR(100) UNIQUE NOT NULL
	);
	CREATE TABLE absence(
		id INTEGER PRIMARY KEY,
		jour DATE NOT NULL,
		id_intervenant INTEGER NOT NULL,
		regularisee BOOLEAN NOT NULL,
		mail_envoye BOOLEAN NOT NULL,
		FOREIGN KEY (id_intervenant) REFERENCES intervenant(id)
	);
	CREATE TABLE cours(
		id INTEGER PRIMARY KEY,
		libelle VARCHAR(100) UNIQUE NOT NULL
	);
	CREATE TABLE intervenant_cours(
		id_intervenant INTEGER NOT NULL,
		id_cours INTEGER NOT NULL,
		PRIMARY KEY (id_intervenant, id_cours),
		FOREIGN KEY (id_intervenant) REFERENCES intervenant(id),
		FOREIGN KEY (id_cours) REFERENCES cours(id)
	);
	CREATE TABLE booleen(
		id INTEGER PRIMARY KEY,
		libelle VARCHAR(4) UNIQUE NOT NULL
	);
COMMIT;
