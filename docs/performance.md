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

## Abnahme der Integration 0.2.0

Die Integration wird in zwei getrennten Gruppen geprüft. Ein Alt-Neu-Vergleich
mit ausdrücklich deaktivierter Fortschrittsschwelle misst den Implementierungs-
aufwand bei gleichen vollständigen Rechnungen. Eine zweite Gruppe vergleicht
die neue Quelle mit `None` und `0.001` und beschreibt die fachlich veränderten
Stopps. Zusätzliche volle Countdownersatzplanung ist gewollter Suchaufwand und
wird separat gezählt. Die Hauptstudie mit 100 neuen Fällen × 12 Bedingungen misst
Strategie und Grid bei überall gleicher Schwelle, nicht einen isolierten
Codegeschwindigkeitsgewinn.

Die vorab festgelegte kurze Matrix und drei gepaarten Blöcke stehen im
[Implementierungsplan](implementation-plan-countdown-progress.md). Ein medianer
neuer/alter Zeitquotient über 1.05 wird untersucht; bei unklarem Screening ist
eine einmalige feste Ergänzung für alle betroffenen Bedingungen vorgesehen.
Ein unklarer Befund bleibt unklar. Die historischen Messwerte darüber sind kein
Laufzeitnachweis für den neuen Quellpayload. Tatsächliche neue Nachweise werden
im [Implementierungsstatus](implementation-status.md) ergänzt.

Die Workerimport-Vorbereitung bleibt vollständig innerhalb derselben gemessenen
Solverschleife. Weder globale Forkserverpreloads noch zusätzliche Warmaufrufe,
Wartefristen oder geänderte Workerzahlen werden eingesetzt. Der Initializer lädt
nur die benötigten Module; geometrische Rechnungen und native Handles entstehen
weiterhin bei der ersten tatsächlichen Aufgabe. Ein isolierter Tuningbefund
ersetzt keine erneute Gesamtprüfung des daraus gebauten Pakets.

Die native Release-5-Prüfung erkannte trotz gleicher Rechnungen eine konsistente
Regression aller zwölf CLI-Kontrollen. Profile grenzen den zusätzlichen Aufwand
auf die wiederholte Prüfung umfangreicher Ereignis- und Ergebnisdokumente ein.
Die anschließende Korrektur verwendet einen eindeutigen Schemadiskriminator und
den gemeinsamen strukturellen Journal-Fold. Sie lässt alle gespeicherten
Belege, Schemaressourcen, Persistenzbarrieren und fachlichen Prüfungen bestehen.
CPU-Mikroproben auf gespeicherten Dokumenten sind dabei nur Diagnose; der neue
Payload benötigt einen eigenen Build und frische vollständige Freigabegates.

Release 6 besteht alle installierten Funktionskontrollen auf beiden Hosts. Sein
vollständiges CLIgate bleibt jedoch gesperrt: 78 korrekte Läufe und 39 exakt
übereinstimmende Paare ergeben elf Regressionen und nach der festgelegten
Erweiterung einen weiterhin unklaren Befund. Die Folgekorrektur beschränkt sich
auf die wiederholte Planschemaprüfung innerhalb eines einzigen Aufrufs.
87 reine Prüfungen einschließlich unabhängig ergänzter Fehler- und Kontextfälle
bestanden. Ein CPUvergleich gespeicherter Dokumente zeigt rund 58 Prozent weniger
Resultat- und 33 Prozent weniger Ereignisprüfzeit. Das sind keine vollständigen
CLI-Laufzeitgewinne; Release 7 erhält neue installierte Funktions- und Laufzeitgates.


Release 7 bestand die frischen installierten Funktionskontrollen auf beiden
Hosts, aber noch nicht das vollständige CLIgate. Alle 84 Ergebnisse waren korrekt
und alle 42 Paare mathematisch identisch. Zehn Bedingungen blieben langsamer,
zwei nach der vorgesehenen Ergänzung unklar. Diese Quelle wird daher nicht für
die Hauptstudie freigegeben.

