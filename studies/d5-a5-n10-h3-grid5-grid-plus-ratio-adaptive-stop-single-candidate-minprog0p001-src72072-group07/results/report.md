# d5-a5-n10-h3-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072-group07

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
adaptive, H3, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 7.5 | 75 |
| Queries, korrekte Lösungen | 10 | 7.5 | 75 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 7.5 | 75 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 222.417 | 2224.17 |
| API-Sekunden, korrekte Lösungen | 10 | 222.417 | 2224.17 |
| Controller-Sekunden, sämtliche Versuche | 10 | 223.108 | 2231.08 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000060, d5-m5-c000067

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000060 | 5 | 12 | 468.801 | completed/correct | exact_single_candidate |
| d5-m5-c000061 | 5 | 6 | 238.294 | completed/correct | exact_single_candidate |
| d5-m5-c000062 | 4 | 5 | 135.39 | completed/correct | exact_single_candidate |
| d5-m5-c000063 | 4 | 3 | 73.2655 | completed/correct | exact_single_candidate |
| d5-m5-c000064 | 3 | 6 | 113.776 | completed/correct | exact_single_candidate |
| d5-m5-c000065 | 3 | 7 | 161.382 | completed/correct | exact_single_candidate |
| d5-m5-c000066 | 5 | 4 | 147.215 | completed/correct | exact_single_candidate |
| d5-m5-c000067 | 3 | 24 | 636.726 | completed/correct | exact_single_candidate |
| d5-m5-c000068 | 4 | 4 | 172.892 | completed/correct | exact_single_candidate |
| d5-m5-c000069 | 3 | 4 | 76.4248 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `c71b358f96ff959066c585813ede14faea3b6db114b4f7eda1a07ac875d52f31`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
