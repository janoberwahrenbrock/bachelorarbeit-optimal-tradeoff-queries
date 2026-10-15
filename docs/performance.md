# Laufzeitprüfung

Eine Formatprüfung oder korrekte Endauswahl beweist keine unveränderte Laufzeit. Performanceabnahme braucht gespeicherte Fälle, deklarierte Konfiguration, tatsächliche Quellen-/Environmentbindung und passende Rohmessungen.

Die vollständige SDKzeit enthält Solverinitialisierung, benötigte Worker, Provider- und Callbackzeit, Bereinigung und normalen Return. Das vollständige äußere CLIgate enthält zusätzlich Vorbereitung, Prozessstart, erforderliche Terminalpersistenz und Cleanup. Native Teilzeiten besitzen eigene Grenzen und ersetzen die vollständige Zeit nicht.

Vergleichspaare verwenden gleiche Matrix, Antworten beziehungsweise Oracle, fachliche Parameter, Budget, Worker-/Threadzahl und Aufzeichnungsleistung. Kalte Prozesse, warme sequentielle SDK-Aufrufe und erster Import sind getrennte Messscopes. Profilierung und vollständige Diagnosecapture bleiben bei ungeprofilten Gates deaktiviert.

Ein Vergleich zweier Implementierungen verwendet außerdem denselben Host und dieselbe tatsächliche Python-/NumPy-/SciPyumgebung, gebunden durch den vollständigen Vergleichslock. Ein gemeinsamer Profilname oder zwei bestandene native Qualifizierungen ersetzen diese Gleichheit nicht. Versions- und Plattformunterschiede können die Queryauswahl und damit die tatsächliche Zahl gestellter Fragen beeinflussen. Mac- und Linux-Ergebnisse werden deshalb innerhalb ihrer jeweiligen Umgebung ausgewertet; ihre unterschiedlichen Queryzahlen und Laufzeiten sind kein isolierter Codevergleich.

Der Messplan legt vorab Reihenfolge, Wiederholungen, Konfigurationsumfang, Budgets und Auswertung fest. Fehlgeschlagene, unterbrochene und ungelöste Läufe bleiben sichtbar. Eine Teilplanung liefert keine vollständige Problemlösungszeit. Bestätigte Regressionen werden untersucht; ein statistisch unklarer Unterschied wird nicht als Geschwindigkeitsfreigabe ausgegeben.

Native Betriebsqualifizierung prüft die tatsächlich ausgeführte Installation, numerische Konformität und Lifecycle-/Persistenzgrenzen. Daraus folgt keine allgemeine Performancefreigabe für andere Modi oder Umgebungen.

## Geprüfter Stand vom 15. Oktober 2026

Die erste eigenständige Implementierung wurde auf Bench i7 gegen den bisherigen
optimierten Algorithmus verglichen. Beide Seiten verwenden acht Worker, einen
nativen Thread und dieselbe tatsächlich installierte Umgebung. Das geprüfte
Paketinventar ist im [Implementierungsstatus](implementation-status.md) gebunden.

| Messbereich | Prüfreihen | Zeitverhältnis neuer / bisheriger Stand |
| --- | ---: | ---: |
| Vollständiger SDK, kalte und warme Aufrufe sowie erster Import mit Aufruf | 35 | 0,891–0,956 |
| Vollständiger dauerhafter CLI-Aufruf | 6 | 0,937–0,971 |

Alle Reihen bestehen die abschließende gemeinsame Prüfung gegen eine
Laufzeitverschlechterung. Die Werte sind geometrische gepaarte Schätzungen,
keine garantierten Beschleunigungen für beliebige Probleme. Mathematische
Ergebnisse und tatsächliche Queryzahlen stimmen zwischen den Implementierungen
überein. Die CLI-Referenz ist der bisherige Solver mit einem externen dauerhaften
Vergleichsrunner; die neue Seite verwendet die unveränderte öffentliche CLI.
Aufzeichnung, Messgrenzen und nachgewiesene Prozessbereinigung sind gleichwertig.

Die SDK-Reihen umfassen feste und adaptive Horizonte, getrennte Stop- und
Planungsbewertungen, 95-/99-Prozent-Regeln und Budgetkontrollen mit Grid5 plus
Ratios. H1/H2 verwenden einen gespeicherten Fall mit drei Zielen und drei
Alternativen ohne Anfangshistorie. Die H3-Laufzeitreihen verwenden eine
gespeicherte Drei-Ziel-Fortsetzung, deren Geometrie durch explizite Antworten
auf eine affine Dimension eingeschränkt ist. Vollständige zusätzliche
Drei-Ziel-H3- und Fünf-Ziel-H2-Funktionskontrollen sind getrennt dokumentiert;
sie stellen keine allgemeine hochdimensionale Laufzeitfreigabe dar.

Nach einem statistisch unklaren ursprünglichen CLI-Ergebnis wurde genau eine
feste Ergänzung von 30 ABBA-Blöcken für jede der sechs Reihen festgelegt.
Ursprüngliche zehn und zusätzliche 30 Blöcke wurden vollständig zusammengeführt;
es wurden keine Ausreißer entfernt. Die abschließende Auswertung verwendet
400.000 Bootstrapwiederholungen ganzer Blöcke, eine strengere gemeinsame
Berücksichtigung der beiden Auswertungszeitpunkte sowie vorab festgelegte
Verschiebungs- und Abhängigkeitskontrollen mit zusätzlichem unabhängigem Review.
Die oberen Intervallgrenzen liegen für alle Reihen unter eins. Die
Bootstrapaussage bleibt unter plausiblen Blockannahmen näherungsweise; ein
unauffälliger Kontrollbefund beweist keine Stationarität oder Unabhängigkeit.

Historische Quellen und gemischte Vergleichsnachweise werden getrennt vom neuen
Produktrepository aufbewahrt. Neue native Eingaben und Laufdaten bleiben
projektintern unter `inputs/` und `runs/`. Für die Bachelorarbeit werden weitere
Datensätze über den [Benchmarkworkflow](benchmarks.md) erzeugt und sämtliche
gelösten, ungelösten, fehlerhaften und unterbrochenen Fälle gemeinsam ausgewiesen.
