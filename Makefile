all:
	pyuic4 gestionAbsencesUI.ui -o gestionAbsencesUI.py

clean:
	rm -f *.pyc
