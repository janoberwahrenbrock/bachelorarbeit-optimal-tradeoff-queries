# d5-a5-n10-h3-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072-group09

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
adaptive, H3, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 4.7 | 47 |
| Queries, korrekte Lösungen | 10 | 4.7 | 47 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 4.7 | 47 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 173.489 | 1734.89 |
| API-Sekunden, korrekte Lösungen | 10 | 173.489 | 1734.89 |
| Controller-Sekunden, sämtliche Versuche | 10 | 174.129 | 1741.29 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000084

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000080 | 4 | 4 | 106.321 | completed/correct | exact_single_candidate |
| d5-m5-c000081 | 4 | 4 | 113.94 | completed/correct | exact_single_candidate |
| d5-m5-c000082 | 4 | 6 | 207.171 | completed/correct | exact_single_candidate |
| d5-m5-c000083 | 5 | 5 | 187.339 | completed/correct | exact_single_candidate |
| d5-m5-c000084 | 4 | 12 | 643.454 | completed/correct | exact_single_candidate |
| d5-m5-c000085 | 4 | 2 | 70.3862 | completed/correct | exact_single_candidate |
| d5-m5-c000086 | 3 | 2 | 48.9558 | completed/correct | exact_single_candidate |
| d5-m5-c000087 | 3 | 1 | 31.0344 | completed/correct | exact_single_candidate |
| d5-m5-c000088 | 3 | 8 | 203.17 | completed/correct | exact_single_candidate |
| d5-m5-c000089 | 5 | 3 | 123.116 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `67f04f5ad8236623ad8f326b9f53a31de820e21c2bf30ff4e27d9ac170361c6a`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
