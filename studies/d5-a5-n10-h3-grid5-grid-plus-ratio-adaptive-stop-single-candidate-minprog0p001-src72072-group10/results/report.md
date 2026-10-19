# d5-a5-n10-h3-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072-group10

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
adaptive, H3, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 10.3 | 103 |
| Queries, korrekte Lösungen | 10 | 10.3 | 103 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 10.3 | 103 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 366.689 | 3666.89 |
| API-Sekunden, korrekte Lösungen | 10 | 366.689 | 3666.89 |
| Controller-Sekunden, sämtliche Versuche | 10 | 367.449 | 3674.49 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000090, d5-m5-c000098

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000090 | 5 | 25 | 795.007 | completed/correct | exact_single_candidate |
| d5-m5-c000091 | 5 | 12 | 326.68 | completed/correct | exact_single_candidate |
| d5-m5-c000092 | 5 | 7 | 363.924 | completed/correct | exact_single_candidate |
| d5-m5-c000093 | 3 | 3 | 54.5589 | completed/correct | exact_single_candidate |
| d5-m5-c000094 | 4 | 12 | 363.099 | completed/correct | exact_single_candidate |
| d5-m5-c000095 | 5 | 4 | 423.924 | completed/correct | exact_single_candidate |
| d5-m5-c000096 | 3 | 4 | 66.7544 | completed/correct | exact_single_candidate |
| d5-m5-c000097 | 4 | 4 | 148.604 | completed/correct | exact_single_candidate |
| d5-m5-c000098 | 4 | 23 | 850.609 | completed/correct | exact_single_candidate |
| d5-m5-c000099 | 4 | 9 | 273.73 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `3a870eeca55f80ba90e4051f226679abf125851bbfe4b4e7d25b7c00a8ec5f52`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