Zwei anschließend isolierte Vorschläge wurden verworfen: Ein größerer, auf eine
Ergebnisprüfung begrenzter Schemacache verfehlte sowohl bei kalten als auch bei
warmen gespeicherten Dokumenten die zuvor festgelegte Nutzenhürde. Ein schnellerer
Metadatenvergleich über Marshal wurde wegen nachgewiesener unerwünschter
Pythoncallbacks nicht in Produktcode überführt. Die verworfenen Varianten und
sämtliche Messungen bleiben im projektinternen Abnahmenachweis erhalten.

Die übernommene Akkumulatoränderung für binäre Zahlennachweise bewahrt Werte,
Reihenfolge und Fehlerverhalten. Auf 104 gespeicherten Payloads benötigte diese
Teilfunktion etwa 38 Prozent weniger CPUzeit; 75 reine Vergleichstests bestanden.
Das ist kein Nachweis für die vollständige CLI-Laufzeit. Ebenso bleiben die
Komponentenmessungen unveränderlich vorbereiteter Schemadaten (vier gespeicherte
Readerfälle, etwa vier bis 16 Prozent weniger CPUzeit) von einer vollständigen
Paket- und Laufzeitabnahme getrennt.


Die neue vorbereitete positive Strukturprüfung wird ausschließlich für vollständig
unterstützte native Schemaabschlüsse verwendet. Ein unbekannter oder negativer
Beleg nimmt den vollständigen ursprünglichen Prüfpfad. Der alte Nutzdatencache
ist dadurch entfernt. Vier gespeicherte warme Readerfälle benötigten in 24
ursprünglichen Messaufrufen rund elf bis 15 Prozent weniger CPUzeit bei gleichen
Ergebnissen. Ein Metadatenfinalisierungsfehler erfasste dabei versehentlich
zwischenzeitlich erzeugte pyc-Dateien; sämtliche ursprünglichen Messungen wurden
aus unveränderten Produkt- und Rohdaten ausgewertet, ohne Wiederholung oder
Fallauswahl. Die Kombination mit unveränderlicher Metadatenvorbereitung und
Akkumulator benötigt weiterhin neue vollständige Paket- und Laufzeitgates.


Die erste installierte Abnahme dieser Kombination erkannte einen Fehler im
Qualifizierungswerkzeug: Die unveränderliche interne Schemaansicht wurde direkt
an die JSON-Metaschemaprüfung übergeben. Der korrigierte Kontrollaufruf erzeugt
eine frische getreue JSON-Ansicht des tatsächlichen kompilierten Schemas und
verwendet dieselbe vollständige Metaschemaprüfung. Alle 40 Ressourcen und vier
absichtlich fehlerhafte Schemas werden durch neue Vertragsfälle geprüft; die
fehlerhaften werden unverändert abgelehnt. Der Paket-/Algorithmuscode wurde
dabei nicht verändert. Die fehlgeschlagene Abnahme bleibt separat erhalten;
der neue Tool-/Buildstand erhält frische installierte Kontrollen.


Release 9 bestand sämtliche installierten Funktionskontrollen und lieferte
84 korrekte Laufzeitergebnisse mit 42 mathematisch identischen Paaren. Zehn
native Bedingungen bestehen, zwei Countdownbedingungen bleiben nach der
vorgesehenen Ergänzung bei medianen Zeitquotienten 1,04566 und 1,05001 unklar.
Es wird weder eine klare Regression noch eine Gesamtfreigabe daraus abgeleitet.
Vier zusätzliche reine kalte Readerprofile lokalisieren verbleibende Kosten im
einmaligen Schemaaufbau; es wurden keine weiteren Solverfälle gestartet.

Zwei daraufhin isolierte Vorschläge erfüllten ihre zuvor festgelegten
Komponentenkriterien. Ein gemeinsamer Compiler für überlappende Definitionen
verringert die CPUzeit zweier gespeicherter kalter Reader um etwa zehn und
12,5 Prozent; ein gemeinsamer Fehlschlag fällt vollständig auf unabhängige
Compiler zurück. Eine redundante tiefe Kopie vor einem bereits vollständig
kopierenden Rewrite entfällt. Die Schemaerzeugung benötigte dadurch rund
58 Prozent weniger CPUzeit; die Reader verbesserten sich um etwa 1,3 und
4,5 Prozent. Alle Rohdaten, vollständigen Ergebnisse und 40 Schemaressourcen
bleiben unverändert. Diese separaten Komponentenbefunde behaupten keine
gemessene kombinierte CLIwirkung; die neue Quelle erhält frische Gates.


