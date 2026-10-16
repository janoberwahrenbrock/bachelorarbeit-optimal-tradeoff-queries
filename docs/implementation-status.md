# Implementierungsstatus

## Aktuelle Integration 0.2.0

Stand: 16. Oktober 2026. Countdown mit vollständiger Ersatzplanung,
`min_expected_progress=0.001`, explizite Fortsetzungen und versionierte
Aufzeichnung sind auf `codex/countdown-progress-integration` implementiert.
Der bisher gebaute und funktional geprüfte Abnahmekandidat ist Release 4 von Version `0.2.0`:

- Implementierungscommit: `289fbe35929f58ce9257213a5956ba42142ac0ce`;
- Paket-/Quellinventar: `b9f796c8f0150f4621749b2118f84349b89347293c198c60cd5e1a92ea8904ef`;
- Wheel-SHA256: `95f3c74553fafb2abd8d16c10ecdde73c5a8c1ce39de97b7da3b84572f82f29a`.

Die [Releasebindung](../runs/countdown-progress-integration-20261016T030055Z/release4.json)
und der [fortlaufende Abnahmestand](../runs/countdown-progress-integration-20261016T030055Z/implementation-state.json)
halten den geprüften Payload und die noch offenen Schritte fest. Änderungen
an Produktcode oder Paketressourcen erfordern erneut passende Prüfungen.

| Bereich | Nachgewiesener Stand für die Integration |
| --- | --- |
| Vollständige Testsuite | 551 Tests bestanden in 32,55 Sekunden; [Testlog](../runs/countdown-progress-integration-20261016T030055Z/pytest-release4.log) |
| Statische Prüfung | Ruff sauber |
| Unabhängiger Review | Konkreter Fulltrace-Befund korrigiert; keine weiteren belastbaren P1/P2 im beschriebenen Prüfumfang; [Reviewbeleg](../runs/countdown-progress-integration-20261016T030055Z/review-independent.md) |
| Frische Wheelinstallation außerhalb des Checkouts | Analytische SDK-Kontrollen bestanden, einschließlich adaptiver Tiefe 3 mit Stop-aware-Bewertung; [Quellbindung und Ergebnis](../runs/countdown-progress-integration-20261016T030055Z/external-installed-smoke-release4.json) |
| Native Betriebsqualifizierung des Release-4-Payloads | 34 Kontrollen auf macOS und 39 auf Linux bestanden; [macOS-Zertifikat](../runs/countdown-progress-integration-20261016T030055Z/macos-qualification-release4/certification.json), hostübergreifende Belegzuordnung im fortlaufenden Abnahmestand |
| Öffentliche native Fortsetzung und Benchmarkbedienung | CLI-Fortsetzung auf beiden Hosts bestanden; je acht native Jobs auf Mac und Bench korrekt, einschließlich Audit/Export/Resume/Seal; frühere Release-Ergebnisse werden nicht übertragen |
| Gepaarte Laufzeit- und Qualitätskontrollen | Noch offen; deaktivierte Schwelle für Implementierungsaufwand und `None` gegen `0.001` für verändertes Abbruchverhalten getrennt prüfen |
| Größere Strategien-/Gridstudie | Noch nicht gestartet; 100 neue Probleme × zwölf Bedingungen erst nach bestandenen Freigabegates |

Die frühen Abnahmekandidaten deckten drei konkrete Wirefehler auf: eine
unveränderte Bootstrapregistrierung erhielt fälschlich Version zwei; ein
Fulltrace-Planungszyklus ließ die bereits bekannte Rootkandidatenzahl aus;
interne Singletonbezeichner wurden nicht in den bestehenden nativen
Baumbezeichner übersetzt. Die Korrekturen und Regressionstests sind im
Release-4-Payload enthalten. Frühere Fehlversuche und Nachweise bleiben unter
`runs/countdown-progress-integration-20261016T030055Z/` erhalten. Eine bestandene
Betriebsqualifizierung ist noch keine Freigabe der Laufzeit oder der großen Studie.

Die anschließende Workerimport-Korrektur wird als eigener Release-5-Payload
neu gebaut und qualifiziert. Die vollständige Suite bestand dafür 554 Tests
in 33,23 Sekunden; 118 fokussierte Tests und Ruff sind ebenfalls bestanden.
Ihre benötigten Module werden im eigenen
Workerinitializer geladen; numerische Handles bleiben first-task-lazy. Der
Release-4-Laufzeitbefund und die isolierte Tuninggruppe bleiben separat erhalten.
Die endgültige Quellenbindung und Gesamtmessung stehen im fortlaufenden
Abnahmenachweis, bis die erneuten Gates abgeschlossen sind.

Die folgenden historischen Freigaben gelten ausschließlich für ihre ursprüngliche
Quelle und werden nicht auf den aktuellen Quellpayload übertragen.

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
