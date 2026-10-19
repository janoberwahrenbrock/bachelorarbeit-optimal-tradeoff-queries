# d7-a5-n10-h2-grid5-grid-plus-ratio-countdown-stop-single-candidate-minprog0p001-src72072-group02

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
countdown, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 24 | 240 |
| Queries, korrekte Lösungen | 10 | 24 | 240 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 24 | 240 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 71.5809 | 715.809 |
| API-Sekunden, korrekte Lösungen | 10 | 71.5809 | 715.809 |
| Controller-Sekunden, sämtliche Versuche | 10 | 72.3546 | 723.546 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d7-m5-c000019

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d7-m5-c000010 | 5 | 14 | 21.6867 | completed/correct | exact_single_candidate |
| d7-m5-c000011 | 5 | 7 | 2.74424 | completed/correct | exact_single_candidate |
| d7-m5-c000012 | 5 | 6 | 3.05685 | completed/correct | exact_single_candidate |
| d7-m5-c000013 | 5 | 12 | 7.65583 | completed/correct | exact_single_candidate |
| d7-m5-c000014 | 5 | 42 | 191.552 | completed/correct | exact_single_candidate |
| d7-m5-c000015 | 5 | 31 | 27.772 | completed/correct | exact_single_candidate |
| d7-m5-c000016 | 5 | 10 | 10.7015 | completed/correct | exact_single_candidate |
| d7-m5-c000017 | 5 | 44 | 127.1 | completed/correct | exact_single_candidate |
| d7-m5-c000018 | 5 | 15 | 18.4421 | completed/correct | exact_single_candidate |
| d7-m5-c000019 | 5 | 59 | 305.098 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `eaa58a47f473416ff14d8e5751ea22febc36510035dc954fd9b5c44601432acc`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
