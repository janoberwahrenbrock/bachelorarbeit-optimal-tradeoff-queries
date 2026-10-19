# d7-a5-n10-h2-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072-group02

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
adaptive, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 18.1 | 181 |
| Queries, korrekte Lösungen | 10 | 18.1 | 181 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 18.1 | 181 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 59.2606 | 592.606 |
| API-Sekunden, korrekte Lösungen | 10 | 59.2606 | 592.606 |
| Controller-Sekunden, sämtliche Versuche | 10 | 60.1078 | 601.078 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d7-m5-c000014

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d7-m5-c000010 | 5 | 14 | 44.4529 | completed/correct | exact_single_candidate |
| d7-m5-c000011 | 5 | 7 | 5.88704 | completed/correct | exact_single_candidate |
| d7-m5-c000012 | 5 | 6 | 5.95828 | completed/correct | exact_single_candidate |
| d7-m5-c000013 | 5 | 9 | 8.6513 | completed/correct | exact_single_candidate |
| d7-m5-c000014 | 5 | 37 | 283.968 | completed/correct | exact_single_candidate |
| d7-m5-c000015 | 5 | 16 | 18.1006 | completed/correct | exact_single_candidate |
| d7-m5-c000016 | 5 | 12 | 37.8026 | completed/correct | exact_single_candidate |
| d7-m5-c000017 | 5 | 39 | 70.4867 | completed/correct | exact_single_candidate |
| d7-m5-c000018 | 5 | 11 | 16.4452 | completed/correct | exact_single_candidate |
| d7-m5-c000019 | 5 | 30 | 100.854 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `eaa58a47f473416ff14d8e5751ea22febc36510035dc954fd9b5c44601432acc`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
