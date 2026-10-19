# Studien veröffentlichen

Abgeschlossene Studien werden unter einer festen Studienkennung veröffentlicht.
Die zentrale Studienseite gehört zum Repository; die vollständigen Rohdaten
werden über einen zugehörigen GitHub-Release angeboten. Das ist eine getrennte
Veröffentlichung vorhandener Daten und startet weder neue Solverläufe noch eine
erneute vollständige native Audit-/Seal-Erstellung.

## Öffentliche Ablage

```text
studies/
  README.md
  <study-id>/
    README.md
    publication-manifest.json
    protocol/
    configurations/
    inputs/
    results/
    provenance/
    reproduction/
```

`README.md` erläutert Fragestellung, Methode, Fallzahlen, Messgrenzen,
Ergebnisse, Einschränkungen und Downloads. Eingaben, Konfigurationen und
native JSON-/CSV-Belege werden als unveränderte Veröffentlichungskopien
übernommen. Neue Erläuterungen stehen in eigenen Dateien. Das
Veröffentlichungsmanifest ordnet alle ausgewählten Dateien ihren ursprünglichen
Projektpfaden und Prüfsummen zu.

`results/` enthält die gemeinsame Problemtabelle, ausführliche Ergebnisse und
Auswertung. Pro Bedingung bleiben Queryzahl, Laufzeit, Endgrund und Qualität
sichtbar. Anzahl unabhängiger Probleme, Bedingungen, Wiederholungen und
Versuche werden getrennt genannt. Ein gemeinsames Mapping verbindet
gegebenenfalls mehrere native Teilserien, ohne deren IDs, Audits oder
Originaldaten umzuschreiben.

`provenance/` bindet die tatsächlich gemessenen Quellen, Wheel, Ausführungsprofil,
Umgebung und Prüfnachweise. Gemessener Buildcommit, spätere Codecommits und
Veröffentlichungscommit sind getrennte Identitäten. Eine Quellenidentität wird
nicht allein deshalb auf einen späteren Commit übertragen, weil dessen
Algorithmus gleich geblieben ist.

## Umfang des Rohdatenpakets

Das Paket enthält die ausgewählten Originaldateien unter ihren ursprünglichen
`inputs/`- und `runs/`-Pfaden. Dazu gehören gespeicherte Probleme und Antworten,
Konfigurationen, native Resultate und Journale, Planungsaufzeichnungen,
Exports, Auditbelege und die Werkzeuge für die unabhängige Auswertung. Das
Manifest ist die verbindliche Dateiliste; es ersetzt keine wissenschaftliche
Beschreibung der Messung.

Identische vollständige Kopien im nativen Seal-Payload und im originalen
Serienverzeichnis werden einmal verpackt. Die ursprünglichen
Sealinventare bleiben erhalten. Inhaltlich unterschiedliche materialisierte
Eingaben und sämtliche tatsächlichen Versuche bleiben getrennt erhalten.
Eine native Sealprüfung erwartet ihre vollständige ursprüngliche
Archivansicht; die Veröffentlichung ist kein direkt unverändert entpacktes
Seal. Die studienspezifische Anleitung beschreibt, wie diese Ansicht bei
Bedarf aus den Originaldateien und Inventaren wiederhergestellt wird.
Die Paketprüfung prüft die veröffentlichten Dateien gegen das Manifest.

Virtuelle Umgebungen, Caches, redundante Sicherungskopien und laufende
Synchronisationsstatus sind keine Pflichtbestandteile. Die vollständige
Entwicklungsqualifizierung ist von wissenschaftlichen Primärdaten getrennt.
Eine Veröffentlichung darf nur dann deren vollständige Nachprüfung behaupten,
wenn die zugehörigen Dateien tatsächlich enthalten sind.

## Paket bauen und prüfen

Die Veröffentlichung arbeitet lesend auf den ausgewählten Originaldateien.
Ein Build darf bestehende eingefrorene Studien, terminale Resultate oder
bereits publizierte Pakete nicht ersetzen. Neue Ausgabedateien erhalten neue
Pfade. Ersetze `example-study` im folgenden Beispiel durch die zu prüfende
Studienkennung. Die Befehle werden vom Projektroot aus ausgeführt:

```sh
study_id=example-study
mkdir -p runs/publication-v1
python3 tools/publication/study_bundle.py build \
  --project-root "$PWD" \
  --manifest "studies/$study_id/publication-manifest.json" \
  --output "runs/publication-v1/$study_id-v1.zip"

python3 tools/publication/study_bundle.py verify \
  --manifest "studies/$study_id/publication-manifest.json" \
  --archive "runs/publication-v1/$study_id-v1.zip" \
  --destination runs/publication-v1/fresh-extraction
```