Release 10 bestand die installierten Funktionskontrollen auf beiden Hosts und
lieferte 78 korrekte Ergebnisse mit 39 mathematisch gleichen Paaren. Elf native
Bedingungen bestehen; ein kurzer fester Konfidenzfall bleibt nach der vorgesehenen
Ergänzung unklar (medianer CLIquotient 1,04785). Drei anschließend isolierte
Vorschläge am Zahlenbeleg und direkten Vergleich wurden verworfen. Die
Hexwalkeränderung erreichte einen Komponentenquotienten von 0,923 und praktisch
keine Readerverbesserung. Ein direkter Paarvergleich erreichte 0,905, die
geordneten Nichtnullvergleiche 0,566. Beide verfehlten ebenfalls die vorab
festgelegten vollständigen Readerhürden. Kein verworfener Kandidat ist im
Paket enthalten; alle ursprünglichen Daten und Messversuche bleiben erhalten.

Der Release-11-Kandidat beseitigt dagegen eine strukturelle Doppelprüfung:
Ohne externes Zeitlimit steuert die vorzeitige Resultatprüfung im Supervisor
keine Watchdogentscheidung und entfällt. Die vollständige verpflichtende Prüfung
nach bewiesenem Gruppenende bleibt immer erhalten; mit Zeitlimit bleibt auch
die frühe Prüfung erhalten. Elf neue Ablaufkontrollen und vier unabhängige
Kontrollen prüfen diese Grenzen einschließlich fehlerhafter Resultate. Die
Paketqualifizierung bestand auf beiden Hosts. Der ursprüngliche vollständige
CLI-Vergleich lieferte 84 korrekte Resultate und 42 mathematisch gleiche Paare.
Zehn Bedingungen bestehen; zwei bleiben nach der festgelegten Ergänzung unklar.
Aus der Anzahl vermiedener Readeraufrufe wird keine Zeitfreigabe abgeleitet.

Die ursprüngliche Screeningimplementierung fordert zum Bestehen, dass sämtliche
Zeitquotienten höchstens 1,05 sind, und klassifiziert nur dann eine Regression,
wenn sämtliche Quotienten darüber liegen. Ein gekreuzter Befund bleibt daher
unter jeder Ergänzung weiterer Werte zwangsläufig unklar. Das entspricht nicht
dem vorgesehenen Zweck einer zusätzlichen Unsicherheitsprüfung. Die vorhandenen
Pläne, Rohdaten, Werkzeuge und Einstufungen bleiben unverändert erhalten.
Eine gesonderte Nachprüfung wird mit festen neuen Paarzahlen, derselben Grenze
und vollständiger Auswertungsregel vor ihrem ersten Lauf festgelegt. Ihr
statistisches Screening gilt nur unter den dokumentierten Annahmen und für die
untersuchten Kontrollen; es ist keine allgemeine Laufzeitgarantie.

Der neue SDK-Vergleich bestand alle 128 vorgesehenen Aufrufe, die 60
mathematisch identischen Zeitvergleichspaare und sämtliche 20 ursprünglichen
Laufzeitscreens. Die Quotienten der SDK-Zeitmediane liegen zwischen 0,93735 und
1,04098. Von den 128 Kontrollen sind 116 gelöst; zwölf enden ohne Auswahl am
vorher festgelegten Antwortbudget. Diese begrenzten Kontrollen werden nicht als
vollständig gelöste Probleme oder als Nachweis unbegrenzter H3-Laufzeit gezählt.
Alle gespeicherten Antworten und vorhandenen Auswahlen sind unabhängig geprüft.

