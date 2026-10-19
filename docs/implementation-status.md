# Implementierungsstatus

## Aktueller Entwicklungsstand: logarithmische Gridinnenpunkte

Stand: 19. Oktober 2026. Main verwendet den Code der Bachelorarbeit mit dem numerischen Profil
`otqa-exact-v3` mit Gridgrenzen `0.05` bis `20` und logarithmisch gleichmäßig
verteilten Innenpunkten für jede konfigurierte Gridgröße. Leere und gemäß den
bestehenden Toleranzen zusammenfallende Intervalle erzeugen keine Gridqueries.
Die gemeinsame Gridfunktion gilt für `grid` und `both`; Ratioerzeugung und
ausschließliche Ratioverwendung auf der letzten Planungsebene bleiben erhalten.
Formel und Sonderfälle stehen in [Algorithmus](algorithm.md) und
[Numerische Berechnung](numerical_behavior.md).

Die zusätzliche Partitionsrecovery des vorherigen Profils `otqa-exact-v2`
bleibt enthalten. Der neue Gridvertrag verändert die Querymenge und kann
Verläufe und Laufzeiten ändern. Die Quellenbindung der abgeschlossenen Studien
ist im [Studienkatalog](../studies/README.md) festgehalten: gemessener Commit
`62d1d01339f91802e2916b63660a4e640d99c9cc`, Produktionsquellhash
`720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`.
Die 104 Veröffentlichungen enthalten ihre eigenen Ausführungsbedingungen,
wissenschaftlichen Prüfbelege und Ergebnisse. 96 Studien sind den empirischen
Abschnitten der Bachelorarbeit zugeordnet; acht weitere sind Zusatzdaten.
Spätere Zusammenführungscommits verändern die ursprünglichen Messquellen und
Rohdaten nicht. Die unten beschriebenen früheren Implementierungsfreigaben
bleiben auf ihren jeweiligen Quellstand begrenzt.

## Abgenommene Integration 0.2.0 vom 16. Oktober 2026

Stand: 16. Oktober 2026. Countdown mit vollständiger Ersatzplanung,
`min_expected_progress=0.001`, explizite Fortsetzungen und versionierte
Aufzeichnung sind als regulärer Vertrag der Version 0.2.0 implementiert.
Der abgenommene Release-11-Payload bindet das Paket-/Quellinventar
`47c3d8b2f66446e1ba07f4538879ac9a99bdb567f3082bff254564ff2736ca76`.
Er bereitet unveränderliche Schemametadaten einmalig vor, prüft die häufigen
Planobjekte mit vollständigen positiven Strukturbelegen und sammelt binäre
Zahlennachweise mit einem gemeinsamen Akkumulator. Der frühere Nutzdatencache
ist entfernt. Numerische Verfahren und alle 40 Schemaressourcen bleiben erhalten. Ohne Zeitlimit
prüft der Supervisor das terminale Resultat einmal vollständig nach bewiesenem
Prozessgruppenende. Mit Zeitlimit bleibt die zusätzliche frühe Watchdogprüfung
erhalten. Die abschließende Validierung bleibt in beiden Fällen verpflichtend.

