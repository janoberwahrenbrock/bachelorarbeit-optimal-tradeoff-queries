# d3-a5-n100-h2-grid5-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
receding, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 8 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 4.66 | 466 |
| Queries, korrekte Lösungen | 100 | 4.66 | 466 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 4.66 | 466 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 0.810915 | 81.0915 |
| API-Sekunden, korrekte Lösungen | 100 | 0.810915 | 81.0915 |
| Controller-Sekunden, sämtliche Versuche | 100 | 1.36558 | 136.558 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d3-m5-c000000, d3-m5-c000001, d3-m5-c000019, d3-m5-c000066, d3-m5-c000067, d3-m5-c000099

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d3-m5-c000000 | 4 | 10 | 1.41845 | completed/correct | exact_single_candidate |
| d3-m5-c000001 | 4 | 11 | 1.35848 | completed/correct | exact_single_candidate |
| d3-m5-c000002 | 4 | 3 | 0.683424 | completed/correct | exact_single_candidate |
| d3-m5-c000003 | 3 | 5 | 0.805363 | completed/correct | exact_single_candidate |
| d3-m5-c000004 | 4 | 2 | 0.613707 | completed/correct | exact_single_candidate |
| d3-m5-c000005 | 2 | 2 | 0.556559 | completed/correct | exact_single_candidate |
| d3-m5-c000006 | 5 | 5 | 1.01163 | completed/correct | exact_single_candidate |
| d3-m5-c000007 | 3 | 3 | 0.65389 | completed/correct | exact_single_candidate |
| d3-m5-c000008 | 4 | 3 | 0.767576 | completed/correct | exact_single_candidate |
| d3-m5-c000009 | 4 | 2 | 0.638309 | completed/correct | exact_single_candidate |
| d3-m5-c000010 | 2 | 1 | 0.468854 | completed/correct | exact_single_candidate |
| d3-m5-c000011 | 2 | 1 | 0.462022 | completed/correct | exact_single_candidate |
| d3-m5-c000012 | 4 | 6 | 0.99529 | completed/correct | exact_single_candidate |
| d3-m5-c000013 | 4 | 5 | 0.996472 | completed/correct | exact_single_candidate |
| d3-m5-c000014 | 4 | 5 | 0.863194 | completed/correct | exact_single_candidate |
| d3-m5-c000015 | 3 | 3 | 0.648129 | completed/correct | exact_single_candidate |
| d3-m5-c000016 | 4 | 8 | 1.13011 | completed/correct | exact_single_candidate |
| d3-m5-c000017 | 4 | 5 | 0.98774 | completed/correct | exact_single_candidate |
| d3-m5-c000018 | 2 | 5 | 0.781397 | completed/correct | exact_single_candidate |
| d3-m5-c000019 | 3 | 37 | 3.68507 | completed/correct | exact_single_candidate |
| d3-m5-c000020 | 4 | 6 | 0.973133 | completed/correct | exact_single_candidate |
| d3-m5-c000021 | 3 | 5 | 0.858748 | completed/correct | exact_single_candidate |
| d3-m5-c000022 | 3 | 2 | 0.590007 | completed/correct | exact_single_candidate |
| d3-m5-c000023 | 4 | 2 | 0.625942 | completed/correct | exact_single_candidate |
| d3-m5-c000024 | 3 | 4 | 0.764463 | completed/correct | exact_single_candidate |
| d3-m5-c000025 | 1 | 0 | 0.0245486 | completed/correct | exact_single_candidate |
| d3-m5-c000026 | 2 | 3 | 0.618074 | completed/correct | exact_single_candidate |
| d3-m5-c000027 | 2 | 2 | 0.542635 | completed/correct | exact_single_candidate |
| d3-m5-c000028 | 3 | 4 | 0.785396 | completed/correct | exact_single_candidate |
| d3-m5-c000029 | 5 | 3 | 0.759664 | completed/correct | exact_single_candidate |
| d3-m5-c000030 | 3 | 10 | 1.30705 | completed/correct | exact_single_candidate |
| d3-m5-c000031 | 2 | 3 | 0.606622 | completed/correct | exact_single_candidate |
| d3-m5-c000032 | 3 | 4 | 0.709065 | completed/correct | exact_single_candidate |
| d3-m5-c000033 | 3 | 7 | 0.958612 | completed/correct | exact_single_candidate |
| d3-m5-c000034 | 4 | 2 | 0.602058 | completed/correct | exact_single_candidate |
| d3-m5-c000035 | 2 | 1 | 0.47077 | completed/correct | exact_single_candidate |
| d3-m5-c000036 | 3 | 2 | 0.584626 | completed/correct | exact_single_candidate |
| d3-m5-c000037 | 3 | 2 | 0.583749 | completed/correct | exact_single_candidate |
| d3-m5-c000038 | 3 | 5 | 0.801697 | completed/correct | exact_single_candidate |
| d3-m5-c000039 | 3 | 3 | 0.667841 | completed/correct | exact_single_candidate |
| d3-m5-c000040 | 4 | 3 | 0.741923 | completed/correct | exact_single_candidate |
| d3-m5-c000041 | 5 | 7 | 1.04426 | completed/correct | exact_single_candidate |
| d3-m5-c000042 | 3 | 4 | 0.741799 | completed/correct | exact_single_candidate |
| d3-m5-c000043 | 3 | 2 | 0.547243 | completed/correct | exact_single_candidate |
| d3-m5-c000044 | 3 | 5 | 0.834237 | completed/correct | exact_single_candidate |
| d3-m5-c000045 | 4 | 9 | 1.16032 | completed/correct | exact_single_candidate |
| d3-m5-c000046 | 3 | 2 | 0.553046 | completed/correct | exact_single_candidate |
| d3-m5-c000047 | 4 | 7 | 1.01726 | completed/correct | exact_single_candidate |
| d3-m5-c000048 | 2 | 5 | 0.758596 | completed/correct | exact_single_candidate |
| d3-m5-c000049 | 2 | 3 | 0.605387 | completed/correct | exact_single_candidate |
| d3-m5-c000050 | 3 | 3 | 0.657657 | completed/correct | exact_single_candidate |
| d3-m5-c000051 | 3 | 5 | 0.903224 | completed/correct | exact_single_candidate |
| d3-m5-c000052 | 4 | 6 | 1.06417 | completed/correct | exact_single_candidate |
| d3-m5-c000053 | 4 | 3 | 0.70781 | completed/correct | exact_single_candidate |
| d3-m5-c000054 | 3 | 4 | 0.724398 | completed/correct | exact_single_candidate |
| d3-m5-c000055 | 4 | 7 | 1.00188 | completed/correct | exact_single_candidate |
| d3-m5-c000056 | 3 | 5 | 0.81507 | completed/correct | exact_single_candidate |
| d3-m5-c000057 | 3 | 4 | 0.760184 | completed/correct | exact_single_candidate |
| d3-m5-c000058 | 2 | 8 | 1.0422 | completed/correct | exact_single_candidate |
| d3-m5-c000059 | 3 | 2 | 0.582054 | completed/correct | exact_single_candidate |
| d3-m5-c000060 | 3 | 2 | 0.546378 | completed/correct | exact_single_candidate |
| d3-m5-c000061 | 4 | 5 | 0.865656 | completed/correct | exact_single_candidate |
| d3-m5-c000062 | 3 | 8 | 1.02141 | completed/correct | exact_single_candidate |
| d3-m5-c000063 | 3 | 11 | 1.26587 | completed/correct | exact_single_candidate |
| d3-m5-c000064 | 4 | 5 | 0.884088 | completed/correct | exact_single_candidate |
| d3-m5-c000065 | 2 | 5 | 0.766557 | completed/correct | exact_single_candidate |
| d3-m5-c000066 | 3 | 11 | 1.36162 | completed/correct | exact_single_candidate |
| d3-m5-c000067 | 4 | 11 | 1.72035 | completed/correct | exact_single_candidate |
| d3-m5-c000068 | 3 | 4 | 0.735689 | completed/correct | exact_single_candidate |
| d3-m5-c000069 | 2 | 6 | 0.853124 | completed/correct | exact_single_candidate |
| d3-m5-c000070 | 2 | 7 | 0.909076 | completed/correct | exact_single_candidate |
| d3-m5-c000071 | 4 | 4 | 0.790896 | completed/correct | exact_single_candidate |
| d3-m5-c000072 | 2 | 4 | 0.709344 | completed/correct | exact_single_candidate |
| d3-m5-c000073 | 3 | 2 | 0.555614 | completed/correct | exact_single_candidate |
| d3-m5-c000074 | 3 | 4 | 0.765845 | completed/correct | exact_single_candidate |
| d3-m5-c000075 | 4 | 8 | 1.31842 | completed/correct | exact_single_candidate |
| d3-m5-c000076 | 2 | 3 | 0.610029 | completed/correct | exact_single_candidate |
| d3-m5-c000077 | 3 | 2 | 0.571019 | completed/correct | exact_single_candidate |
| d3-m5-c000078 | 3 | 2 | 0.589935 | completed/correct | exact_single_candidate |
| d3-m5-c000079 | 3 | 5 | 0.893356 | completed/correct | exact_single_candidate |
| d3-m5-c000080 | 2 | 5 | 0.739361 | completed/correct | exact_single_candidate |
| d3-m5-c000081 | 3 | 2 | 0.589285 | completed/correct | exact_single_candidate |
| d3-m5-c000082 | 3 | 3 | 0.653235 | completed/correct | exact_single_candidate |
| d3-m5-c000083 | 3 | 6 | 0.830371 | completed/correct | exact_single_candidate |
| d3-m5-c000084 | 2 | 2 | 0.537164 | completed/correct | exact_single_candidate |
| d3-m5-c000085 | 2 | 3 | 0.613188 | completed/correct | exact_single_candidate |
| d3-m5-c000086 | 3 | 3 | 0.649296 | completed/correct | exact_single_candidate |
| d3-m5-c000087 | 2 | 1 | 0.476668 | completed/correct | exact_single_candidate |
| d3-m5-c000088 | 3 | 2 | 0.574624 | completed/correct | exact_single_candidate |
| d3-m5-c000089 | 3 | 5 | 0.782612 | completed/correct | exact_single_candidate |
| d3-m5-c000090 | 3 | 6 | 0.873799 | completed/correct | exact_single_candidate |
| d3-m5-c000091 | 4 | 4 | 0.732092 | completed/correct | exact_single_candidate |
| d3-m5-c000092 | 3 | 2 | 0.570834 | completed/correct | exact_single_candidate |
| d3-m5-c000093 | 4 | 4 | 0.822528 | completed/correct | exact_single_candidate |
| d3-m5-c000094 | 4 | 3 | 0.713462 | completed/correct | exact_single_candidate |
| d3-m5-c000095 | 4 | 4 | 0.835017 | completed/correct | exact_single_candidate |
| d3-m5-c000096 | 1 | 0 | 0.0247452 | completed/correct | exact_single_candidate |
| d3-m5-c000097 | 3 | 3 | 0.69674 | completed/correct | exact_single_candidate |
| d3-m5-c000098 | 3 | 3 | 0.660107 | completed/correct | exact_single_candidate |
| d3-m5-c000099 | 3 | 10 | 1.35903 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `04f2ff2c8b25440a8be0770c6ccd90c759d7a5dfd1e53ca9f7c0c05ed5132652`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
