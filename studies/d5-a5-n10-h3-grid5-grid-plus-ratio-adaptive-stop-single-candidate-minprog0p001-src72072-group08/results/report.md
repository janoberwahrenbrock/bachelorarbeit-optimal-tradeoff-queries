# d5-a5-n10-h3-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072-group08

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
adaptive, H3, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 9.7 | 97 |
| Queries, korrekte Lösungen | 10 | 9.7 | 97 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 9.7 | 97 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 379.301 | 3793.01 |
| API-Sekunden, korrekte Lösungen | 10 | 379.301 | 3793.01 |
| Controller-Sekunden, sämtliche Versuche | 10 | 380.039 | 3800.39 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000070

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000070 | 4 | 32 | 1247.72 | completed/correct | exact_single_candidate |
| d5-m5-c000071 | 5 | 13 | 655.29 | completed/correct | exact_single_candidate |
| d5-m5-c000072 | 5 | 5 | 176.487 | completed/correct | exact_single_candidate |
| d5-m5-c000073 | 3 | 4 | 73.7848 | completed/correct | exact_single_candidate |
| d5-m5-c000074 | 3 | 3 | 56.9944 | completed/correct | exact_single_candidate |
| d5-m5-c000075 | 3 | 8 | 151.692 | completed/correct | exact_single_candidate |
| d5-m5-c000076 | 3 | 2 | 34.8105 | completed/correct | exact_single_candidate |
| d5-m5-c000077 | 4 | 4 | 117.431 | completed/correct | exact_single_candidate |
| d5-m5-c000078 | 3 | 22 | 1203.95 | completed/correct | exact_single_candidate |
| d5-m5-c000079 | 3 | 4 | 74.843 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `d39f20f9e6893c5d77f8add58e6a9ee847b3f0d6992089afb2668231375070ca`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
