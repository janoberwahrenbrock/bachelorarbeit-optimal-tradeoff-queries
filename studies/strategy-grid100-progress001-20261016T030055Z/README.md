# Strategien und Gridgrößen: 100 Probleme

Abgeschlossene Studie vom 16. Oktober 2026. **100 unabhängige Probleme × zwölf
Konfigurationen = 1.200 Läufe**, jeweils einmal ausgeführt. Alle 1.200 Läufe
endeten mit dem richtigen Einzelkandidaten. Diese Seite ist die gemeinsame
Referenz der gesamten Studie.

## Fragestellung und Versuchsaufbau

Wie verändern Neuplanung, Countdown und adaptive Verringerung pro erwarteter
Query bei unterschiedlichen Gridgrößen die Queryzahl und die Rechenzeit?

| Parameter | Festlegung |
| --- | --- |
| Unabhängige Probleme | 100 neue, ungefilterte Fälle; Masterseed `2026101601` |
| Ziele / Alternativen | 5 / 5 |
| Maximale Planungstiefe | 2 |
| Strategien | Feste Neuplanung, fester Countdown, adaptive Verringerung pro erwarteter Query |
| Gridgrößen | 3, 5, 10, 20 |
| Queryquellen | Oberhalb der letzten Ebene Grid + Ratios; letzte Ebene nur Ratios |
| Bewertung / Abschluss | `candidate_count` / `single_candidate` |
| Mindestfortschritt | `0.001` pro vollständigem Planungshorizont |
| Ausführung | Acht Worker, ein nativer Thread, Linux `forkserver` |
| Wahrscheinlichkeiten | Geometrische Volumenberechnung ohne Sampling |
| Wiederholungen / Limits | Eine Ausführung pro Zelle; kein Zeit- oder Querylimit; kein Profiling |

Die ersten drei Probleme wurden als vorgeschaltete Kontrolle mit 36 Läufen
ausgeführt; danach folgten die übrigen 97 mit 1.164 Läufen. Beide Abschnitte
gehören zur vorab festgelegten Primärgruppe. Kein Fall wurde ausgeschlossen oder
wiederholt. Die unveränderte [Zuordnung aller 1.200 Zellen](protocol/primary-mapping.json)
bindet jeden Lauf an seine ursprüngliche Phase und Jobkennung.

## Ergebnisse

| Strategie | Grid | Korrekt / 100 | Ø Queries | Ø SDK-Zeit je Problem (s) |
| --- | ---: | ---: | ---: | ---: |
| Neuplanung | 3 | 100 | 10,46 | 4,967 |
| Countdown | 3 | 100 | 9,39 | 2,479 |
| Adaptiv | 3 | 100 | 8,81 | 4,320 |
| Neuplanung | 5 | 100 | 11,49 | 8,124 |
| Countdown | 5 | 100 | 8,88 | 3,470 |
| Adaptiv | 5 | 100 | 8,49 | 6,319 |
| Neuplanung | 10 | 100 | 11,56 | 15,242 |
| Countdown | 10 | 100 | 8,92 | 6,309 |
| Adaptiv | 10 | 100 | 8,60 | 11,491 |
| Neuplanung | 20 | 100 | 14,52 | 34,375 |
| Countdown | 20 | 100 | 8,64 | 11,564 |
| Adaptiv | 20 | 100 | 8,21 | 21,125 |

Countdown mit Grid 3 hatte die geringste mittlere SDK-Zeit; adaptiv mit Grid 20
benötigte die wenigsten Queries. Die Wahl hängt damit vom Verhältnis zwischen
Rechenaufwand und Anzahl der zu beantwortenden Fragen ab. Die Studie begründet
keine universell beste Konfiguration. Die Grids 3, 5, 10 und 20 sind außerdem
nicht durchgängig verschachtelte Querymengen.

