# Grid und Ratio bei Countdown und adaptiver Planung

Abgeschlossene Messung vom 16. Oktober 2026 (UTC). **100 gemeinsame Probleme ×
acht Bedingungen = 800 frische Grid-Läufe**, ausgeführt in einer einzigen
nativen Phase. Alle 800 Läufe endeten mit dem richtigen Einzelkandidaten.
Verglichen werden die acht passenden historischen Grid-plus-Ratio-Bedingungen
auf denselben 100 Problemen.

Reines Grid benötigte insgesamt **7.097 statt 6.994 Queries**. Die beobachtete
SDK-Gesamtzeit lag bei **6.005,242 statt 6.707,594 Sekunden**, also 10,47 Prozent
niedriger. Die zeitversetzten Messsitzungen und unterschiedliche
Betriebsüberwachung erlauben daraus keinen isolierten kausalen Laufzeitnachweis
für die Queryquelle.

## Fragestellung und Versuchsaufbau

Wie verändert die Queryquelle oberhalb der letzten Planungsebene die Anzahl
der Fragen und die Rechenzeit bei Countdown und adaptiver Planung?

| Parameter | Festlegung |
| --- | --- |
| Unabhängige Probleme | Dieselben 100 ungefilterten Fälle aus Masterseed `2026101601` wie in der [vorherigen Studie](../strategy-grid100-progress001-20261016T030055Z/README.md) |
| Ziele / Alternativen | 5 / 5 |
| Maximale Planungstiefe | 2 |
| Strategien | Fester Countdown und adaptive erwartete Kandidatenverringerung pro erwarteter Query |
| Gridgrößen | 3, 5, 10, 20 |
| Neue Queryquelle | Oberhalb der letzten Ebene ausschließlich Grid; letzte Ebene ausschließlich Ratios |
| Historische Vergleichsquelle | Oberhalb der letzten Ebene Grid + Ratios; letzte Ebene ausschließlich Ratios |
| Bewertung / Abschluss | `candidate_count` / `single_candidate` |
| Mindestfortschritt | `0.001` pro vollständigem Planungshorizont |
| Ausführung | Acht Worker, ein nativer Thread, Linux `forkserver` |
| Wahrscheinlichkeiten | Geometrische Volumenberechnung ohne Sampling |
| Wiederholungen / Limits | Eine Ausführung pro Zelle; kein Zeit- oder Querylimit; kein Profiling |

Bei adaptiver Planung bleiben Horizont-eins-Bewertungen Ratio-Bewertungen.
„Grid“ bezeichnet hier daher die Queryquelle oberhalb der letzten Ebene.
Die [unveränderte Primärzuordnung](protocol/primary-mapping.json) bindet alle
800 neuen Zellen an ihre Jobs in der einzigen Phase `all100`.

Der Umfang wurde nach Sichtung der ersten drei Fälle einer früheren
Grid-Vorserie auf Countdown und adaptiv eingeschränkt. Bei fester Neuplanung
kann die hypothetische Ratio-Endstufe wiederholt verschoben werden. Diese
Begründung ist keine allgemeine Unbrauchbarkeitserklärung für Neuplanung; die
Umfangswahl bleibt eine **nachträgliche Festlegung**. Keines der 100 Probleme
wurde anhand seines Ergebnisses gefiltert.

Es gibt **kein Carryover** aus der Vorserie. Ihre 47 Versuche mit 45 korrekten
Ergebnissen, einem numerischen Fehler und einer Unterbrechung sowie 1.153
nicht gestartete Zellen bleiben ausschließlich historischer Anhang. Auch ihre
30 abgeschlossenen Countdown-/Adaptiv-Zellen zählen nicht zur neuen Primärgruppe.
Die [Baseline-Referenz](provenance/baseline-reference.json) bindet die 800
ausgewählten Both-Zellen an den vollständigen unveränderten Bestand von 1.200
historischen Zellen. Es wurden keine Both-Läufe wiederholt.

## Ergebnisse je Bedingung

Alle Zahlenpaare zeigen **Grid + Ratio → Grid**. Jede Zeile umfasst 100
gemeinsam korrekt gelöste Probleme; „weniger / gleich / mehr“ zählt die
Queryzahl von Grid relativ zu Grid + Ratio mit Nenner 100.

| Strategie | Grid | Korrekt je Quelle / 100 | Ø Queries | Ø SDK-Zeit (s) | Grid weniger / gleich / mehr |
| --- | ---: | ---: | ---: | ---: | ---: |
| Countdown | 3 | 100 | 9,39 → 10,02 | 2,479 → 2,217 | 16 / 49 / 35 |
| Countdown | 5 | 100 | 8,88 → 8,94 | 3,470 → 3,124 | 17 / 51 / 32 |
| Countdown | 10 | 100 | 8,92 → 8,90 | 6,309 → 5,648 | 16 / 61 / 23 |
| Countdown | 20 | 100 | 8,64 → 8,75 | 11,564 → 10,671 | 8 / 77 / 15 |
| Adaptiv | 3 | 100 | 8,81 → 8,93 | 4,320 → 3,464 | 4 / 82 / 14 |
| Adaptiv | 5 | 100 | 8,49 → 8,81 | 6,319 → 5,499 | 6 / 81 / 13 |
| Adaptiv | 10 | 100 | 8,60 → 8,49 | 11,491 → 10,213 | 9 / 84 / 7 |
| Adaptiv | 20 | 100 | 8,21 → 8,13 | 21,125 → 19,216 | 9 / 85 / 6 |

