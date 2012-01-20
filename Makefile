DB_FILE=private/gem.db

UI=configUI.py mailUI.py tableUI.py gemUI.py

all:ui db

ui:$(UI)

%UI.py:interface/%.ui
	@echo "Création de l'ui" $(subst UI.py,,$@)
	@pyside-uic $< -o $@
db:
	@echo "Création de la structure de la base de données"
	@cat gem.sql | sqlite3 $(DB_FILE)
data:
	@echo "Création du jeu de données de test"
	@cat old/createData.sql | sqlite3 $(DB_FILE)

clean:
	@echo Nettoyage
	@rm -f $(UI)
	@rm -f *.pyc

db-clean:
	@echo "Suppression de la base de données"
	@rm -f $(DB_FILE)

linpkg:mrproper ui db
	@tar cjf gem-0_1_1.tar.bz2 *.py private/

winexe-clean:
	@rm -Rf dist gem.spec warngem.txt

winexe:all
	@echo "Création de l'exécutable windows"
	@~/.wine/drive_c/Python27/python.exe windows/pyinstaller-1.5.1/Makespec.py --icon=gem.ico -F -w gem.py
	@~/.wine/drive_c/Python27/python.exe windows/pyinstaller-1.5.1/Build.py gem.spec
	@echo Finalisation
	@mkdir dist/sqldrivers
	@mkdir dist/private
	@cp sqldrivers/qsqlite4.dll dist/sqldrivers/
	@cp private/gem.db dist/private

winsetup:mrproper winexe
	@echo "Création de l'installeur windows"
	@echo > log
	@wine ~/.wine/drive_c/Program\ Files/Inno\ Setup\ 5/Compil32.exe /cc inno_setup.iss

winsetup-clean:

mrproper:clean db-clean winexe-clean
	@rm -f log log* rm -Rf dist gem_setup.exe gem-0_1_1.tar.bz2