Die [100-Zeilen-Tabelle](results/comparison-100-problems.csv) enthält Queryzahl,
SDK-Zeit, Status, Endgrund und Qualität für alle zwölf Bedingungen je Problem.
Die [Queryübersicht](results/queries-100-problems.md) ist direkt lesbar.
[results.json](results/results.json) enthält alle Einzelläufe, Kandidatenverläufe,
Planungstiefen, vollständige Verteilungen und 30 gepaarte Vergleiche mit Nennern.
Das ursprüngliche [Fazit](results/conclusion.md) bleibt unverändert erhalten.

## Laufzeiten und Prüfgrenzen

Vom ersten Fallstart bis zum letzten Fallabschluss vergingen **4 h 08 min 07 s**.
Die anschließende native Abschlussprüfung und Archivierung dauerte weitere
**57 min 56 s**, die abschließende Mac-Sicherung endete knapp drei Minuten später.
Diese Verwaltungskosten sind separat von den SDK-Zeiten auszuweisen. SDK-, Fall-
und Controllerzeiten sind ineinander enthaltene Messgrenzen und werden nicht addiert.

Alle 11.797 tatsächlichen Antworten und die wahren Gewinner wurden unabhängig
geprüft. Es gab 58 Countdown-Ersatzplanungen, alle erfolgreich; keine falsche
Auswahl, keinen ungelösten Abschluss, keinen Fehler und keine Unterbrechung.
Siehe [Prüfzusammenfassung](provenance/verification-summary.json).

Die 1.200 Läufe sind **keine 1.200 unabhängigen Qualitätsfälle**. Es gibt keine
Timingwiederholungen; Median und P90 beschreiben die 100 verschiedenen Probleme
einer Bedingung. Die Rohprüfung ist keine erneute geometrische Zertifizierung
aller hypothetischen Planbewertungen.

## Downloads und Nachvollziehbarkeit

Der [Studien-Release v1](https://github.com/janoberwahrenbrock/bachelorarbeit-optimal-tradeoff-queries/releases/tag/study%2Fstrategy-grid100-progress001-20261016T030055Z%2Fv1)
stellt die vollständigen wissenschaftlichen Rohdaten, das originale Lauf-Wheel,
alle eingefrorenen Studienwerkzeuge und Prüfnachweise bereit. Die
[Downloadbeschreibung](downloads.json) nennt Dateigrößen und SHA-256-Prüfsummen.

Das [Veröffentlichungsmanifest](publication-manifest.json) bindet jede enthaltene
Datei an ihren ursprünglichen Pfad, ihre Größe und Prüfsumme. Die Duplikate der
versiegelten Sicherungen sind ausgelassen; alle Originalphasen und beide
Seal-Inventare bleiben erhalten. Die vollständige native Sealansicht lässt sich
bei Bedarf gesondert rekonstruieren. Historische Originalbelege enthalten
Rechnernamen, lokale Pfade und damalige Betriebsanweisungen. Für die Nutzung
nach dem Download gilt die [Reproduktionsanleitung](reproduction/README.md).

Die historische Qualifikationsbescheinigung und ihre sechs Berichte sind
enthalten. Frühere Entwicklungsversuche und die vollständigen
Qualifikationsfallarchive gehören nicht zu diesem wissenschaftlichen Datenpaket.

Der gemessene Wheel-Build stammt aus Commit
`8256508bd711ab9b98a742f3a2741938fcc4d3bd`, Quellinventar
`47c3d8b2f66446e1ba07f4538879ac9a99bdb567f3082bff254564ff2736ca76`.
Der spätere Main-Stand und der Veröffentlichungscommit sind davon getrennt;
siehe [Quellenbindung](provenance/source.json),
[Ausführungsprofil](provenance/execution-profile.json) und
[Umgebungsstand](provenance/environment-lock.txt).

Für einen Verweis in der Bachelorarbeit: **„Strategien-/Gridvergleich,
16. Oktober 2026, 100 Probleme, 1.200 Läufe, Veröffentlichung v1“**, zusammen
mit dem oben verlinkten versionierten Studien-Release. Die Studienkennung lautet
`strategy-grid100-progress001-20261016T030055Z`.
