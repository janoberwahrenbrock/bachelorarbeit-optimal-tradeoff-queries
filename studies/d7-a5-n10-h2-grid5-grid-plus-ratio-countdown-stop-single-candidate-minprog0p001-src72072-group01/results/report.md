# d7-a5-n10-h2-grid5-grid-plus-ratio-countdown-stop-single-candidate-minprog0p001-src72072-group01

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
countdown, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 19.5 | 195 |
| Queries, korrekte Lösungen | 10 | 19.5 | 195 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 19.5 | 195 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 29.9618 | 299.618 |
| API-Sekunden, korrekte Lösungen | 10 | 29.9618 | 299.618 |
| Controller-Sekunden, sämtliche Versuche | 10 | 30.7062 | 307.062 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d7-m5-c000000, d7-m5-c000001

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d7-m5-c000000 | 5 | 51 | 86.85 | completed/correct | exact_single_candidate |
| d7-m5-c000001 | 5 | 44 | 122.263 | completed/correct | exact_single_candidate |
| d7-m5-c000002 | 4 | 20 | 21.991 | completed/correct | exact_single_candidate |
| d7-m5-c000003 | 5 | 16 | 15.1133 | completed/correct | exact_single_candidate |
| d7-m5-c000004 | 5 | 8 | 3.34458 | completed/correct | exact_single_candidate |
| d7-m5-c000005 | 5 | 17 | 28.5202 | completed/correct | exact_single_candidate |
| d7-m5-c000006 | 4 | 10 | 5.03525 | completed/correct | exact_single_candidate |
| d7-m5-c000007 | 5 | 10 | 6.35541 | completed/correct | exact_single_candidate |
| d7-m5-c000008 | 5 | 7 | 3.17915 | completed/correct | exact_single_candidate |
| d7-m5-c000009 | 4 | 12 | 6.96614 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `c7b298a42384f7af365157e562533d1af3fabf19073060e5cefcda5cf486c3b3`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
