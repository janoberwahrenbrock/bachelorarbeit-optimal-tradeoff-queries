# d7-a5-n10-h2-grid5-grid-plus-ratio-countdown-stop-single-candidate-minprog0p001-src72072-group04

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
countdown, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 20.8 | 208 |
| Queries, korrekte Lösungen | 10 | 20.8 | 208 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 20.8 | 208 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 32.0456 | 320.456 |
| API-Sekunden, korrekte Lösungen | 10 | 32.0456 | 320.456 |
| Controller-Sekunden, sämtliche Versuche | 10 | 32.8113 | 328.113 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d7-m5-c000033

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d7-m5-c000030 | 5 | 48 | 71.7349 | completed/correct | exact_single_candidate |
| d7-m5-c000031 | 4 | 4 | 1.77809 | completed/correct | exact_single_candidate |
| d7-m5-c000032 | 4 | 10 | 5.97494 | completed/correct | exact_single_candidate |
| d7-m5-c000033 | 5 | 76 | 173.209 | completed/correct | exact_single_candidate |
| d7-m5-c000034 | 3 | 8 | 2.97796 | completed/correct | exact_single_candidate |
| d7-m5-c000035 | 4 | 6 | 1.80567 | completed/correct | exact_single_candidate |
| d7-m5-c000036 | 4 | 6 | 2.25456 | completed/correct | exact_single_candidate |
| d7-m5-c000037 | 5 | 6 | 2.27193 | completed/correct | exact_single_candidate |
| d7-m5-c000038 | 5 | 10 | 5.09233 | completed/correct | exact_single_candidate |
| d7-m5-c000039 | 4 | 34 | 53.3564 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `2d5c68ea56a0d5bdf1fdb15f3340347782169ae49b577fd5ffe142234a630b36`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
