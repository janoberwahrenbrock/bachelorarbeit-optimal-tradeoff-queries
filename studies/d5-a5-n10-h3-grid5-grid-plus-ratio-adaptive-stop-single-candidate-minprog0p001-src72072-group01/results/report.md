# d5-a5-n10-h3-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072-group01

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
adaptive, H3, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 7 | 70 |
| Queries, korrekte Lösungen | 10 | 7 | 70 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 7 | 70 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 347.84 | 3478.4 |
| API-Sekunden, korrekte Lösungen | 10 | 347.84 | 3478.4 |
| Controller-Sekunden, sämtliche Versuche | 10 | 348.533 | 3485.33 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: keine

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000000 | 2 | 3 | 35.4187 | completed/correct | exact_single_candidate |
| d5-m5-c000001 | 5 | 10 | 449.931 | completed/correct | exact_single_candidate |
| d5-m5-c000002 | 5 | 5 | 142.771 | completed/correct | exact_single_candidate |
| d5-m5-c000003 | 3 | 4 | 74.2431 | completed/correct | exact_single_candidate |
| d5-m5-c000004 | 5 | 9 | 1036.83 | completed/correct | exact_single_candidate |
| d5-m5-c000005 | 5 | 14 | 717.883 | completed/correct | exact_single_candidate |
| d5-m5-c000006 | 3 | 5 | 133.111 | completed/correct | exact_single_candidate |
| d5-m5-c000007 | 5 | 2 | 107.414 | completed/correct | exact_single_candidate |
| d5-m5-c000008 | 4 | 15 | 632.198 | completed/correct | exact_single_candidate |
| d5-m5-c000009 | 5 | 3 | 148.599 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `ed8cb204afb8d9fee9b1382b970e5f5f532b3340f8e95ea9d942d034aa10ec08`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
