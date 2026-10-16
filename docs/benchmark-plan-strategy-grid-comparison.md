# Benchmarkplan für Strategien und Gridgrößen

Stand: 16. Oktober 2026. Status: Umfang und Ausführung autorisiert; die Integration ist implementiert, ihre abschließenden Freigabegates laufen. Die größere Vergleichsserie ist noch nicht gestartet. Der autorisierte Umfang beträgt 100 neue Probleme und 1.200 Läufe für Neuplanung, Countdown und adaptive Strategie mit Grid 3, 5, 10 und 20.

Die Umsetzung selbst folgt dem [Implementierungsplan für Countdown und Mindestfortschritt](implementation-plan-countdown-progress.md). Die dortigen Funktions-, Integrations- und Qualifizierungsprüfungen bleiben Voraussetzung dieser Studie. Dieser Benchmarkplan definiert die anschließende inhaltliche Untersuchung der Varianten.

Der Release-10-Kandidat von Version `0.2.0` bindet Quellinventar
`9339e88e7885015290ca118208e48d45ad58130af3e0058fcc2b50448a4d3b72`. Die Runtime bereitet unveränderliche Schemametadaten einmalig vor,
prüft bekannte Planobjekte mit vollständigen positiven Strukturbelegen und
sammelt binäre Zahlennachweise mit einem gemeinsamen Akkumulator. Der frühere
Nutzdatencache ist entfernt. Alle 40 Schemaressourcen und die numerischen
Verfahren bleiben unverändert.

Die vollständige Testsuite im Hauptcheckout besteht mit 927 Tests in 40.40 Sekunden;
Ruff ist sauber. Unabhängiger Review findet keine offenen P1/P2
im unterstützten nativen JSON-Umfang. Neuer Build sowie frische installierte
Funktions- und Laufzeitgates folgen für diesen konkreten Payload.

Frühere SDK- und Funktionsprüfungen werden nicht auf geänderte Quellen
übertragen. Der [fortlaufende Abnahmestand](../runs/countdown-progress-integration-20261016T030055Z/implementation-state.json)
enthält Quellen, Fehlerhistorie und konkrete Belege.

## Fragestellungen

Die Serie untersucht, welche Variante tatsächlich weniger Fragen bis zur akzeptierten Lösung benötigt und wie viel reale Rechenzeit sie dafür verwendet. Außerdem wird geprüft, wie sich eine Verfeinerung des Grids innerhalb jeder Strategie auswirkt und ob die Rangfolge auf einer größeren gemeinsamen Stichprobe stabil bleibt.

Queryzahl und Rechenzeit werden getrennt ausgewertet. Eine Variante kann weniger Fragen benötigen und zugleich mehr Rechenzeit verbrauchen. Ein schneller ungelöster Abschluss zählt nicht als schnell gelöstes Problem.

## Ausgangsbefund

Die erste passende Vergleichsgruppe umfasste 50 Probleme mit Grid 3 und 5. Eine zweite eigenständige Serie untersuchte 25 neue Probleme mit Grid 3, 5 und 9. In der zweiten Serie wurden alle 225 Läufe korrekt bis zum Einzelkandidaten gelöst. Adaptiv benötigte bei allen drei Grids im Mittel weniger Queries; Countdown benötigte weniger Rechenzeit. Der kleine Queryvorsprung des Countdowns aus der ersten Gruppe bestätigte sich in der zweiten Gruppe nicht.

Die neue Serie verwendet den regulär integrierten Algorithmus mit Countdownneustart und Fortschrittsprüfung. Sie ist keine bloße Erweiterung der historischen Rohserie. Die früheren Quellen, Problemkollektive und Semantiken bleiben separat erhalten.

Vorhandene Projektbelege:

- `runs/strategy-comparison50-grid35-20261015T190920Z/README.md`
- `runs/strategy-grid-extension-20261015T192900Z/analysis/verified-final-20261015T200200Z/conclusion.md`

## Feste Konfiguration

