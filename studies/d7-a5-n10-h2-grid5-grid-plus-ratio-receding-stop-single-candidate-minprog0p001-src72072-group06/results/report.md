# d7-a5-n10-h2-grid5-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072-group06

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
receding, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 19.6 | 196 |
| Queries, korrekte Lösungen | 10 | 19.6 | 196 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 19.6 | 196 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 53.8108 | 538.108 |
| API-Sekunden, korrekte Lösungen | 10 | 53.8108 | 538.108 |
| Controller-Sekunden, sämtliche Versuche | 10 | 54.55 | 545.5 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: keine

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d7-m5-c000050 | 5 | 12 | 34.8659 | completed/correct | exact_single_candidate |
| d7-m5-c000051 | 5 | 7 | 7.82415 | completed/correct | exact_single_candidate |
| d7-m5-c000052 | 5 | 5 | 4.2888 | completed/correct | exact_single_candidate |
| d7-m5-c000053 | 5 | 12 | 18.6999 | completed/correct | exact_single_candidate |
| d7-m5-c000054 | 4 | 16 | 33.0906 | completed/correct | exact_single_candidate |
| d7-m5-c000055 | 5 | 40 | 84.6123 | completed/correct | exact_single_candidate |
| d7-m5-c000056 | 4 | 20 | 64.0164 | completed/correct | exact_single_candidate |
| d7-m5-c000057 | 5 | 53 | 169.907 | completed/correct | exact_single_candidate |
| d7-m5-c000058 | 5 | 22 | 112.775 | completed/correct | exact_single_candidate |
| d7-m5-c000059 | 5 | 9 | 8.02797 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `faa535dc0a6d8411084419cb8a9f58087896d7d3e6fe607fd62a881449dee6a0`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
