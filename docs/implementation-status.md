# Implementierungsstatus

## Aktuelle Integration 0.2.0

Stand: 16. Oktober 2026. Countdown mit vollständiger Ersatzplanung,
`min_expected_progress=0.001`, explizite Fortsetzungen und versionierte
Aufzeichnung sind auf `codex/countdown-progress-integration` implementiert.
Der neue Release-11-Kandidat bindet das Paket-/Quellinventar
`47c3d8b2f66446e1ba07f4538879ac9a99bdb567f3082bff254564ff2736ca76`.
Er bereitet unveränderliche Schemametadaten einmalig vor, prüft die häufigen
Planobjekte mit vollständigen positiven Strukturbelegen und sammelt binäre
Zahlennachweise mit einem gemeinsamen Akkumulator. Der frühere Nutzdatencache
ist entfernt. Numerische Verfahren und alle 40 Schemaressourcen bleiben erhalten. Ohne Zeitlimit
prüft der Supervisor das terminale Resultat einmal vollständig nach bewiesenem
Prozessgruppenende. Mit Zeitlimit bleibt die zusätzliche frühe Watchdogprüfung
erhalten. Die abschließende Validierung bleibt in beiden Fällen verpflichtend.

| Bereich | Nachgewiesener Stand für den aktuellen Kandidaten |
| --- | --- |
| Reine Verträge und unabhängiger Review | Gezielte Quellprüfungen bestanden; keine offenen P1/P2 im unterstützten nativen JSON-Umfang |
| Vollständige Testsuite | 942 Tests in 43.52 Sekunden im tatsächlichen Hauptcheckout |
| Statische Prüfung | Ruff für Quellcode, Tests, Werkzeuge und Buildbackend sauber |
| Installation und Betriebsqualifizierung | Frischer Build und Mac-/Linux-Prüfungen für Release 11 erforderlich |
| SDK-/CLI-Laufzeitkontrollen und Policyeffekte | Neue vollständige Prüfungen erforderlich |
| Größere Strategien-/Gridstudie | Noch nicht gestartet; 100 neue Probleme × zwölf Bedingungen erst nach bestandenen Freigabegates |

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
Supervisorumbau; dessen Laufzeitwirkung ist noch nicht freigegeben.

Komponentenmessungen beschreiben ausschließlich ihre angegebenen Prüfgrenzen;
sie ersetzen keine vollständigen Laufzeitgates. Der
[fortlaufende Abnahmestand](../runs/countdown-progress-integration-20261016T030055Z/implementation-state.json)
bindet Quellen, Rohdaten, Fehler und nächste Schritte.

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

Eine Projektlizenz und die Git-Veröffentlichung tatsächlicher Laufarchive sind
noch nicht festgelegt. Laufdaten werden nicht automatisch auf GitHub geladen.