Grid bietet damit keinen allgemeinen Queryvorteil. Countdown mit Grid 3 hatte
die geringste mittlere SDK-Zeit der neuen Bedingungen; adaptiv mit Grid 20
benötigte die wenigsten Queries. Innerhalb der beiden neuen Modi sank die
mittlere Queryzahl mit den untersuchten feineren Grids, während die Rechenzeit
stieg. Die Wahl hängt vom Aufwand einer Frage und der verfügbaren Rechenzeit
ab. Die Grids sind nicht durchgängig verschachtelte Querymengen; keine
Konfiguration wird als universell beste Wahl ausgewiesen.

Einzelne Nachteile bleiben sichtbar: Bei `d5-m5-c000070` benötigte adaptiv mit
Grid 5 **54 statt 39 Queries**. Die
[100-Zeilen-Tabelle](results/comparison-100-problems.csv) enthält Queryzahl,
SDK-Zeit, Status, Endgrund und Qualität für alle 16 neuen und historischen
Bedingungen je Problem. [Queryübersicht](results/queries-100-problems.md),
[ausführliche Ergebnisse](results/results.json) und
[ursprüngliches Fazit](results/conclusion.md) erhalten Einzelfälle,
Verteilungen, Ausreißer und gepaarte Vergleiche samt Nennern.

## Prüfung und Rechenkosten

Alle **7.097 tatsächlichen Antworten**, die Gewinner sowie die gespeicherten
Fortschritts- und Countdownabläufe wurden unabhängig geprüft. Es gab **50
erfolgreiche Countdown-Ersatzplanungen**, keine falsche Auswahl, keinen
ungelösten Abschluss, keinen Fehler, keine Unterbrechung und keinen
Anfangssingleton in den 800 neuen Zellen. Der
[Abschlussbericht](provenance/final-report.json) und die
[Prüfzusammenfassung](provenance/verification-summary.json) binden die Nachweise.

Die native Serie benötigte **6.980,589 Sekunden**, rund **1 h 56 min 20 s**.
Die anschließenden nativen Prüf- und Exportstufen dauerten 355,012 Sekunden;
die Analyse weitere rund 17,7 Sekunden. Die abschließende Mac-Sicherung endete
am 16. Oktober um 23:02:37 UTC, rund 7½ Minuten nach dem Ende der Serie.
SDK-, Fall- und Controllerzeiten sind ineinander enthalten und werden nicht
addiert. Die Kosten aller alten 47 Grid-Versuche und der vollständigen
historischen Both-Studie bleiben gesondert ausgewiesen; deren ausgewählte
800 Zellen werden nicht doppelt gezählt.

Die Studie enthält **100 unabhängige Probleme**, keine 800 oder 1.600
unabhängigen Qualitätsfälle. Es gibt keine Timingwiederholungen;
Verteilungsmediane beschreiben verschiedene Probleme. Auf zusätzliche zeitnahe
Both-Kontrollen wurde verzichtet. Die Rohprüfung zertifiziert keine
hypothetischen geometrischen Planbewertungen neu. Für diese Serie wurde kein
zusätzliches natives Seal mit einer zweiten vollständigen Datenkopie erzeugt;
Originaldaten, Audit, Exporte und der abschließende Hashvergleich bleiben erhalten.

## Downloads und Quellenbindung

Der [Studien-Release v1](https://github.com/janoberwahrenbrock/bachelorarbeit-optimal-tradeoff-queries/releases/tag/study%2Fquery-source-grid100-ca-20261016T205019Z%2Fv1)
stellt das Rohdatenpaket, das Veröffentlichungsmanifest und `SHA256SUMS` bereit.
[downloads.json](downloads.json) nennt Dateinamen, Größen und Prüfsummen;
das [Veröffentlichungsmanifest](publication-manifest.json) bindet jede Datei an
ihren ursprünglichen Projektpfad.

Das neue ZIP enthält alle neuen Primärdaten und die für ihre unveränderte
Offlineanalyse benötigten festen Both-Referenzen. Die vollständigen historischen
Both-Rohdaten bleiben im bereits veröffentlichten
[alten Release](https://github.com/janoberwahrenbrock/bachelorarbeit-optimal-tradeoff-queries/releases/tag/study%2Fstrategy-grid100-progress001-20261016T030055Z%2Fv1);
sie werden nicht ein zweites Mal publiziert. Für eine zusätzliche vollständige
Rohprüfung dieser Baseline beschreibt die
[Reproduktionsanleitung](reproduction/README.md) den getrennten Bezug.

Gemessen wurde das originale Wheel aus Buildcommit
`8256508bd711ab9b98a742f3a2741938fcc4d3bd`, Quellinventar
`47c3d8b2f66446e1ba07f4538879ac9a99bdb567f3082bff254564ff2736ca76`,
Wheel-SHA-256
`509d0441bda0d58d3cbe9b9c5ffcfdd25d8a4b015ad603eb604fdd7023887f19`.
Spätere Main- und Veröffentlichungscommits sind davon getrennt; siehe
[Quellenbindung](provenance/source.json),
[Ausführungsprofil](provenance/execution-profile.json),
[Umgebungsstand](provenance/environment-lock.txt) und
[Studienprotokoll](protocol/study-protocol.json).

Für einen Verweis in der Bachelorarbeit: **„Grid und Ratio bei Countdown und
adaptiver Planung, 16. Oktober 2026, 100 Probleme, 800 neue Läufe und 800
historische Vergleichszellen, Veröffentlichung v1“**, mit dem versionierten
Studien-Release. Die Studienkennung lautet
`query-source-grid100-ca-20261016T205019Z`.
