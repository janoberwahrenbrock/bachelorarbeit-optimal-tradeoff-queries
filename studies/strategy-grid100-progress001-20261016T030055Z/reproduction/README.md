# Ergebnisse prüfen und Experimente wiederholen

Die ersten beiden Wege verwenden vorhandene Daten und starten keinen Solver.
Für die Werkzeuge dieses Repositories wird Python 3.13 oder 3.14 verwendet.
Die originalen Studienwerkzeuge im Datenpaket benötigen ausschließlich die
Python-Standardbibliothek. Befehle werden vom geklonten Repository aus ausgeführt.

## 1. Tabellen aus den kompakten Ergebnissen nachrechnen

```sh
python3 tools/publication/compare_analysis.py \
  --reference studies/strategy-grid100-progress001-20261016T030055Z/results/results.json
```

Dieser Aufruf berechnet Fallzahlen und Mittelwerte unmittelbar aus den
gespeicherten Einzelmessungen. Die vollständigen Verteilungen und gepaarten
Vergleiche stehen in derselben Ergebnisdatei. Die CSV enthält 100 Zeilen mit
den zwölf Bedingungen je Problem.

## 2. Originale Rohdaten unabhängig auswerten

Lade das ZIP, `publication-manifest.json` und `SHA256SUMS` vom
[Release v1](https://github.com/janoberwahrenbrock/bachelorarbeit-optimal-tradeoff-queries/releases/tag/study%2Fstrategy-grid100-progress001-20261016T030055Z%2Fv1)
in ein neu angelegtes Verzeichnis unter `runs/`. Die folgenden Befehle verwenden
`runs/published-grid100-v1/` als Downloadverzeichnis. Prüfe dort zuerst mit
`shasum -a 256 -c SHA256SUMS` (macOS) oder `sha256sum -c SHA256SUMS` (Linux)
die tatsächlichen Downloadbytes. Das Manifest muss mit der versionierten
Datei im Repository übereinstimmen.

Vom Repositoryroot aus:

```sh
python3 tools/publication/study_bundle.py verify \
  --manifest studies/strategy-grid100-progress001-20261016T030055Z/publication-manifest.json \
  --archive runs/published-grid100-v1/strategy-grid100-progress001-20261016T030055Z-v1.zip \
  --destination runs/published-grid100-v1/extracted

python3 runs/published-grid100-v1/extracted/inputs/strategy-grid100-progress001-20261016T030055Z/analyze_series.py \
  --project-root "$PWD/runs/published-grid100-v1/extracted"
```

Das Entpackziel muss neu sein. Die Paketprüfung kontrolliert alle Dateien,
Pfade, Größen und SHA-256-Werte vor dem Entpacken. Sie benötigt etwa 1,3 GB
für den entpackten Inhalt zusätzlich zum Download. Das Paket enthält
**sämtliche 1.200 tatsächlichen Versuche**, die 100 ursprünglichen Eingaben,
zwölf Konfigurationen, beide nativen Serien und die ursprünglichen Werkzeuge.

Der zweite Aufruf erzeugt und nennt einen neuen Analyseordner. Er prüft die
Quellenbindung, gespeicherten Antworten und Gewinner, Queryzähler,
Fortschrittsentscheidungen und Countdownabläufe und gleicht die nativen Exporte
ab. Verwende dessen `results.json` für den Vergleich:

```sh
python3 tools/publication/compare_analysis.py \
  --reference studies/strategy-grid100-progress001-20261016T030055Z/results/results.json \
  --reproduced /ABSOLUTER/PFAD/ZUM/NEUEN/ANALYSEORDNER/results.json
```

Nur der neu erzeugte Zeitstempel `generated_at_utc` wird beim Vergleich
ausgenommen. Alle Messwerte, Verteilungen, Einzelfälle, Paarvergleiche und
Herkunftsbindungen müssen übereinstimmen. Diese Prüfung berechnet keine
hypothetischen Geometrien neu und erzeugt keine neuen Laufzeitmessungen.

### Optionale vollständige native Sealansicht

Die identischen Seal-Payloadkopien sind im Download ausgelassen, die beiden
originalen `archive_inventory.json` bleiben enthalten. Für die ursprüngliche
native Sealprüfung rekonstruiert man eine neue Ansicht außerhalb der
unveränderlichen Rohphasen: Für jeden Inventareintrag wird die gleichnamige
Datei aus der zugehörigen Originalphase kopiert und zuletzt das ursprüngliche
Inventar als `archive_inventory.json` ergänzt. Die Quelle eines Eintrags ist
also `phases/<phase>/<Eintragspfad>`, nicht ein anderes Master-Dataset.
Die Gesamtdateimenge dieser Ansicht ist exakt die Inventarliste plus Inventar;
es werden keine weiteren Verzeichnisse übernommen. Anschließend lässt sich
`otqa.analysis.seal.verify_seal` mit dem extern veröffentlichten Inventarhash
anwenden, wie in [docs/seal.md](../../../docs/seal.md) beschrieben.
Diese zusätzliche Ansicht benötigt rund 1,26 GB und ist für die obige
unabhängige Rohdatenanalyse nicht erforderlich.

## 3. Neue Algorithmusläufe mit denselben Eingaben

Dieser Weg führt neue Berechnungen durch. Die vorhandenen nativen Serien sind
abgeschlossene Archive und werden auf einem anderen Rechner nicht fortgesetzt.

1. Checke den tatsächlichen Lauf-Buildcommit
   `8256508bd711ab9b98a742f3a2741938fcc4d3bd` in einem eigenen Checkout aus.
2. Vergleiche das mitgelieferte Wheel unter
   `inputs/strategy-grid100-progress001-20261016T030055Z/installation/` mit dem
   Wheelhash im Studienprotokoll. Installiere dieses Wheel in einer eigenen
   Umgebung mit Python 3.13 oder 3.14; die ursprünglichen Bibliotheksversionen
   stehen im [Umgebungsstand](../provenance/environment-lock.txt).
3. Übernimm gespeicherte Probleme, Oracle-Dateien und vollständige Konfigurationen
   in den neuen Projektroot. Erzeuge eine neue Suite und einen neuen Serienplan
   mit eigenen Kennungen nach [docs/benchmarks.md](../../../docs/benchmarks.md).
   Für eine gemeinsame 100er-Serie verwende alle 100 ursprünglichen Case-IDs
   bei allen zwölf Konfigurationen und genau eine Wiederholung.
4. Qualifiziere die installierte Quelle auf dem tatsächlichen Ausführungshost
   nach [docs/cli.md](../../../docs/cli.md#installation-and-native-qualification).
   Für Linux-Serien ist `series_linux_recovery` erforderlich. Das historische
   Ausführungsprofil aus dem Download dient der Herkunftsdokumentation.
5. Starte ausschließlich den neu erzeugten Plan. Vergleiche Queryzahlen,
   Qualität und Endgründe gemeinsam mit den neuen Messzeiten.

Die alten Worker-/Prozessidentitäten, lokalen Rechnerpfade und Betriebsanweisungen
in den historischen Originalbelegen werden dabei nicht als neue Startanweisung
verwendet. Eine andere Maschine oder Bibliotheksumgebung kann andere Laufzeiten
und numerische Grenzfälle ergeben; die Veröffentlichung verspricht keine
identischen neuen Messwerte.
