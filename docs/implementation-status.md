# Implementierungsstatus

Stand der integrierten Implementierung am 15. Oktober 2026. Die mathematische
Paketidentität wird unabhängig vom Gitstand durch das tatsächliche
Paketdateiinventar gebunden. Ein bestandener Betriebscheck ist keine allgemeine
Geschwindigkeitsfreigabe.

| Bereich | Tatsächlich geprüfter Stand |
|---|---|
| Eigenständiges src-Paket, Modelle und gemeinsame SDK-Solverschleife | Implementiert; 336 native Tests bestanden, Ruff sauber |
| Feste und adaptive Planung bis Tiefe drei | Implementiert; analytische Tests, vollständige kleine Vergleichsläufe und interne Captureprüfungen |
| Numerik, Geometrie, Zustände und Queries | Implementiert; externe installierte Vergleichskontrollen einschließlich negativer und dünner Geometrien |
| Dauerhafte Standaloneläufe, Serien und Wiederaufnahme | Implementiert; Mac- und Linux-Betriebsqualifizierung bestanden |
| Audit, JSON-/CSV-Export und portable Archive | Implementiert; vollständiger öffentlicher CLI-Ablauf auf beiden Hosts geprüft |
| Installation und Distribution | Wheel außerhalb des Checkouts installiert; tatsächliche Paketbytes geprüft; Sdist-Rebuild erhält alle Paketbytes |
| CI | macOS/Linux mit Python 3.13/3.14 bestanden, einschließlich mathematischem Smoke-Test des außerhalb des Checkouts installierten Wheels |
| Vollständige externe Laufzeitabnahme | Noch offen; ungeprofilte gepaarte Messungen werden separat durchgeführt |

Die aktuelle native Betriebsqualifizierung umfasst 34 bestandene Einzelkontrollen
auf macOS und 39 auf Linux. Linux prüft zusätzlich reale Prozessgruppen,
Startfreigabe, unbekannte Zustände und die Erhaltung alter Versuche. Das sind
begrenzte tatsächliche Kontrollen, kein pauschaler Nachweis gegen jeden Strom-
oder Dateisystemausfall.

Der neue funktionelle CLI-Test erzeugte pro Host vier neue Probleme und acht Jobs
mit acht Workern. Alle acht Jobs waren korrekt; der erneute Resume-Aufruf legte
keinen Versuch an. Vier Jobs zeichneten echte Parent-cProfile-Daten auf. Audit,
beide Exportformate und die anschließende Offline-Archivprüfung bestanden.
Profilierte Zeiten sind keine Performanceabnahme.

Ein weiterer frischer Pilot mit fünf Zielen und fünf Alternativen wurde bis zum
Singleton gelöst: feste Tiefe zwei benötigte sieben Queries bei rund acht Sekunden
APIzeit, adaptive Tiefe zwei sechs Queries bei rund vier Sekunden. Bei sieben
Zielen erreichten beide Varianten das ausdrücklich gesetzte Testlimit von 60
Sekunden ohne Lösung. Ihre 18 beziehungsweise 22 bestätigten Antworten und alle
Teilresultate bleiben erhalten. Das sind einzelne Funktionsbeobachtungen auf dem
Mac, keine kontrollierte Geschwindigkeitsfreigabe oder typische Laufzeitverteilung.

Die vollständigen nativen Rohdaten, Qualifikationsprofile und Quittungen liegen
lokal unter `runs/`. Unterschiedliche Python-/Numerikversionen auf verschiedenen
Hosts werden nicht als direkter Performance- oder Paritätsvergleich verwendet.
Externe Alt-Neu-Abnahmebelege bleiben im getrennten bisherigen Projekt.

Eine Veröffentlichung als vollständig abgenommene V1 setzt zusätzlich bestandene
externe Mathematik- und Laufzeitgates im jeweils ausdrücklich gemessenen Umfang
voraus. Unklare oder langsamere Messergebnisse werden nicht als bestanden gezählt.
Die Auswahl einer Projektlizenz und die Git-Veröffentlichung tatsächlicher
Laufarchive sind separate Entscheidungen; bisher wurde keine Lizenz erfunden und
keine automatische Rohdatenveröffentlichung eingerichtet.

Eine zusätzliche Fehlerprüfung stellte die ursprüngliche Fehlerursache an drei
Grenzen der begrenzten rationalen Wahrscheinlichkeitsreparatur wieder her.
Elf neue analytische Tests prüfen nicht unterstützte Räume, erhaltene Ursachen,
erfolgreiche Reparaturen und unveränderte normale Volumenpfade. Dieser neue
Quellstand benötigt erneut seine eigenen Installations- und Vergleichsbelege;
Messungen eines früheren Wheels werden ihm nicht automatisch zugeschrieben.
