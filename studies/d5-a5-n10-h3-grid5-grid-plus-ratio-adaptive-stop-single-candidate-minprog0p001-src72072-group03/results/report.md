# d5-a5-n10-h3-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072-group03

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
adaptive, H3, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 8.5 | 85 |
| Queries, korrekte Lösungen | 10 | 8.5 | 85 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 8.5 | 85 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 330.185 | 3301.85 |
| API-Sekunden, korrekte Lösungen | 10 | 330.185 | 3301.85 |
| Controller-Sekunden, sämtliche Versuche | 10 | 330.907 | 3309.07 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: keine

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000020 | 5 | 12 | 672.628 | completed/correct | exact_single_candidate |
| d5-m5-c000021 | 5 | 11 | 355.042 | completed/correct | exact_single_candidate |
| d5-m5-c000022 | 5 | 8 | 470.628 | completed/correct | exact_single_candidate |
| d5-m5-c000023 | 5 | 4 | 242.54 | completed/correct | exact_single_candidate |
| d5-m5-c000024 | 5 | 11 | 296.466 | completed/correct | exact_single_candidate |
| d5-m5-c000025 | 5 | 19 | 682.264 | completed/correct | exact_single_candidate |
| d5-m5-c000026 | 3 | 7 | 168.39 | completed/correct | exact_single_candidate |
| d5-m5-c000027 | 4 | 5 | 169.925 | completed/correct | exact_single_candidate |
| d5-m5-c000028 | 4 | 4 | 152.339 | completed/correct | exact_single_candidate |
| d5-m5-c000029 | 4 | 4 | 91.6284 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `798d0dd17cf0a8320a6065c2a18c7e5155ac2f8adcc25812e634bc55a485790c`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