Die getrennte native Nachprüfung umfasst vorab festgelegte 30 neue Paare je
zwölf Bedingungen, also 720 vollständige CLI-Aufrufe auf zwei analytischen
Problemen. Sie verwendet den einseitigen exakten Binomialschwanz der strikten
Unterschreitungen von `1.05` und die feste Grenze `0.05/12`. Mindestens 23 von
30 Quotienten müssen strikt darunter liegen; Gleichheit zählt nicht als
Unterschreitung. Zusätzlich müssen alle Paare vollständig und mathematisch
identisch sein und die Prozessgruppen nachweislich enden. Es gibt weder
Ausreißerentfernung noch Verlängerung bis zum Bestehen. Die Binomialinterpretation
setzt unabhängige Vorzeichen innerhalb jeder Bedingung voraus. Ausbalancierte
Reihenfolgen und die Korrektur über zwölf Bedingungen beweisen diese Annahme
nicht. Werkzeug, vollständige Reihenfolge und Protokoll wurden vor dem ersten
neuen Aufruf eingefroren. Tatsächlich bestehen alle zwölf Bedingungen mit
29, 29, 26, 23, 29, 30, 29, 30, 30, 30, 30 und 29 strikten Unterschreitungen
von jeweils 30; es gab keine Gleichheiten an der Grenze. Die medianen
CLI-Quotienten liegen zwischen 0,9616 und 1,0317. Alle 720 Resultate sind korrekt,
alle 360 Mathematik-/Journalpaare identisch und alle 721 Controller-/Fallgruppen
beendet. Die feste Stichprobe wurde nicht ergänzt. Der ursprüngliche
84-Aufruf-Befund bleibt unverändert unklar; der separate neue Nachweis besteht
innerhalb seiner oben angegebenen Grenzen.

## Abgeschlossene Strategien-/Gridstudie vom 16. Oktober 2026

Die [veröffentlichte Hauptstudie](../studies/strategy-grid100-progress001-20261016T030055Z/README.md) löste 100 neue
Probleme mit fünf Zielen und fünf Alternativen unter zwölf Bedingungen:
Neuplanung, Countdown und adaptive Verringerung pro erwarteter Query, jeweils
mit maximaler Tiefe zwei, Grid 3/5/10/20 und Mindestfortschritt `0.001`.
Alle 1.200 Zellen sind korrekte Singletonlösungen; jede wurde genau einmal
ausgeführt. Die Daten sind 100 unabhängige Probleme mit gepaarten Bedingungen,
keine 1.200 unabhängigen Qualitätsfälle und keine Timingwiederholungen.

Das gemessene Wheel stammt aus `8256508bd711ab9b98a742f3a2741938fcc4d3bd`;
sein Quellinventar ist
`47c3d8b2f66446e1ba07f4538879ac9a99bdb567f3082bff254564ff2736ca76`.
Der spätere Main-Stand `a5ba67b56d7214153535a3927cc04e76b3f5b274` und
der Veröffentlichungscommit werden getrennt davon dokumentiert.

Die Spanne vom ersten Fallstart bis zum letzten Fallende beträgt 4 Stunden,
8 Minuten und 7 Sekunden. Die etwa 58 Minuten anschließender nativer
Audit-/Export-/Archivarbeit sind gesonderter Abschlussaufwand. Summierte
API-, Fall- und Controllerzeiten haben ineinander liegende Messgrenzen und
werden nicht addiert oder mit dieser seriellen Zeitspanne gleichgesetzt.
Die [vollständigen Ergebnisse](../studies/strategy-grid100-progress001-20261016T030055Z/results/results.json)
weisen jeden einzelnen Lauf und sämtliche gepaarten Vergleiche aus.

Countdown mit Grid 3 hatte die niedrigste mittlere API-Zeit; adaptiv mit
Grid 20 benötigte die wenigsten Queries insgesamt. Diese beobachteten
Rangfolgen sind weder eine allgemeine Laufzeitgarantie noch eine isolierte
Messung eines Implementierungsgeschwindigkeitsgewinns. Die 58 erfolgreichen
Countdownersatzplanungen gehören zum gemessenen Verfahren.
