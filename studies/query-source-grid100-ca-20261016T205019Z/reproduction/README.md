# Daten prüfen und Ergebnisse reproduzieren

Die Offlineanalyse verwendet gespeicherte Daten und startet keinen Solver.
Die originalen Analysewerkzeuge benötigen nur die Python-Standardbibliothek;
für die Repositorywerkzeuge wird Python 3.13 oder 3.14 verwendet. Alle Befehle
gehen vom geklonten Repository aus.

## Downloads und Prüfsummen

Lade `query-source-grid100-ca-20261016T205019Z-v1.zip`,
`publication-manifest.json` und `SHA256SUMS` aus dem
[Release v1](https://github.com/janoberwahrenbrock/bachelorarbeit-optimal-tradeoff-queries/releases/tag/study%2Fquery-source-grid100-ca-20261016T205019Z%2Fv1)
in ein neues Verzeichnis `runs/published-query-source-grid100-ca-v1/`.
[downloads.json](../downloads.json) bindet Größen und SHA-256-Werte.

Prüfe vor dem Entpacken die Downloadbytes. Auf macOS:

```sh
(cd runs/published-query-source-grid100-ca-v1 && shasum -a 256 -c SHA256SUMS)
```

Unter Linux lautet das entsprechende Programm `sha256sum`. Das heruntergeladene
Manifest muss mit der versionierten Datei
`studies/query-source-grid100-ca-20261016T205019Z/publication-manifest.json`
übereinstimmen. Die anschließende Paketprüfung kontrolliert Dateimenge, Pfade,
Größen und Prüfsummen und entpackt ausschließlich in ein neues Ziel:

```sh
python3 tools/publication/study_bundle.py verify \
  --manifest studies/query-source-grid100-ca-20261016T205019Z/publication-manifest.json \
  --archive runs/published-query-source-grid100-ca-v1/query-source-grid100-ca-20261016T205019Z-v1.zip \
  --destination runs/published-query-source-grid100-ca-v1/extracted
```

## Originale Analyse ausführen und vergleichen

Das ZIP erhält die ursprünglichen projektbezogenen Pfade. Es enthält die
800 neuen nativen Versuche mit ihren Rohantworten und Journalen, die
eingefrorenen Eingaben und Werkzeuge sowie die festen kompakten
Both-Referenzen. Die ausgeschlossene Grid-Vorserie bleibt historischer Anhang.
Für die folgende Analyse ist kein zusätzlicher Baseline-Download erforderlich.

Führe das unveränderte originale Analysewerkzeug auf dem entpackten Projekt aus:

```sh
python3 runs/published-query-source-grid100-ca-v1/extracted/inputs/query-source-grid100-ca-20261016T205019Z/analyze_series.py \
  --project-root "$PWD/runs/published-query-source-grid100-ca-v1/extracted"
```

Es prüft die neuen gespeicherten Antworten, Gewinner, Quellenbindung,
Queryzahlen, Fortschrittsentscheidungen und Countdownabläufe und gleicht die
nativen Exporte ab. Der vollständige alte Both-Report mit 1.200 Zellen und seine
Zuordnung werden gegen ihre eingefrorenen Hashes geprüft; genau die 800
passenden Zellen gehen in den Vergleich ein. Die historischen 30 fertigen
Countdown-/Adaptiv-Zellen der alten Grid-Vorserie werden nicht übernommen.

Der Aufruf schreibt und nennt einen neuen Analyseordner. Vergleiche dessen
`results.json` mit der veröffentlichten Referenz:

```sh
python3 tools/publication/compare_analysis.py \
  --reference studies/query-source-grid100-ca-20261016T205019Z/results/results.json \
  --reproduced /ABSOLUTER/PFAD/ZUM/NEUEN/ANALYSEORDNER/results.json
```

Der vollständige Vergleich nimmt ausschließlich `generated_at_utc` aus.
Alle anderen Felder einschließlich Einzelfällen, Baselineauswahl,
Versuchskosten, Verteilungen, gepaarten Vergleichen und Herkunftsbindungen
müssen übereinstimmen. Die wissenschaftliche Tabelle hat 100 Zeilen mit
acht neuen und acht historischen Bedingungen.

Eine kurze Nachrechnung der Mittelwerte ist zusätzlich möglich:

```sh
python3 tools/publication/compare_analysis.py \
  --reference studies/query-source-grid100-ca-20261016T205019Z/results/results.json
```

Diese Kurzansicht fasst ausschließlich die **acht neuen Grid-Bedingungen** aus
`rows` zusammen. Die historischen Both-Werte stehen getrennt in
`baseline_rows`, die vollständigen Vergleiche in der CSV und im Ergebnis-JSON.
Die Offlineprüfung erzeugt weder neue Laufzeitmessungen noch eine geometrische
Neuzertifizierung hypothetischer Planungen.

## Optionale vollständige Prüfung der historischen Both-Rohdaten

Die feste [Baseline-Referenz](../provenance/baseline-reference.json) verweist auf
den bereits veröffentlichten
[Both-Release v1](https://github.com/janoberwahrenbrock/bachelorarbeit-optimal-tradeoff-queries/releases/tag/study%2Fstrategy-grid100-progress001-20261016T030055Z%2Fv1).
Dessen ZIP umfasst 66.460.126 Byte, rund 66,46 MB komprimiert. Seine
[Downloadbeschreibung](../../strategy-grid100-progress001-20261016T030055Z/downloads.json)
bindet die Prüfsummen; das Archiv enthält die vollständigen 1.200 alten
Versuche. Es wird nicht nochmals im neuen ZIP veröffentlicht.

Für eine vollständige erneute Rohdatenprüfung der Baseline lade und prüfe
dieses alte Paket in einem **getrennten neuen Verzeichnis** nach dessen
[Reproduktionsanleitung](../../strategy-grid100-progress001-20261016T030055Z/reproduction/README.md).
Entpacke die beiden Pakete nicht übereinander. Die neue Offlineanalyse benötigt
nur ihre bereits enthaltenen festen Baseline-Referenzen; die zusätzliche alte
Rohprüfung prüft die historische Studie selbst.

## Neue Solverläufe sind ein separates Experiment

Die enthaltenen `README.md`- und `CONTINUATION.md`-Dateien dokumentieren den
damaligen Betrieb auf Bench und Mac. Ihre Maschinenpfade, Prozessidentitäten
und `run`-/`resume`-Anweisungen sind historische Belege und dürfen nicht zum
Starten oder Fortsetzen der veröffentlichten Serien verwendet werden.

Eine neue Berechnung erhält eigene Eingabenbindungen, Suite-, Serien- und
Ausgabekennungen. Dafür wird das tatsächlich gemessene Wheel aus Buildcommit
`8256508bd711ab9b98a742f3a2741938fcc4d3bd` anhand des Protokolls geprüft,
in einer eigenen passenden Umgebung installiert und auf dem tatsächlichen
Ausführungshost qualifiziert. Die gespeicherten 100 Fälle und acht
Konfigurationen lassen sich dann nach dem
[Benchmarkworkflow](../../../docs/benchmarks.md) in einem neuen Plan verwenden.
Andere Rechner oder Bibliotheksumgebungen können andere Laufzeiten und
numerische Grenzfälle ergeben.