| Bereich | Nachgewiesener Stand für die reguläre Integration |
| --- | --- |
| Reine Verträge und unabhängiger Review | Gezielte Quellprüfungen bestanden; keine offenen P1/P2 im unterstützten nativen JSON-Umfang |
| Vollständige Testsuite und CI | [CI 38877314634](https://github.com/janoberwahrenbrock/bachelorarbeit-optimal-tradeoff-queries/actions/runs/38877314634): vier Jobs unter macOS/Linux mit Python 3.13/3.14, jeweils 1.007 Tests, Ruff, Paketbau und externer Wheel-Smoke bestanden |
| Statische Prüfung | Ruff für Quellcode, Tests, Werkzeuge und Buildbackend sauber |
| Installation und Betriebsqualifizierung | Release 11: 34 Mac- und 39 Linux-Kontrollen, öffentliche Fortsetzung und je acht korrekte CLI-Fälle bestanden; zusätzlich drei Mac-Terminalabläufe und externe SDK-Installation geprüft |
| SDK-/CLI-Laufzeitkontrollen und Policyeffekte | SDK: 128 Aufrufe, 60 mathematisch gleiche Vergleichspaare und alle 20 ursprünglichen Laufzeitscreens bestanden. Separate CLI-Nachprüfung: 720 korrekte Aufrufe, 360 mathematisch gleiche Paare, alle zwölf festen Sign-Gates bestanden; acht gezielte Verhaltensprüfungen bestanden |

Die Releases 5, 6 und 7 sind trotz bestandener Funktionskontrollen am vollständigen
nativen Laufzeitgate gesperrt geblieben. Release 7 lieferte 84 korrekte Resultate
und 42 mathematisch gleiche Paare; zehn Bedingungen waren langsamer und zwei
nach der festgelegten Ergänzung unklar. Keine frühere Freigabe wird auf eine
geänderte Quelle übertragen. Verworfene Vorschläge und sämtliche Versuche
bleiben im projektinternen Nachweis erhalten.

Release 10 lieferte 78 korrekte Ergebnisse und 39 mathematisch gleiche Paare.
Elf native Bedingungen bestehen, eine bleibt nach der vorgesehenen Ergänzung
bei einem medianen Zeitquotienten von 1,04785 unklar. Drei isolierte Vorschläge
am Zahlenvergleich verfehlten ihre vorab festgelegten Nutzenhürden und wurden
verworfen. Release 11 enthält ausschließlich den zusätzlich geprüften
Supervisorumbau. Sein ursprünglicher nativer Vergleich ist ohne klare
Regression beendet, bleibt aber nach seiner ursprünglichen Regel insgesamt
unklar.

Die implementierte Max-/Min-Screeningregel enthält einen Prüfdesignfehler:
Sobald Werte auf beiden Seiten der Grenze liegen, kann eine Ergänzung diesen
Zustand nicht mehr auflösen. Alle ursprünglichen Einstufungen bleiben erhalten.
Die neue, getrennte Nachprüfung fixierte ihre vollständige Stichprobe und
Auswertung vor dem ersten neuen Lauf; die Grenze von fünf Prozent blieb
unverändert. Alle zwölf Bedingungen bestehen, mit medianen CLI-Zeitquotienten
zwischen 0,9616 und 1,0317. Alle 721 Controller-/Fallgruppen sind nachweislich
beendet. Die Binomialinterpretation setzt unabhängige Vorzeichen innerhalb
jeder Bedingung voraus; dieser Nachweis auf zwei kleinen analytischen Problemen
ist keine allgemeine Laufzeitgarantie. Die Nachprüfung wertet keine früheren
Messungen um.

Die acht getrennten Verhaltensprüfungen sind absichtlich ungelöste Kontrollen:
sechs enden nach zwei Antworten am Budget, zwei ohne Antwort am
Mindestfortschritt. Alle zwölf Antworten sind unabhängig korrekt geprüft.
Vier Ersatzplanungen wurden über ausdrücklich deklarierte Cursor geprüft;
native Herkunfts- und Fortsetzungsnachweise sind separat qualifiziert. Eine
frühere Kontrollserie blieb an einer falschen exakten Testannahme stehen;
deren Fehler und sieben nicht gestartete Jobs bleiben erhalten. Die Korrektur
betraf ausschließlich den Test der unveränderten binären gewichteten Summe.

Komponentenmessungen beschreiben ausschließlich ihre angegebenen Prüfgrenzen;
sie ersetzen keine vollständigen Laufzeitgates. Die vollständige Entwicklungs-
und Qualifizierungshistorie bleibt projektintern unter
`runs/countdown-progress-integration-20261016T030055Z/` erhalten.

Die Integration wurde auf `main` als
`a5ba67b56d7214153535a3927cc04e76b3f5b274` übernommen. Das tatsächlich
gemessene Wheel wurde aus
`8256508bd711ab9b98a742f3a2741938fcc4d3bd` gebaut; sein Laufquellinventar
ist das oben genannte `47c3d8…`. Spätere Commits werden davon getrennt
ausgewiesen.

## Historische Freigabe 0.1.0

Stand: 15. Oktober 2026. Die Paketidentität
`c75783a7c62d03c5aeb4f9d78ce3eee85a7dfeb4d3d6ac5f6984b1c7b67a1ba1`
bindet den tatsächlich geprüften Algorithmuscode und seine Schemadateien.
Dokumentations- und Laufdatenänderungen verändern diese Identität nicht.

| Bereich | Geprüfter Stand |
| --- | --- |
| Eigenständiges src-Paket und gemeinsame SDK-Solverschleife | 365 native Tests bestanden; Ruff sauber |
| Feste und adaptive Planung | Horizonte eins bis drei, getrennte Stop-/Bewertungsregeln, vollständige H3-Kindoptionen und gewichtete erwartete Querykosten |
| Numerik, Geometrie, Zustände und Queries | Installierte externe Vergleichskontrollen einschließlich dünner, degenerierter und negativer Geometriefälle; Einschränkungen ausdrücklich erfasst |
| Interne Diagnosecapture | Sechs vollständige H3-Aufzeichnungen, einschließlich tatsächlicher Pruning-Gründe und vorhandener Dominanzreferenzen, gegen die Referenz geprüft |
| Dauerhafte Ausführung und Wiederaufnahme | 34 native Betriebskontrollen auf macOS, 39 auf Linux bestanden |
| Interaktive Terminalroute | Je drei zusätzliche reale TTY-Proben auf macOS und Linux bestanden |
| Öffentlicher Benchmarkablauf | Je acht neue Jobs auf beiden Hosts; Audit, JSON-/CSV-Export, Resume und Archivprüfung bestanden |
| Installation und Distribution | Wheel außerhalb des Checkouts installiert, vollständiges Paketinventar geprüft; Sdist-Rebuild erhält alle 105 Paketdateien |
| CI | Vier Jobs unter macOS/Linux mit Python 3.13/3.14 bestanden, einschließlich installiertem mathematischem Smoke-Test |
| Externe Laufzeitabnahme | 35 gepaarte SDK-Prüfreihen und sechs vollständige CLI-Prüfreihen bestanden im festgelegten Vergleichsumfang |

Die vollständigen H3-Capturekontrollen verwenden drei Modi eines Falls mit zwei
Zielen und drei Alternativen sowie drei Modi eines gespeicherten Drei-Ziel-Falls mit
expliziter Anfangshistorie. Weitere Kontrollen prüfen zwei H3-Planungsschritte
mit fünf Zielspalten und einer durch Historie auf eine Dimension eingeschränkten
Geometrie. Das sind vollständige Berechnungen ihrer jeweiligen Kontrollfälle,
keine beliebig großen uneingeschränkten H3-Läufe.

Eine zusätzliche vollständige H3-Kontrolle startet mit drei Zielen, drei
Alternativen und allen drei Kandidaten ohne Anfangshistorie. Feste Tiefe drei
benötigte in beiden Implementierungen 15 Queries, die adaptive Planung bis
Tiefe drei jeweils drei. Alle vier Auswahlen waren korrekt; tatsächliche
Trajektorien und vorhandene Planungsergebnisse stimmten bitweise überein.
Die adaptive Planung betrachtete in jedem Schritt die Horizonte eins, zwei und
drei. Diese vier ungeprofilten Funktionsläufe bilden keine statistische
Laufzeitfreigabe.

Zehn vollständige zusätzliche Vergleichspaare auf gespeicherten neuen Problemen
mit zwei, drei und fünf Zielen ergaben gleiche Trajektorien und korrekte
Auswahlen. Der Fünf-Ziel-Fall mit fünf Alternativen wurde ohne Anfangshistorie
bis zum Singleton gelöst: feste Tiefe zwei benötigte sieben Queries, adaptive
Tiefe zwei sechs. Diese Funktionskontrollen ersetzen keine statistische
Laufzeitmessung.

Der öffentliche CLI-Test erzeugte pro Host vier neue Probleme und acht Jobs mit
acht Workern. Alle Jobs waren korrekt; vier anfangs eindeutige Fälle benötigten
keine Query. Resume erzeugte keinen neuen Versuch. Vier Jobs zeichneten echte
Parent-cProfile-Daten auf. Die strenge Rückprüfung bestätigte Launchketten,
Resultate, Journale, Archive und das Ende sämtlicher Casegruppen. Profilierte
Zeiten gelten als Diagnose.

Die realen Terminalproben prüfen ungültige Eingabe mit gleicher Frage und danach
einer gültigen Antwort, Terminal-EOF und Strg+C. Bei Abbruch blieb die offene
Frage unbeantwortet. Linux prüft darüber hinaus reale Prozessgruppen, unbekannte
Startzustände und die Erhaltung alter Versuche. Diese konkreten Kontrollen
behaupten keine Sicherheit gegen jeden Strom- oder Dateisystemausfall.

Die nativen Eingaben, Profile, Rohdaten und Quittungen liegen projektintern unter
`inputs/` und `runs/`. Historische Quellen und gemischte Alt-Neu-Abnahmebelege
bleiben im getrennten bisherigen Projekt. Unterschiedliche qualifizierte
Python-/NumPy-/SciPyumgebungen können unterschiedliche Queryfolgen erzeugen;
Codevergleiche verwenden deshalb dieselbe tatsächliche Umgebung.

Die externe Laufzeitprüfung auf Bench i7 verwendet auf beiden Seiten acht
Worker, einen nativen Thread und dieselbe tatsächliche Python-/NumPy-/SciPyumgebung.
Alle 35 SDK-Prüfreihen und sechs vollständigen CLI-Prüfreihen bestehen die
abschließende gemeinsame Auswertung. Die gemessenen Zeitverhältnisse liegen
beim SDK zwischen 0,891 und 0,956, bei vollständigen CLI-Aufrufen zwischen
0,937 und 0,971 (neuer geteilt durch bisherigen Stand).

Die erste CLI-Serie enthielt einen statistisch unklaren Fall. Deshalb wurde
vor weiteren Messungen einmalig eine feste Ergänzung für alle sechs Reihen
festgelegt. Sämtliche ursprünglichen Beobachtungen bleiben in den abschließenden
40 Blöcken pro CLI-Reihe enthalten. Die gemeinsame Auswertung verschärft die
Unsicherheitsgrenzen und prüft zusätzlich auffällige Verschiebungen und
Abhängigkeiten; sie bleibt eine näherungsweise statistische Aussage.

Der SDK-Vergleich enthält 3.440 vollständige Aufrufe einschließlich 680
ausdrücklich erhaltener, nicht in den Schätzer eingehender Warmläufe. Die CLI
wurde mit 960 vollständigen Aufrufen geprüft. Ergebnisse, Queryfolgen und
Queryzahlen stimmen in den jeweiligen Vergleichspaaren überein; alle Auswahlen
waren korrekt. Diese Wiederholungen sind keine ebenso große Menge verschiedener
Probleme. Die genauen Eingabe- und H3-Grenzen nennt [Laufzeitprüfung](performance.md).
Es besteht keine allgemeine Laufzeitgarantie für andere Eingaben oder
Konfigurationen. Unklare, fehlende oder langsamere Messungen zählen nicht als
bestanden.

Eine Projektlizenz ist noch nicht festgelegt. Veröffentlichte Studien
sind im [Studienkatalog](../studies/README.md) erfasst.
Weitere Laufdaten werden ausschließlich nach dem
[Veröffentlichungsverfahren](publication.md) ausgewählt und nicht automatisch
auf GitHub geladen.
