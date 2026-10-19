# d7-a5-n10-h2-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072-group01

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
adaptive, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 16.2 | 162 |
| Queries, korrekte Lösungen | 10 | 16.2 | 162 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 16.2 | 162 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 50.2368 | 502.368 |
| API-Sekunden, korrekte Lösungen | 10 | 50.2368 | 502.368 |
| Controller-Sekunden, sämtliche Versuche | 10 | 51.0065 | 510.065 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d7-m5-c000001

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d7-m5-c000000 | 5 | 26 | 57.0999 | completed/correct | exact_single_candidate |
| d7-m5-c000001 | 5 | 38 | 253.628 | completed/correct | exact_single_candidate |
| d7-m5-c000002 | 4 | 16 | 19.3746 | completed/correct | exact_single_candidate |
| d7-m5-c000003 | 5 | 14 | 18.359 | completed/correct | exact_single_candidate |
| d7-m5-c000004 | 5 | 8 | 8.32701 | completed/correct | exact_single_candidate |
| d7-m5-c000005 | 5 | 18 | 85.7358 | completed/correct | exact_single_candidate |
| d7-m5-c000006 | 4 | 9 | 7.64811 | completed/correct | exact_single_candidate |
| d7-m5-c000007 | 5 | 12 | 29.8566 | completed/correct | exact_single_candidate |
| d7-m5-c000008 | 5 | 9 | 6.58236 | completed/correct | exact_single_candidate |
| d7-m5-c000009 | 4 | 12 | 15.7563 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `c7b298a42384f7af365157e562533d1af3fabf19073060e5cefcda5cf486c3b3`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