| Größe | Vorgeschlagene Festlegung |
| --- | --- |
| Unabhängige Probleme | 100 neue ungefilterte Probleme; identische Matrizen und Zielgewichte; jede Antwort wird aus der tatsächlich gestellten Query simuliert |
| Ziele | 5 |
| Alternativen | 5 |
| Masterseed | `2026101601`, Erzeugung einmal mit dem nativen Datasetgenerator |
| Maximale Tiefe | 2 |
| Strategien | Fixed mit Neuplanung, Fixed mit Countdown, adaptive Verringerung pro Query |
| Gridgrößen | 3, 5, 10 und 20 |
| Queries oberhalb der letzten Planungsebene | Grid plus Ratios |
| Queries auf der letzten Planungsebene | Nur Ratios |
| Planungsbewertung | `candidate_count` |
| Zielkriterium | `single_candidate` |
| Mindestfortschritt | `0.001` für jede Variante |
| Maximal verfügbare Worker | 8 für jede Variante |
| Native Threads | 1 je Prozess |
| Antwortwahrscheinlichkeiten | Bestehende geometrische Volumenberechnung ohne Sampling |
| Wiederholungen | Eine vollständige Ausführung je Problem und Konfiguration |
| Querybudget | Kein Limit, entsprechend der vorherigen Vergleichsserien |
| Fallzeitlimit | Kein externes Fallzeitlimit |
| Profiling und Diagnosecapture | Ausgeschaltet während dieser Messserie |

Anfangssingletons und von Beginn an erfolglose Fälle werden nicht ausgefiltert oder ersetzt. Bei adaptiver Tiefe zwei werden die Horizonte eins und zwei bewertet. Beim Countdown gelten die neuen regulären Rückfall- und Blockregeln aus dem Implementierungsplan.

Die konkreten erzeugten Problemdateien, Oracle-Dateien, Konfigurationen und Suite werden vor der ersten Ausführung mit Hashes gebunden. Ein Seed allein ersetzt nicht die gespeicherten Eingaben und deren Generatorprovenienz.

## Vergleichsmatrix

| Variante | Grid 3 | Grid 5 | Grid 10 | Grid 20 | Läufe gesamt |
| --- | --- | --- | --- | --- | --- |
| Neuplanung bei fester Tiefe 2 | 100 | 100 | 100 | 100 | 400 |
| Countdown bei fester Tiefe 2 | 100 | 100 | 100 | 100 | 400 |
| Adaptive Strategie bis Tiefe 2 | 100 | 100 | 100 | 100 | 400 |
| Gesamt | 300 | 300 | 300 | 300 | 1.200 |

Die 1.200 Läufe sind zwölf Bedingungen auf denselben 100 unabhängigen Problemen. Sie sind weder 1.200 unabhängige Probleme noch drei Timingwiederholungen. Es werden keine weiteren Schwellenwerte, Konfidenzvarianten oder Dimensionen still hinzugefügt.

Grid 3, 5, 10 und 20 knüpfen an die vorhandene 100er-Sensitivitätsanalyse an und decken einen breiteren Auflösungsbereich ab. Die zuvor vorgeschlagenen Größen 3, 5 und 9 hatten den besonderen Vorteil mathematisch verschachtelter Ausgangsgrids bei identischem Zustand. Für 3, 5, 10 und 20 gilt diese Teilmengenbeziehung nicht durchgängig. Die neue Studie bleibt ein gültiger empirischer Auflösungsvergleich, behauptet aber keine monotone Erweiterung derselben Querymenge.

Die Fortschrittsschwelle ist in dieser Studie überall gleich. Die Studie isoliert damit Strategie und Gridgröße, nicht den Effekt unterschiedlicher Fortschrittsschwellen. Ein kleiner separater Kompatibilitätsvergleich mit deaktivierter Schwelle bleibt Teil der vorherigen Integrationsabnahme; er wird nicht in diese Qualitätsgruppe gemischt.

## Reihenfolge und Betrieb

Vor dem großen Lauf müssen die relevanten Funktionstests und die native Qualifizierung der tatsächlich installierten finalen Quelle bestanden sein. Das Wheelinventar, die numerische Umgebung, das Ausführungsprofil und sämtliche Policywerte werden eingefroren.

Zunächst laufen die ersten drei der ohnehin festgelegten 100 Probleme mit allen zwölf Konfigurationen. Diese 36 Jobs bleiben normale Primärdaten und werden nicht nochmals ausgeführt oder nachträglich als Pilot ausgeschlossen. Sie dienen zugleich der Überprüfung des gesamten Datenflusses und einer aktualisierten Aufwandsschätzung.

Der eine unveränderte 100er-Datensatz wird vorab auf zwei native Serienpläne verteilt: die ersten drei Probleme mit 36 Jobs und die übrigen 97 mit 1.164 Jobs. Eine vor dem Start gespeicherte Zuordnung bindet alle 100 × 12 Primärergebnisse an genau einen Plan und Job. Beide Pläne verwenden dieselben Quellen, Konfigurationen und Eingaben; es gibt keine nachträgliche Fallauswahl. Die ursprüngliche Datasetposition steuert die zyklische Konfigurationsrotation auch im zweiten Abschnitt.

