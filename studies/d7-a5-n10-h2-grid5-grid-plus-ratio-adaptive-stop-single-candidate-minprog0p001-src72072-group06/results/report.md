# d7-a5-n10-h2-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072-group06

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
adaptive, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 9/10; regulär ungelöst: 1/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 14.2 | 142 |
| Queries, korrekte Lösungen | 9 | 15.5556 | 140 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 14.2 | 142 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 32.0111 | 320.111 |
| API-Sekunden, korrekte Lösungen | 9 | 35.3333 | 317.999 |
| Controller-Sekunden, sämtliche Versuche | 10 | 32.789 | 327.89 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d7-m5-c000057

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d7-m5-c000050 | 5 | 9 | 10.1362 | completed/correct | exact_single_candidate |
| d7-m5-c000051 | 5 | 6 | 6.7508 | completed/correct | exact_single_candidate |
| d7-m5-c000052 | 5 | 4 | 3.10582 | completed/correct | exact_single_candidate |
| d7-m5-c000053 | 5 | 13 | 25.3988 | completed/correct | exact_single_candidate |
| d7-m5-c000054 | 4 | 14 | 26.7649 | completed/correct | exact_single_candidate |
| d7-m5-c000055 | 5 | 18 | 42.8912 | completed/correct | exact_single_candidate |
| d7-m5-c000056 | 4 | 2 | 2.11139 | completed/regular_unsolved | insufficient_expected_progress |
| d7-m5-c000057 | 5 | 48 | 159.927 | completed/correct | exact_single_candidate |
| d7-m5-c000058 | 5 | 14 | 23.476 | completed/correct | exact_single_candidate |
| d7-m5-c000059 | 5 | 14 | 19.5486 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `faa535dc0a6d8411084419cb8a9f58087896d7d3e6fe607fd62a881449dee6a0`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
