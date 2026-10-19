# d5-a5-n10-h3-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072-group04

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
adaptive, H3, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 8.5 | 85 |
| Queries, korrekte Lösungen | 10 | 8.5 | 85 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 8.5 | 85 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 317.214 | 3172.14 |
| API-Sekunden, korrekte Lösungen | 10 | 317.214 | 3172.14 |
| Controller-Sekunden, sämtliche Versuche | 10 | 317.931 | 3179.31 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000036

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000030 | 4 | 3 | 80.2997 | completed/correct | exact_single_candidate |
| d5-m5-c000031 | 4 | 5 | 138.911 | completed/correct | exact_single_candidate |
| d5-m5-c000032 | 4 | 2 | 65.7642 | completed/correct | exact_single_candidate |
| d5-m5-c000033 | 3 | 2 | 40.5258 | completed/correct | exact_single_candidate |
| d5-m5-c000034 | 5 | 9 | 368.979 | completed/correct | exact_single_candidate |
| d5-m5-c000035 | 4 | 6 | 138.936 | completed/correct | exact_single_candidate |
| d5-m5-c000036 | 5 | 30 | 1341.34 | completed/correct | exact_single_candidate |
| d5-m5-c000037 | 4 | 10 | 253.867 | completed/correct | exact_single_candidate |
| d5-m5-c000038 | 3 | 6 | 244.133 | completed/correct | exact_single_candidate |
| d5-m5-c000039 | 5 | 12 | 499.383 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `e4fcf5eb4a937e80689256cfe02e909bcd62b0298670d5afeb80a5a7729105eb`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
