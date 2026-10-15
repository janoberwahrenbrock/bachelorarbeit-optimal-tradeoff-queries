# Native Betriebsqualifizierung

`qualify.py` prüft ein installiertes Wheel mit neuen analytischen Eingaben und
gezielten Laufzeitfehlern. Es verwendet dieselbe Solver-, Supervisor- und
Writerroute wie reguläre Läufe. Der private Kandidatenprofilresolver erlaubt
diese erste Prüfung, ohne eine bestehende Freigabe zu behaupten. Er ist kein
öffentlicher CLI-Schalter.

```sh
/path/to/wheel-environment/bin/python tools/qualification/qualify.py \
  --project-root "$PWD" --output "$PWD/runs/qualification-unique-id" \
  --scope standalone
```

Unter Linux qualifiziert `--scope series_linux_recovery` zusätzlich echte
Prozessidentitäten, die Sperre lebender Gruppen, einen neuen Versuch nach
nachgewiesenem Gruppenende, die Freigabepipe bei EOF, unsichere Startzustände und
die Erhaltung aller Versuche. Faultinjections verändern keine Querybewertung.
Ein ungeklärter Spawn oder Start bleibt gesperrt und wird nicht als Erfolg
gezählt. Die Kontrollen behaupten keine Powerloss-Sicherheit für jedes
Dateisystem.

Jeder Check speichert konkrete Beobachtungen, Fehler und die gebundenen Quellen,
Umgebungen und Harnessdateien unter dem angegebenen neuen `runs/`-Verzeichnis.
Nur vollständig bestandene Kontrollen erzeugen `profile.json`. Ein Fehlschlag
bleibt erhalten; für einen neuen Versuch ist ein neues Ausgabeverzeichnis nötig.

Die Qualifizierung prüft den nativen Betrieb. Alt-Neu-Gleichheit und Laufzeit
werden getrennt außerhalb dieses Projekts abgenommen und gehören nicht in die
native Zertifizierungsclosure.
