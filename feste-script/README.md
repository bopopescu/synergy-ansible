Entwickelt von Felix Sterzelmaier, Concat AG
Für die ITSG
im November 2019
Projektleiter: Florian Fein


Ausgangslage:
Für das Projekt Nublar soll die Installation der Hardware Synergy und der Managementsoftware Oneview mittels Ansible automatisiert werden. Nötige Informationen stehen in einer Exceldatei.
Die Datei nublar_automation.xlsx gibt einen Überblick über die einzelnen Aufgaben und Playbooks


Verbindung:
Ich verbinde mich mittels VPN mit technik.concat.de:443 als Benutzer feste-local.
Anschließend verbinde ich mich mit als feste mit dem ssh server 10.10.5.239 und wechsle mit "sudo -i" und "su olant" den Benutzer.


Workflow:
Exportieren der aktuellsten Version der Exceldatei.
Anpassen der Konfiguration im gekennzeichneten Bereich der Datei convert.py nach Vorgaben von Oliver Antwerpen.
Ausführen der run.bat (Installiert Python-Abhängigkeiten. Und Startet das Python-Skript.)
=> Das hierdurch ausgeführte Python-Skript liest die Exceltabelle (wip_checkliste_gesamt.xlsx) ein und generiert hierzu passende Ansible-Playbooks und Konfigurationsdateien im Ordner output. Diese benötigen die Dateien, welche im Unterordner "filter_plugins" liegen. Dateien im Unterordner "files" sind nicht Teil dieses git-Repositorys und werden vor dem Ausführen auf dem Server hinzugefügt.


Setup Linux:
pip3 install xlrd
pip3 install pytz
pip3 install tzlocal

Run Linux:
python3 ./convert.py
or
python ./convert.py
example:
olant@olant-ansible:~/synergy-ansible/feste-script$ python3 ./convert.py

Setup & Run Windows:
remove every "rem " in run.bat
install pyrthon 3.7
configure paths in run.bat
run run.bat
