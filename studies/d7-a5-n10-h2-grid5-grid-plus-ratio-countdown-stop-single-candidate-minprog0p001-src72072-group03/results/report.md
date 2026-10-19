# d7-a5-n10-h2-grid5-grid-plus-ratio-countdown-stop-single-candidate-minprog0p001-src72072-group03

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
countdown, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 18 | 180 |
| Queries, korrekte Lösungen | 10 | 18 | 180 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 18 | 180 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 28.5915 | 285.915 |
| API-Sekunden, korrekte Lösungen | 10 | 28.5915 | 285.915 |
| Controller-Sekunden, sämtliche Versuche | 10 | 29.3158 | 293.158 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: keine

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d7-m5-c000020 | 5 | 24 | 44.5295 | completed/correct | exact_single_candidate |
| d7-m5-c000021 | 5 | 12 | 7.42981 | completed/correct | exact_single_candidate |
| d7-m5-c000022 | 4 | 20 | 21.9938 | completed/correct | exact_single_candidate |
| d7-m5-c000023 | 5 | 13 | 5.26694 | completed/correct | exact_single_candidate |
| d7-m5-c000024 | 4 | 14 | 7.1119 | completed/correct | exact_single_candidate |
| d7-m5-c000025 | 5 | 8 | 6.26792 | completed/correct | exact_single_candidate |
| d7-m5-c000026 | 5 | 24 | 70.6729 | completed/correct | exact_single_candidate |
| d7-m5-c000027 | 5 | 3 | 2.18285 | completed/correct | exact_single_candidate |
| d7-m5-c000028 | 5 | 31 | 33.4364 | completed/correct | exact_single_candidate |
| d7-m5-c000029 | 4 | 31 | 87.0231 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `5bcb0dfd0e6f8077ce8f9ea75e48052cab1ddee9ffc47b04297fcd86379c7d69`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
