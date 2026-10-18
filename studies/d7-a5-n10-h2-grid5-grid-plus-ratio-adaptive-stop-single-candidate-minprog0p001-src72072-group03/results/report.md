# d7-a5-n10-h2-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072-group03

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
adaptive, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 16 | 160 |
| Queries, korrekte Lösungen | 10 | 16 | 160 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 16 | 160 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 43.536 | 435.36 |
| API-Sekunden, korrekte Lösungen | 10 | 43.536 | 435.36 |
| Controller-Sekunden, sämtliche Versuche | 10 | 44.3411 | 443.411 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d7-m5-c000029

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d7-m5-c000020 | 5 | 16 | 38.1667 | completed/correct | exact_single_candidate |
| d7-m5-c000021 | 5 | 9 | 10.6312 | completed/correct | exact_single_candidate |
| d7-m5-c000022 | 4 | 13 | 18.3235 | completed/correct | exact_single_candidate |
| d7-m5-c000023 | 5 | 9 | 9.07129 | completed/correct | exact_single_candidate |
| d7-m5-c000024 | 4 | 12 | 8.49825 | completed/correct | exact_single_candidate |
| d7-m5-c000025 | 5 | 8 | 12.328 | completed/correct | exact_single_candidate |
| d7-m5-c000026 | 5 | 20 | 37.6525 | completed/correct | exact_single_candidate |
| d7-m5-c000027 | 5 | 3 | 3.61682 | completed/correct | exact_single_candidate |
| d7-m5-c000028 | 5 | 30 | 63.9666 | completed/correct | exact_single_candidate |
| d7-m5-c000029 | 4 | 40 | 233.105 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `5bcb0dfd0e6f8077ce8f9ea75e48052cab1ddee9ffc47b04297fcd86379c7d69`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
