# d7-a5-n10-h2-grid5-grid-plus-ratio-countdown-stop-single-candidate-minprog0p001-src72072-group09

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
countdown, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 9/10; regulär ungelöst: 1/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 15.8 | 158 |
| Queries, korrekte Lösungen | 9 | 17.3333 | 156 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 15.8 | 158 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 22.132 | 221.32 |
| API-Sekunden, korrekte Lösungen | 9 | 24.399 | 219.591 |
| Controller-Sekunden, sämtliche Versuche | 10 | 22.8355 | 228.355 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: keine

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d7-m5-c000080 | 5 | 35 | 49.1819 | completed/correct | exact_single_candidate |
| d7-m5-c000081 | 4 | 6 | 2.61851 | completed/correct | exact_single_candidate |
| d7-m5-c000082 | 5 | 34 | 85.9561 | completed/correct | exact_single_candidate |
| d7-m5-c000083 | 5 | 12 | 6.03389 | completed/correct | exact_single_candidate |
| d7-m5-c000084 | 5 | 2 | 1.72867 | completed/regular_unsolved | insufficient_expected_progress |
| d7-m5-c000085 | 4 | 26 | 48.9245 | completed/correct | exact_single_candidate |
| d7-m5-c000086 | 5 | 6 | 3.34512 | completed/correct | exact_single_candidate |
| d7-m5-c000087 | 5 | 12 | 6.70433 | completed/correct | exact_single_candidate |
| d7-m5-c000088 | 5 | 12 | 8.13788 | completed/correct | exact_single_candidate |
| d7-m5-c000089 | 5 | 13 | 8.68917 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `7fa34415d39b943a2f49e48fbbb30bbb888d9862cd4062bd744745fbeffdcc0d`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