Nach Ende des ersten Abschnitts werden alle 36 Resultate, Rohantworten und Gewinner geprüft sowie ein nativer Audit mit passenden Exporten erstellt. Nur bei konsistenten Belegen und ohne fehlerhafte oder falsche Auswahl folgt der zweite Abschnitt. Reguläre NoQuery- oder Fortschrittsabschlüsse bleiben Primärdaten und sind bei korrekter Evidenz kein Integritätsfehler.

Die Reihenfolge der zwölf Konfigurationen wird vorab festgelegt und je Problem zyklisch rotiert. Problemjobs laufen nacheinander auf Bench i7; ihre Worker konkurrieren nicht mit gleichzeitig gestarteten Solverjobs um dieselben Kerne. Der Wrapper überwacht eigene Fehlerzustände. Bei einem späteren echten Fehler fordert er den bewiesenen eigenen Controller über dessen regulären Interruptpfad zum Stop auf; ein unmittelbar bereits gestarteter Folgeversuch kann dabei als Unterbrechung erhalten bleiben. Es gibt keine stille Wiederholung oder Fallersetzung. Dieses dokumentierte enge Zeitfenster ist keine strikt atomare Zulassungssperre nach jedem Resultat.

Eine lange Laufzeit allein verändert weder Quelle noch Konfiguration und führt nicht zur Fallersetzung. Falls die verfügbare Arbeitszeit keine vollständige Serie erlaubt, bleibt der offene Umfang ausdrücklich pending und wird mit derselben eingefrorenen Quelle fortgesetzt. Begonnene Fälle werden nicht allein wegen einer Laufzeitschätzung abgebrochen.

Controller und Mac-Sicherung werden beim Start nach bestandenen Freigabegates unabhängig vom AI-Run ausgeführt. Eingaben, Rohdaten, Controllerstatus und Fortsetzungsanweisungen liegen in eigenen Studienordnern unter `inputs/` und `runs/`. Vor einer Fortsetzung werden tatsächliche Prozessidentitäten geprüft; fehlender SSH-Zugriff beweist keinen Solverabbruch. Bestehende terminale Ergebnisse werden nicht erneut versucht oder ersetzt.

Ein Quellfehler stoppt die weitere Zulassung neuer Jobs zur Klärung. Eine Reparatur verändert niemals die eingefrorene Quelle einer bereits gestarteten Studie. Läufe einer korrigierten Quelle erhalten eine eigene Quellenbindung und werden nicht still mit den ursprünglichen Ergebnissen zu einer einheitlichen Serie zusammengezählt.

## Gespeicherte Messwerte

Jeder Lauf hält die Eingabe- und Quellenbindung, tatsächliche Queries und Antworten, die konfigurierten Queryquellen, gewählte Planungshorizonte, tatsächliche Kandidatenfolge und die vorhandenen Erwartungswerte fest. Hinzu kommen Fortschrittswerte, Schwellenentscheidungen, Countdownresttiefen und Ersatzversuche nach dem neuen Ereignisvertrag. Die Standardaufzeichnung behauptet keine gesonderte Generatorherkunft jeder ausgewählten Query; die Queryidentität und der Horizont bleiben nachvollziehbar.

Laufzeiten umfassen mindestens die vollständige SDK-Wandzeit und die native Fall-/Controllerzeit als getrennte Größen. Kumulierte Workerzeit wird nicht als Problemlaufzeit ausgegeben. Zusätzliche Messinstrumentierung wird nicht nachträglich nur für ausgewählte Bedingungen aktiviert.

Die Endzustände bleiben getrennt sichtbar: Singleton, `insufficient_expected_progress`, `no_query`, Fehler, Unterbrechung und noch nicht beendeter Fall. Ein Konfidenzabschluss ist in dieser konkreten Konfiguration nicht vorgesehen und müsste als Konfigurationsabweichung untersucht werden. Ein Querybudgetabschluss ist ebenfalls nicht vorgesehen.

## Auswertung

Die Haupttabelle hat 100 Zeilen. Jede der zwölf Varianten erhält Queryzahl, vollständige Laufzeit, Endgrund und Korrektheitsstatus pro Problem. Eine begleitende Detaildatei bindet jedes Ergebnis an seine Rohdateien und enthält die vollständigen tatsächlichen Verläufe.

Pro Variante werden gelöste und korrekt gelöste Fälle von 100, sämtliche ungelösten Endgründe sowie Fehler und Unterbrechungen ausgewiesen. Queryzahlen und Laufzeiten werden mit Mittelwert, Median, P90 und Maximum beschrieben. Die Zeit bis zur korrekten Lösung und der Aufwand sämtlicher Versuche sind getrennte Verteilungen.

