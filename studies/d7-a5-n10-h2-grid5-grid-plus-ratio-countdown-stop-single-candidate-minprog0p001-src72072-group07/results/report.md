# d7-a5-n10-h2-grid5-grid-plus-ratio-countdown-stop-single-candidate-minprog0p001-src72072-group07

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
countdown, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 12.2 | 122 |
| Queries, korrekte Lösungen | 10 | 12.2 | 122 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 12.2 | 122 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 8.79632 | 87.9632 |
| API-Sekunden, korrekte Lösungen | 10 | 8.79632 | 87.9632 |
| Controller-Sekunden, sämtliche Versuche | 10 | 9.43566 | 94.3566 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d7-m5-c000062, d7-m5-c000065

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d7-m5-c000060 | 5 | 6 | 2.99746 | completed/correct | exact_single_candidate |
| d7-m5-c000061 | 5 | 6 | 3.85159 | completed/correct | exact_single_candidate |
| d7-m5-c000062 | 5 | 32 | 20.3955 | completed/correct | exact_single_candidate |
| d7-m5-c000063 | 5 | 6 | 3.04948 | completed/correct | exact_single_candidate |
| d7-m5-c000064 | 5 | 6 | 3.68116 | completed/correct | exact_single_candidate |
| d7-m5-c000065 | 5 | 24 | 27.998 | completed/correct | exact_single_candidate |
| d7-m5-c000066 | 5 | 8 | 4.81321 | completed/correct | exact_single_candidate |
| d7-m5-c000067 | 4 | 8 | 2.62479 | completed/correct | exact_single_candidate |
| d7-m5-c000068 | 4 | 14 | 9.70733 | completed/correct | exact_single_candidate |
| d7-m5-c000069 | 5 | 12 | 8.84472 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `026a9712166f66b066f8f6cb0df7bff787f8a581b10dbc4f274815bdb8c61452`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