Das Zielverzeichnis der Entpackprüfung muss neu sein. Die Prüfung gleicht
Dateimenge, Pfade, Größen und Prüfsummen ab. Die zusätzliche wissenschaftliche
Prüfung gleicht Tabellen und die ursprüngliche Zuordnung aller Ergebnisse
anhand der enthaltenen Rohdaten ab. Die jeweilige Reproduktionsanleitung nennt
das enthaltene Auswertungswerkzeug und seine benötigten Dateien.

Eine erneute Auswertung schreibt einen neuen Analyseordner. Sie überschreibt keine
Originalresultate. Ihr Nachweis betrifft Quellenbindung, gespeicherte Queries,
Antworten, Gewinner und Ablauf; er ist keine geometrische Neuzertifizierung
sämtlicher hypothetischer Planbewertungen. Die studienspezifische
Reproduktionsanleitung erläutert die genaue Übereinstimmungsprüfung.

Eine erneute Algorithmusausführung ist ein eigener Weg: passende Python-/
Numerikumgebung herstellen, das gemessene Wheel prüfen und installieren,
auf dem tatsächlichen Ausführungshost nativ qualifizieren und einen neuen
Serienplan aus den publizierten Eingaben und Konfigurationen erstellen.
Alte Maschinenpfade und Prozesssteuerungsdateien werden nicht als neuer
Startbefehl verwendet. Neue Läufe erhalten neue Kennungen; ihre Laufzeiten
müssen nicht mit den ursprünglichen Messungen identisch sein.

## GitHub-Release und abschließende Downloadprüfung

Nach bestandener lokaler Prüfung werden Studienseite, ausgewählte kompakte
Dateien, Manifest und aktuelle Dokumentation gemeinsam auf Main übernommen.
Ein Studien-Tag der Form `study/<study-id>/v1` bindet den Veröffentlichungscommit.

Der zugehörige Release bietet folgende Downloads:

- das Datenpaket `<study-id>-v1.zip`;
- `publication-manifest.json` mit der ursprünglichen Dateizuordnung;
- `SHA256SUMS` für die herunterladbaren Dateien.

Die automatisch von GitHub angebotenen Quellcodearchive enthalten die
versionierten Repositorydateien. Das zusätzliche Rohdatenpaket ist ein eigener
Release-Download und muss ausdrücklich gewählt werden. Studienseite und
Releasebeschreibung verlinken sich gegenseitig.

Die tatsächliche komprimierte Größe entscheidet über eine Aufteilung. Ein
zu großes Paket wird in mehrere separat entpackbare Dateien mit gemeinsamem
Manifest gegliedert; die Studie behält dabei eine einzige Kennung und
Referenz. Die Teilpaketzuordnung wird vor der Veröffentlichung festgelegt und
beim frischen Download vollständig geprüft. Kein Originalfall wird aus
Größengründen weggelassen.

Das aktuelle Werkzeug baut ein einzelnes ZIP und weist Dateien ab 2 GiB zurück.
Eine künftige Aufteilung benötigt je ZIP ein eigenes Dateimanifest und eine
gemeinsame Downloadübersicht; automatisches Sharding ist derzeit nicht
implementiert.

Nach Veröffentlichung werden die tatsächlichen Release-Dateien einmal in ein
neues Verzeichnis geladen. Ihre Prüfsummen und der Paketinhalt werden erneut
geprüft. Erst dann gilt die Veröffentlichung als vollständig. Ergebnisse
werden nicht allein anhand eines erfolgreich abgeschlossenen Uploads als
öffentlich reproduzierbar bezeichnet.

## Spätere Studien und Korrekturen

Jede neue Studie erhält einen eigenen Eintrag im Studienkatalog und eine neue
Studienkennung. Sie übernimmt weder stillschweigend Fallzahlen noch
Qualifizierungsbehauptungen früherer Studien. Die gemeinsame
Veröffentlichungsstruktur und das Paketwerkzeug werden wiederverwendet.

Veröffentlichte Originalarchive und ihre Prüfsummen bleiben unverändert.
Eine Korrektur erzeugt eine neue Veröffentlichungsversion, einen neuen Tag und
einen Änderungsvermerk mit Grund und betroffenen Aussagen. Die alte Version
bleibt auffindbar. Wissenschaftliche Originaldaten werden dabei nicht durch
nachträglich günstigere Ausführungen ersetzt.