Gepaarte Vergleiche umfassen die Strategien innerhalb desselben Grids und die Gridgrößen innerhalb derselben Strategie. Jeder Vergleich nennt seinen Nenner und zeigt weniger/gleich/mehr Queries sowie die gepaarten Unterschiede. Erfolgsvergleiche verwenden alle 100 Fälle; reine Lösungszeitvergleiche kennzeichnen die gemeinsame korrekt gelöste Teilgruppe. Ungelöste Fälle dürfen diese Gruppe nicht still verbessern.

Lange Endphasen werden gesondert beschrieben: Queries bei unveränderter tatsächlicher Kandidatenzahl, verbleibender erwarteter Fortschritt und gegebenenfalls Countdownneustart. Eine stagnierende tatsächliche Kandidatenzahl wird nicht automatisch als null erwarteter Fortschritt bezeichnet.

Die Quellenbindung, Resultat-/Journalhashes, akzeptierten Antworten und wahren Gewinner werden unabhängig geprüft. Native Audits und JSON-/CSV-Exporte verwenden denselben Auditstand. Anschließend werden Rohdaten, Auswertung und Prüfnachweise versiegelt und auf Bench und Mac mit Hashvergleich gesichert. Dieser Audit behauptet keine erneute geometrische Zertifizierung aller hypothetischen Bewertungen.

## Zeitliche Orientierung

Die frühere reine Neuplanungsstudie hat genau diese vier Gridgrößen auf 100 Problemen gemessen. Ihre primären Controller-Wandzeiten einschließlich Start-/Speicheraufwand betrugen:

| Grid | 100 Neuplanungsläufe |
| --- | --- |
| 3 | 9,54 Minuten |
| 5 | 15,12 Minuten |
| 10 | 28,63 Minuten |
| 20 | 55,04 Minuten |
| Gesamt | 108,32 Minuten |

Quelle ist ausschließlich die Primärgruppe unter `runs/grid-sensitivity-100-single-20261015T145421Z/analysis/verified-campaign-20261015T163826Z-0c9d4b97/`. Zusätzliche alte Timingwiederholungen und unterbrochene Versuche werden nicht für diese Schätzung mitgezählt.

In der späteren frischen 25er-Serie benötigte Countdown je Grid ungefähr 40 bis 47 Prozent und Adaptiv ungefähr 71 bis 76 Prozent der API-Zeit von Neuplanung. Überträgt man diese Verhältnisse auf die vier Gridgrößen und ergänzt den gemessenen Verwaltungsanteil, ergeben sich ungefähr 47 bis 54 Minuten für Countdown und 78 bis 84 Minuten für Adaptiv. Für diese beiden Modi sind Grid 10 und 20 Hochrechnungen, keine Messungen.

Die zentrale Orientierung beträgt damit rund vier Stunden für die 1.200 seriellen Läufe. Als praktischen Zeitansatz einschließlich Auswertung und Sicherung sollten etwa vier bis fünf Stunden reserviert werden; dies ist keine zugesicherte Obergrenze. Implementierung, Funktionsprüfungen und Paketqualifizierung kommen davor hinzu.

Die neue Fortschrittsregel, Countdownneustarts und andere Fälle können die Dauer ändern. Nach den ersten 36 neuen Jobs wird eine aktualisierte Schätzung aus tatsächlichen vollständigen Messungen erstellt. Die hier genannten historischen Zeiten beschreiben nicht die noch ungemessene neue Quelle.

## Abgrenzung und noch nicht gestartete Schritte

Dieser Vorschlag vertieft den gewünschten Strategien-/Gridvergleich. Er ersetzt keine ausführliche Tiefe-3-, Sieben-Ziele-, Konfidenz- oder Thresholdsensitivitätsstudie. Solche Untersuchungen erhalten eigene festgelegte Fragen und Fallgruppen.

Die reguläre Integration ist im Release-10-Kandidaten implementiert; noch offene
Abnahmen und ihre Belege bleiben im fortlaufenden Implementierungsstatus
sichtbar. Die Benchmarkserie folgt erst nach bestandener Abnahme. Vor ihrem
Start und einer Wiederaufnahme werden der Implementierungsplan, dieser
Benchmarkplan und die vorhandenen Arbeitsanweisungen gelesen. Fortschritt,
Fehler und Wiederaufnahmepunkte werden fortlaufend dokumentiert.
