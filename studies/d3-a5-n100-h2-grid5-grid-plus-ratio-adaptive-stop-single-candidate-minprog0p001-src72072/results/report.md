# d3-a5-n100-h2-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
adaptive, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 8 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 3.15 | 315 |
| Queries, korrekte Lösungen | 100 | 3.15 | 315 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 3.15 | 315 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 0.785571 | 78.5571 |
| API-Sekunden, korrekte Lösungen | 100 | 0.785571 | 78.5571 |
| Controller-Sekunden, sämtliche Versuche | 100 | 1.36637 | 136.637 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d3-m5-c000000, d3-m5-c000013, d3-m5-c000016, d3-m5-c000019, d3-m5-c000047, d3-m5-c000066, d3-m5-c000067, d3-m5-c000075, d3-m5-c000099

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d3-m5-c000000 | 4 | 9 | 1.58723 | completed/correct | exact_single_candidate |
| d3-m5-c000001 | 4 | 2 | 0.744198 | completed/correct | exact_single_candidate |
| d3-m5-c000002 | 4 | 4 | 0.810118 | completed/correct | exact_single_candidate |
| d3-m5-c000003 | 3 | 3 | 0.719669 | completed/correct | exact_single_candidate |
| d3-m5-c000004 | 4 | 2 | 0.618782 | completed/correct | exact_single_candidate |
| d3-m5-c000005 | 2 | 1 | 0.626514 | completed/correct | exact_single_candidate |
| d3-m5-c000006 | 5 | 3 | 0.900734 | completed/correct | exact_single_candidate |
| d3-m5-c000007 | 3 | 1 | 0.642808 | completed/correct | exact_single_candidate |
| d3-m5-c000008 | 4 | 2 | 0.701293 | completed/correct | exact_single_candidate |
| d3-m5-c000009 | 4 | 2 | 0.660381 | completed/correct | exact_single_candidate |
| d3-m5-c000010 | 2 | 1 | 0.63406 | completed/correct | exact_single_candidate |
| d3-m5-c000011 | 2 | 1 | 0.621647 | completed/correct | exact_single_candidate |
| d3-m5-c000012 | 4 | 4 | 0.818826 | completed/correct | exact_single_candidate |
| d3-m5-c000013 | 4 | 6 | 1.16235 | completed/correct | exact_single_candidate |
| d3-m5-c000014 | 4 | 2 | 0.632125 | completed/correct | exact_single_candidate |
| d3-m5-c000015 | 3 | 2 | 0.650227 | completed/correct | exact_single_candidate |
| d3-m5-c000016 | 4 | 10 | 1.41386 | completed/correct | exact_single_candidate |
| d3-m5-c000017 | 4 | 3 | 0.769277 | completed/correct | exact_single_candidate |
| d3-m5-c000018 | 2 | 5 | 0.957694 | completed/correct | exact_single_candidate |
| d3-m5-c000019 | 3 | 10 | 1.31405 | completed/correct | exact_single_candidate |
| d3-m5-c000020 | 4 | 2 | 0.790775 | completed/correct | exact_single_candidate |
| d3-m5-c000021 | 3 | 2 | 0.65513 | completed/correct | exact_single_candidate |
| d3-m5-c000022 | 3 | 1 | 0.642504 | completed/correct | exact_single_candidate |
| d3-m5-c000023 | 4 | 2 | 0.661189 | completed/correct | exact_single_candidate |
| d3-m5-c000024 | 3 | 3 | 0.750628 | completed/correct | exact_single_candidate |
| d3-m5-c000025 | 1 | 0 | 0.0248228 | completed/correct | exact_single_candidate |
| d3-m5-c000026 | 2 | 2 | 0.707668 | completed/correct | exact_single_candidate |
| d3-m5-c000027 | 2 | 2 | 0.716696 | completed/correct | exact_single_candidate |
| d3-m5-c000028 | 3 | 3 | 0.727292 | completed/correct | exact_single_candidate |
| d3-m5-c000029 | 5 | 3 | 0.793355 | completed/correct | exact_single_candidate |
| d3-m5-c000030 | 3 | 3 | 0.711845 | completed/correct | exact_single_candidate |
| d3-m5-c000031 | 2 | 2 | 0.717267 | completed/correct | exact_single_candidate |
| d3-m5-c000032 | 3 | 2 | 0.648474 | completed/correct | exact_single_candidate |
| d3-m5-c000033 | 3 | 3 | 0.732405 | completed/correct | exact_single_candidate |
| d3-m5-c000034 | 4 | 2 | 0.656054 | completed/correct | exact_single_candidate |
| d3-m5-c000035 | 2 | 1 | 0.625544 | completed/correct | exact_single_candidate |
| d3-m5-c000036 | 3 | 1 | 0.642467 | completed/correct | exact_single_candidate |
| d3-m5-c000037 | 3 | 1 | 0.641888 | completed/correct | exact_single_candidate |
| d3-m5-c000038 | 3 | 2 | 0.655456 | completed/correct | exact_single_candidate |
| d3-m5-c000039 | 3 | 2 | 0.646507 | completed/correct | exact_single_candidate |
| d3-m5-c000040 | 4 | 2 | 0.704229 | completed/correct | exact_single_candidate |
| d3-m5-c000041 | 5 | 3 | 0.808696 | completed/correct | exact_single_candidate |
| d3-m5-c000042 | 3 | 4 | 0.876803 | completed/correct | exact_single_candidate |
| d3-m5-c000043 | 3 | 2 | 0.647897 | completed/correct | exact_single_candidate |
| d3-m5-c000044 | 3 | 4 | 0.884348 | completed/correct | exact_single_candidate |
| d3-m5-c000045 | 4 | 3 | 0.750083 | completed/correct | exact_single_candidate |
| d3-m5-c000046 | 3 | 2 | 0.642352 | completed/correct | exact_single_candidate |
| d3-m5-c000047 | 4 | 13 | 1.87539 | completed/correct | exact_single_candidate |
| d3-m5-c000048 | 2 | 3 | 0.800722 | completed/correct | exact_single_candidate |
| d3-m5-c000049 | 2 | 3 | 0.789596 | completed/correct | exact_single_candidate |
| d3-m5-c000050 | 3 | 4 | 0.787969 | completed/correct | exact_single_candidate |
| d3-m5-c000051 | 3 | 4 | 0.857609 | completed/correct | exact_single_candidate |
| d3-m5-c000052 | 4 | 3 | 0.787941 | completed/correct | exact_single_candidate |
| d3-m5-c000053 | 4 | 2 | 0.737822 | completed/correct | exact_single_candidate |
| d3-m5-c000054 | 3 | 4 | 0.836136 | completed/correct | exact_single_candidate |
| d3-m5-c000055 | 4 | 3 | 0.75018 | completed/correct | exact_single_candidate |
| d3-m5-c000056 | 3 | 3 | 0.745638 | completed/correct | exact_single_candidate |
| d3-m5-c000057 | 3 | 4 | 0.802587 | completed/correct | exact_single_candidate |
| d3-m5-c000058 | 2 | 5 | 0.960935 | completed/correct | exact_single_candidate |
| d3-m5-c000059 | 3 | 2 | 0.649868 | completed/correct | exact_single_candidate |
| d3-m5-c000060 | 3 | 2 | 0.640927 | completed/correct | exact_single_candidate |
| d3-m5-c000061 | 4 | 3 | 0.723412 | completed/correct | exact_single_candidate |
| d3-m5-c000062 | 3 | 5 | 0.858019 | completed/correct | exact_single_candidate |
| d3-m5-c000063 | 3 | 4 | 0.849027 | completed/correct | exact_single_candidate |
| d3-m5-c000064 | 4 | 4 | 0.843791 | completed/correct | exact_single_candidate |
| d3-m5-c000065 | 2 | 1 | 0.629248 | completed/correct | exact_single_candidate |
| d3-m5-c000066 | 3 | 11 | 1.47407 | completed/correct | exact_single_candidate |
| d3-m5-c000067 | 4 | 15 | 2.16503 | completed/correct | exact_single_candidate |
| d3-m5-c000068 | 3 | 5 | 0.885286 | completed/correct | exact_single_candidate |
| d3-m5-c000069 | 2 | 3 | 0.780132 | completed/correct | exact_single_candidate |
| d3-m5-c000070 | 2 | 4 | 0.874743 | completed/correct | exact_single_candidate |
| d3-m5-c000071 | 4 | 3 | 0.835594 | completed/correct | exact_single_candidate |
| d3-m5-c000072 | 2 | 3 | 0.798145 | completed/correct | exact_single_candidate |
| d3-m5-c000073 | 3 | 2 | 0.641908 | completed/correct | exact_single_candidate |
| d3-m5-c000074 | 3 | 2 | 0.654052 | completed/correct | exact_single_candidate |
| d3-m5-c000075 | 4 | 8 | 1.39763 | completed/correct | exact_single_candidate |
| d3-m5-c000076 | 2 | 1 | 0.628801 | completed/correct | exact_single_candidate |
| d3-m5-c000077 | 3 | 1 | 0.631849 | completed/correct | exact_single_candidate |
| d3-m5-c000078 | 3 | 2 | 0.656409 | completed/correct | exact_single_candidate |
| d3-m5-c000079 | 3 | 3 | 0.808333 | completed/correct | exact_single_candidate |
| d3-m5-c000080 | 2 | 2 | 0.638799 | completed/correct | exact_single_candidate |
| d3-m5-c000081 | 3 | 1 | 0.645607 | completed/correct | exact_single_candidate |
| d3-m5-c000082 | 3 | 2 | 0.647161 | completed/correct | exact_single_candidate |
| d3-m5-c000083 | 3 | 3 | 0.696364 | completed/correct | exact_single_candidate |
| d3-m5-c000084 | 2 | 1 | 0.625633 | completed/correct | exact_single_candidate |
| d3-m5-c000085 | 2 | 4 | 0.838064 | completed/correct | exact_single_candidate |
| d3-m5-c000086 | 3 | 1 | 0.640553 | completed/correct | exact_single_candidate |
| d3-m5-c000087 | 2 | 1 | 0.625654 | completed/correct | exact_single_candidate |
| d3-m5-c000088 | 3 | 1 | 0.647616 | completed/correct | exact_single_candidate |
| d3-m5-c000089 | 3 | 2 | 0.647341 | completed/correct | exact_single_candidate |
| d3-m5-c000090 | 3 | 2 | 0.645072 | completed/correct | exact_single_candidate |
| d3-m5-c000091 | 4 | 4 | 0.910783 | completed/correct | exact_single_candidate |
| d3-m5-c000092 | 3 | 2 | 0.645115 | completed/correct | exact_single_candidate |
| d3-m5-c000093 | 4 | 3 | 0.777769 | completed/correct | exact_single_candidate |
| d3-m5-c000094 | 4 | 3 | 0.767334 | completed/correct | exact_single_candidate |
| d3-m5-c000095 | 4 | 3 | 0.854419 | completed/correct | exact_single_candidate |
| d3-m5-c000096 | 1 | 0 | 0.024915 | completed/correct | exact_single_candidate |
| d3-m5-c000097 | 3 | 3 | 0.724054 | completed/correct | exact_single_candidate |
| d3-m5-c000098 | 3 | 1 | 0.641574 | completed/correct | exact_single_candidate |
| d3-m5-c000099 | 3 | 9 | 1.30629 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `04f2ff2c8b25440a8be0770c6ccd90c759d7a5dfd1e53ca9f7c0c05ed5132652`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
