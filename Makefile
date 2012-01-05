DB_FILE=private/gestionAbsences.db


all:ui db

ui:
	@echo "Création de l'interface utilisateur"
	@pyuic4 gestionAbsencesUI.ui -o gestionAbsencesUI.py
	@pyuic4 mailUI.ui -o mailUI.py
	@pyuic4 interface/configUI.ui -o configUI.py

db:
	@echo "Création de la structure de la base de données"
	@cat gestionAbsences.sql | sqlite3 $(DB_FILE)
data:
	@echo "Création du jeu de données de test"
	@cat private/createData.sql | sqlite3 $(DB_FILE)

clean:
	@echo Nettoyage
	@rm -f *UI.py
	@rm -f *.pyc

db-clean:
	@echo "Suppression de la base de données"
	@rm -f $(DB_FILE)

mrproper:clean db-clean
