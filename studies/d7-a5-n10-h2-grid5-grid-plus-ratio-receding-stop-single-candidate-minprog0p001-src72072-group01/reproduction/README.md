# Offline-Nachpruefung des eigenstaendigen Pakets

Der portable Einstieg und die wissenschaftlichen Vergleichsregeln bleiben unveraendert. Die urspruenglichen Roh-/Reportbelege tragen ihren damaligen Erstellungsstatus; spaetere Inhaltsgates stehen in ../provenance/verification-summary.json. Die konkrete Archivpruefung steht im getrennten package-validation.json.

# Offline-Nachprüfung

Dieses Paket benötigt für die gespeicherte wissenschaftliche Nachprüfung nur Python3.13 oder3.14 und die Standardbibliothek. Keine Installation des Algorithmus, kein Netzwerk und keine anderen Studienarchive.

Nach Manifest-/ZIP-Prüfung in ein frisches Verzeichnis:

```sh
python3 studies/d7-a5-n10-h2-grid5-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072-group01/reproduction/reproduce.py --project-root /ABS/EXTRACTED --output /ABS/FRESH-ANALYSIS
```

Der portable Einstieg ruft die reinen APIs `analyze(project_root, series_path)` und `verify_study(project_root, series_path, finish_proof, wheel, prepared_index)` auf. Die ursprünglichen interaktiven Tools enthalten Mac-Schutzregeln für ihre Ausgabeverzeichnisse; deren CLI ist hier ausdrücklich nicht der Reproduktionsweg. Nur Erstellungszeit/Prüfdauer tragen keine wissenschaftliche Bedeutung. Alle übrigen Reportwerte sowie CSV und Markdown stimmen überein; Rohprüf-Dateireferenzen werden nur nach portablem Pfad sortiert.

Die fünfzehn ursprünglichen Qualifikationsbelege unterstützen die gespeicherte Belegprüfung. Das Paket behauptet keine vollständige erneute Durchführung aller Entwicklungs-/Fehlerqualifikationen; dazu wären weitere Testfixtures und passende tatsächliche Hardware nötig. Eine neue Solverausführung wäre ein eigener autorisierter Lauf mit neuen IDs und neuer tatsächlicher Hostqualifikation. Alte Steuerungsdateien sind historische Belege, keine Start- oder Wiederaufnahmebefehle.
