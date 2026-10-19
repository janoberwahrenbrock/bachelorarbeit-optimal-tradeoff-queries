# d5-a5-n10-h3-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072-group02

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
adaptive, H3, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 6.1 | 61 |
| Queries, korrekte Lösungen | 10 | 6.1 | 61 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 6.1 | 61 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 223.073 | 2230.73 |
| API-Sekunden, korrekte Lösungen | 10 | 223.073 | 2230.73 |
| Controller-Sekunden, sämtliche Versuche | 10 | 223.701 | 2237.01 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000011, d5-m5-c000014

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000010 | 3 | 2 | 41.8858 | completed/correct | exact_single_candidate |
| d5-m5-c000011 | 5 | 7 | 432.699 | completed/correct | exact_single_candidate |
| d5-m5-c000012 | 4 | 5 | 165.242 | completed/correct | exact_single_candidate |
| d5-m5-c000013 | 3 | 10 | 214.764 | completed/correct | exact_single_candidate |
| d5-m5-c000014 | 5 | 19 | 784.736 | completed/correct | exact_single_candidate |
| d5-m5-c000015 | 5 | 3 | 135.448 | completed/correct | exact_single_candidate |
| d5-m5-c000016 | 3 | 2 | 34.6801 | completed/correct | exact_single_candidate |
| d5-m5-c000017 | 4 | 3 | 85.644 | completed/correct | exact_single_candidate |
| d5-m5-c000018 | 4 | 6 | 177.769 | completed/correct | exact_single_candidate |
| d5-m5-c000019 | 4 | 4 | 157.862 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `0732c8c89184f44fbdf613334a85b57101cef71258d3048546bd8709a4e41a3e`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
