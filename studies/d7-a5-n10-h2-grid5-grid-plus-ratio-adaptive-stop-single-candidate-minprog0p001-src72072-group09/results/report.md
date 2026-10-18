# d7-a5-n10-h2-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072-group09

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
adaptive, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 14.1 | 141 |
| Queries, korrekte Lösungen | 10 | 14.1 | 141 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 14.1 | 141 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 35.4431 | 354.431 |
| API-Sekunden, korrekte Lösungen | 10 | 35.4431 | 354.431 |
| Controller-Sekunden, sämtliche Versuche | 10 | 36.203 | 362.03 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: keine

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d7-m5-c000080 | 5 | 21 | 59.7711 | completed/correct | exact_single_candidate |
| d7-m5-c000081 | 4 | 6 | 5.51537 | completed/correct | exact_single_candidate |
| d7-m5-c000082 | 5 | 21 | 72.868 | completed/correct | exact_single_candidate |
| d7-m5-c000083 | 5 | 10 | 9.90101 | completed/correct | exact_single_candidate |
| d7-m5-c000084 | 5 | 6 | 5.31296 | completed/correct | exact_single_candidate |
| d7-m5-c000085 | 4 | 27 | 83.8215 | completed/correct | exact_single_candidate |
| d7-m5-c000086 | 5 | 5 | 4.67144 | completed/correct | exact_single_candidate |
| d7-m5-c000087 | 5 | 20 | 74.1435 | completed/correct | exact_single_candidate |
| d7-m5-c000088 | 5 | 12 | 19.068 | completed/correct | exact_single_candidate |
| d7-m5-c000089 | 5 | 13 | 19.3579 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `7fa34415d39b943a2f49e48fbbb30bbb888d9862cd4062bd744745fbeffdcc0d`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
