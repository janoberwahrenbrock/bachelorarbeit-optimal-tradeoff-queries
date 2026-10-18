# d5-a5-n10-h3-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072-group05

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
adaptive, H3, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 9.5 | 95 |
| Queries, korrekte Lösungen | 10 | 9.5 | 95 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 9.5 | 95 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 379.217 | 3792.17 |
| API-Sekunden, korrekte Lösungen | 10 | 379.217 | 3792.17 |
| Controller-Sekunden, sämtliche Versuche | 10 | 379.961 | 3799.61 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000046

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000040 | 4 | 10 | 280.43 | completed/correct | exact_single_candidate |
| d5-m5-c000041 | 4 | 3 | 82.1889 | completed/correct | exact_single_candidate |
| d5-m5-c000042 | 5 | 4 | 130.55 | completed/correct | exact_single_candidate |
| d5-m5-c000043 | 5 | 4 | 119.611 | completed/correct | exact_single_candidate |
| d5-m5-c000044 | 4 | 7 | 196.94 | completed/correct | exact_single_candidate |
| d5-m5-c000045 | 4 | 2 | 51.0061 | completed/correct | exact_single_candidate |
| d5-m5-c000046 | 4 | 40 | 2022.17 | completed/correct | exact_single_candidate |
| d5-m5-c000047 | 4 | 6 | 252.531 | completed/correct | exact_single_candidate |
| d5-m5-c000048 | 5 | 9 | 385.64 | completed/correct | exact_single_candidate |
| d5-m5-c000049 | 3 | 10 | 271.104 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `66b4569ad609271e70a2fbb2c24a91f24a1a546a588010e12dd67bf1263bd87c`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
