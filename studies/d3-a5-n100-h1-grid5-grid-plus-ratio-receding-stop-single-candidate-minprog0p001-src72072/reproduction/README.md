# Offlineprüfung gespeicherter Daten

Benötigt Python3.13/3.14 und die Standardbibliothek. Nach der ZIP-Manifestprüfung in einem neuen Verzeichnis:

`python3 -I -S -B studies/d3-a5-n100-h1-grid5-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072/reproduction/reproduce.py --project-root /ABS/EXTRACTED --output /ABS/FRESH_ANALYSIS`

Das Ausgabeziel muss neu sein und außerhalb des entpackten Originalbaums liegen. Die Prüfung reproduziert die ursprünglichen Berichtsdateien und alle100 Fraction-Gewinner sowie sämtliche tatsächlichen Antworten. H1/A10/A20 vergleichen zusätzlich die unveränderte Rohprüfung bis auf Erzeugungszeit und Prüfdauer. A3 bewahrt das fehlgeschlagene ursprüngliche Raw und prüft nur den separat korrigierten Export gegen den gespeicherten Issue-Nachweis; kein vollständiger A3-Raw-Retry. Kein Solver, Netzwerk oder native Audit-/Raw-/Report-Phase wird gestartet. Die vollständige historische Entwicklungsqualifizierung und die laufende Fleet-Sicherung sind keine Paketvollständigkeitsbehauptung. Historische Prozess-/Kontrolldateien autorisieren keine neue Ausführung.
