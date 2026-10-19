# d7-a5-n10-h2-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072-group08

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
adaptive, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 9.8 | 98 |
| Queries, korrekte Lösungen | 10 | 9.8 | 98 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 9.8 | 98 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 15.0453 | 150.453 |
| API-Sekunden, korrekte Lösungen | 10 | 15.0453 | 150.453 |
| Controller-Sekunden, sämtliche Versuche | 10 | 15.7335 | 157.335 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d7-m5-c000070, d7-m5-c000073

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d7-m5-c000070 | 5 | 20 | 50.435 | completed/correct | exact_single_candidate |
| d7-m5-c000071 | 5 | 5 | 6.06145 | completed/correct | exact_single_candidate |
| d7-m5-c000072 | 4 | 9 | 10.2334 | completed/correct | exact_single_candidate |
| d7-m5-c000073 | 5 | 22 | 41.1314 | completed/correct | exact_single_candidate |
| d7-m5-c000074 | 4 | 7 | 5.21309 | completed/correct | exact_single_candidate |
| d7-m5-c000075 | 5 | 7 | 8.3741 | completed/correct | exact_single_candidate |
| d7-m5-c000076 | 5 | 10 | 8.62017 | completed/correct | exact_single_candidate |
| d7-m5-c000077 | 4 | 10 | 11.6694 | completed/correct | exact_single_candidate |
| d7-m5-c000078 | 5 | 4 | 3.76448 | completed/correct | exact_single_candidate |
| d7-m5-c000079 | 5 | 4 | 4.9504 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `2fcdbf1443cec7b711d0cf6c49c70aa5de8a40e095f77c7b71560afa7094e6ee`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
