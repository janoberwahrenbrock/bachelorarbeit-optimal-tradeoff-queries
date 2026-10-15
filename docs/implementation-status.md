# Implementierungsstatus

Stand: 15. Oktober 2026. Die Paketidentität
`c75783a7c62d03c5aeb4f9d78ce3eee85a7dfeb4d3d6ac5f6984b1c7b67a1ba1`
bindet den tatsächlich geprüften Algorithmuscode und seine Schemadateien.
Dokumentations- und Laufdatenänderungen verändern diese Identität nicht.

| Bereich | Geprüfter Stand |
| --- | --- |
| Eigenständiges src-Paket und gemeinsame SDK-Solverschleife | 361 native Tests bestanden; Ruff sauber |
| Feste und adaptive Planung | Horizonte eins bis drei, getrennte Stop-/Bewertungsregeln, vollständige H3-Kindoptionen und gewichtete erwartete Querykosten |
| Numerik, Geometrie, Zustände und Queries | Installierte externe Vergleichskontrollen einschließlich dünner, degenerierter und negativer Geometriefälle; Einschränkungen ausdrücklich erfasst |
| Interne Diagnosecapture | Sechs vollständige H3-Aufzeichnungen, einschließlich tatsächlicher Pruning-Gründe und vorhandener Dominanzreferenzen, gegen die Referenz geprüft |
| Dauerhafte Ausführung und Wiederaufnahme | 34 native Betriebskontrollen auf macOS, 39 auf Linux bestanden |
| Interaktive Terminalroute | Je drei zusätzliche reale TTY-Proben auf macOS und Linux bestanden |
| Öffentlicher Benchmarkablauf | Je acht neue Jobs auf beiden Hosts; Audit, JSON-/CSV-Export, Resume und Archivprüfung bestanden |
| Installation und Distribution | Wheel außerhalb des Checkouts installiert, vollständiges Paketinventar geprüft; Sdist-Rebuild erhält alle 105 Paketdateien |
| CI | Vier Jobs unter macOS/Linux mit Python 3.13/3.14 bestanden, einschließlich installiertem mathematischem Smoke-Test |
| Externe Laufzeitabnahme | 35 gepaarte SDK-Prüfreihen und sechs vollständige CLI-Prüfreihen werden separat abgenommen; noch offen |

Die vollständigen H3-Capturekontrollen verwenden drei Modi eines Falls mit zwei
Zielen und drei Alternativen sowie drei Modi eines gespeicherten Drei-Ziel-Falls mit
expliziter Anfangshistorie. Weitere Kontrollen prüfen zwei H3-Planungsschritte
mit fünf Zielspalten und einer durch Historie auf eine Dimension eingeschränkten
Geometrie. Das sind vollständige Berechnungen ihrer jeweiligen Kontrollfälle,
keine beliebig großen uneingeschränkten H3-Läufe.

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

Eine vollständige externe Laufzeitfreigabe benötigt die bestandenen gepaarten
Prüfreihen im ausdrücklich gemessenen Umfang. Unklare, fehlende oder langsamere
Messungen zählen nicht als bestanden. Es besteht keine allgemeine
Laufzeitgarantie für andere Eingaben oder Konfigurationen.

Eine Projektlizenz und die Git-Veröffentlichung tatsächlicher Laufarchive sind
noch nicht festgelegt. Laufdaten werden nicht automatisch auf GitHub geladen.
