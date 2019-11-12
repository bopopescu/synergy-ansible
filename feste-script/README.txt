Entwickelt von Felix Sterzelmaier, Concat AG
Für die ITSG
im November 2019
Projektleiter: Florian Fein


Ausgangslage:



Verbindung:
Ich verbinde mich mittels VPN mit technik.concat.de:443 als Benutzer feste-local.
Anschließend verbinde ich mich mit


Workflow:
Exportieren der aktuellsten Version der Exceldatei.
Anpassen der Konfiguration im gekennzeichneten Bereich der Datei convert.py nach Vorgaben von Oliver Antwerpen.
Ausführen der run.bat (Installiert Python-Abhängigkeiten. Und Startet das Python-Skript.)
=> Das hierdurch ausgeführte Python-Skript liest die Exceltabelle ein und generiert ein hierzu passendes Ansible-Playbook.



Logs:
Können in den beiden Dateien log* eigesehen werden.


Setup Linux:
pip3 install xlrd
pip3 install pytz
pip3 install tzlocal

Run Linux:
python3 ./convert.py
or
python ./convert.py
eample:
olant@olant-ansible:~/synergy-ansible/feste-script$ python3 ./convert.py

Setup & Run Windows:
remove every "rem " in run.bat
install pyrthon
configure python path in run.bat
run run.bat