# d5-a5-n10-h3-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072-group06

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
adaptive, H3, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 7.6 | 76 |
| Queries, korrekte Lösungen | 10 | 7.6 | 76 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 7.6 | 76 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 316.378 | 3163.78 |
| API-Sekunden, korrekte Lösungen | 10 | 316.378 | 3163.78 |
| Controller-Sekunden, sämtliche Versuche | 10 | 317.069 | 3170.69 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000058

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000050 | 5 | 5 | 187.749 | completed/correct | exact_single_candidate |
| d5-m5-c000051 | 5 | 8 | 393.886 | completed/correct | exact_single_candidate |
| d5-m5-c000052 | 4 | 8 | 348.746 | completed/correct | exact_single_candidate |
| d5-m5-c000053 | 5 | 8 | 271.759 | completed/correct | exact_single_candidate |
| d5-m5-c000054 | 5 | 6 | 276.49 | completed/correct | exact_single_candidate |
| d5-m5-c000055 | 5 | 4 | 119.987 | completed/correct | exact_single_candidate |
| d5-m5-c000056 | 3 | 10 | 292.79 | completed/correct | exact_single_candidate |
| d5-m5-c000057 | 4 | 3 | 63.5081 | completed/correct | exact_single_candidate |
| d5-m5-c000058 | 5 | 20 | 1075.46 | completed/correct | exact_single_candidate |
| d5-m5-c000059 | 4 | 4 | 133.412 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `42a051f166b9a01535d0912b7c03dca22d08ad54306bdb2fe9d6441ad1c5356e`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
