DB_FILE=private/gem.db

UI=configUI.py mailUI.py tableUI.py gemUI.py

all:ui db

ui:$(UI)

%UI.py:interface/%.ui
	@echo "Création de l'ui" $(subst UI.py,,$@)
	@pyuic4 $< -o $@
db:
	@echo "Création de la structure de la base de données"
	@cat gem.sql | sqlite3 $(DB_FILE)
data:
	@echo "Création du jeu de données de test"
	@cat private/createData.sql | sqlite3 $(DB_FILE)

clean:
	@echo Nettoyage
	@rm -f $(UI)
	@rm -f *.pyc

db-clean:
	@echo "Suppression de la base de données"
	@rm -f $(DB_FILE)

mrproper:clean db-clean
