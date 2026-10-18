# d5-a5-n100-h2-grid3-grid-countdown-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
countdown, H2, Grid 3, Queryquelle grid, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 8.74 | 874 |
| Queries, korrekte Lösungen | 100 | 8.74 | 874 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 8.74 | 874 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 1.66385 | 166.385 |
| API-Sekunden, korrekte Lösungen | 100 | 1.66385 | 166.385 |
| Controller-Sekunden, sämtliche Versuche | 100 | 2.29974 | 229.974 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000001, d5-m5-c000004, d5-m5-c000014, d5-m5-c000036, d5-m5-c000046, d5-m5-c000058, d5-m5-c000061, d5-m5-c000070

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000000 | 2 | 7 | 1.12919 | completed/correct | exact_single_candidate |
| d5-m5-c000001 | 5 | 16 | 3.09066 | completed/correct | exact_single_candidate |
| d5-m5-c000002 | 5 | 4 | 1.12635 | completed/correct | exact_single_candidate |
| d5-m5-c000003 | 3 | 2 | 0.816371 | completed/correct | exact_single_candidate |
| d5-m5-c000004 | 5 | 12 | 3.64396 | completed/correct | exact_single_candidate |
| d5-m5-c000005 | 5 | 12 | 1.8973 | completed/correct | exact_single_candidate |
| d5-m5-c000006 | 3 | 6 | 1.07508 | completed/correct | exact_single_candidate |
| d5-m5-c000007 | 5 | 4 | 1.15324 | completed/correct | exact_single_candidate |
| d5-m5-c000008 | 4 | 16 | 2.81117 | completed/correct | exact_single_candidate |
| d5-m5-c000009 | 5 | 4 | 1.20369 | completed/correct | exact_single_candidate |
| d5-m5-c000010 | 3 | 2 | 0.813427 | completed/correct | exact_single_candidate |
| d5-m5-c000011 | 5 | 6 | 1.45689 | completed/correct | exact_single_candidate |
| d5-m5-c000012 | 4 | 6 | 1.1616 | completed/correct | exact_single_candidate |
| d5-m5-c000013 | 3 | 14 | 1.85884 | completed/correct | exact_single_candidate |
| d5-m5-c000014 | 5 | 27 | 3.74107 | completed/correct | exact_single_candidate |
| d5-m5-c000015 | 5 | 4 | 1.09509 | completed/correct | exact_single_candidate |
| d5-m5-c000016 | 3 | 2 | 0.790604 | completed/correct | exact_single_candidate |
| d5-m5-c000017 | 4 | 4 | 1.01163 | completed/correct | exact_single_candidate |
| d5-m5-c000018 | 4 | 6 | 1.36263 | completed/correct | exact_single_candidate |
| d5-m5-c000019 | 4 | 6 | 1.44023 | completed/correct | exact_single_candidate |
| d5-m5-c000020 | 5 | 14 | 2.43412 | completed/correct | exact_single_candidate |
| d5-m5-c000021 | 5 | 11 | 1.83094 | completed/correct | exact_single_candidate |
| d5-m5-c000022 | 5 | 8 | 2.07965 | completed/correct | exact_single_candidate |
| d5-m5-c000023 | 5 | 4 | 1.25844 | completed/correct | exact_single_candidate |
| d5-m5-c000024 | 5 | 12 | 1.79763 | completed/correct | exact_single_candidate |
| d5-m5-c000025 | 5 | 19 | 2.72133 | completed/correct | exact_single_candidate |
| d5-m5-c000026 | 3 | 5 | 1.02092 | completed/correct | exact_single_candidate |
| d5-m5-c000027 | 4 | 6 | 1.34579 | completed/correct | exact_single_candidate |
| d5-m5-c000028 | 4 | 4 | 1.1107 | completed/correct | exact_single_candidate |
| d5-m5-c000029 | 4 | 9 | 1.47423 | completed/correct | exact_single_candidate |
| d5-m5-c000030 | 4 | 2 | 0.889887 | completed/correct | exact_single_candidate |
| d5-m5-c000031 | 4 | 4 | 1.02579 | completed/correct | exact_single_candidate |
| d5-m5-c000032 | 4 | 2 | 0.947472 | completed/correct | exact_single_candidate |
| d5-m5-c000033 | 3 | 4 | 0.972805 | completed/correct | exact_single_candidate |
| d5-m5-c000034 | 5 | 10 | 1.82322 | completed/correct | exact_single_candidate |
| d5-m5-c000035 | 4 | 6 | 1.22023 | completed/correct | exact_single_candidate |
| d5-m5-c000036 | 5 | 24 | 3.38043 | completed/correct | exact_single_candidate |
| d5-m5-c000037 | 4 | 12 | 1.83279 | completed/correct | exact_single_candidate |
| d5-m5-c000038 | 3 | 8 | 1.57894 | completed/correct | exact_single_candidate |
| d5-m5-c000039 | 5 | 8 | 1.70588 | completed/correct | exact_single_candidate |
| d5-m5-c000040 | 4 | 15 | 2.19929 | completed/correct | exact_single_candidate |
| d5-m5-c000041 | 4 | 4 | 1.02913 | completed/correct | exact_single_candidate |
| d5-m5-c000042 | 5 | 4 | 1.09769 | completed/correct | exact_single_candidate |
| d5-m5-c000043 | 5 | 4 | 1.07686 | completed/correct | exact_single_candidate |
| d5-m5-c000044 | 4 | 6 | 1.21516 | completed/correct | exact_single_candidate |
| d5-m5-c000045 | 4 | 2 | 0.890101 | completed/correct | exact_single_candidate |
| d5-m5-c000046 | 4 | 38 | 5.97431 | completed/correct | exact_single_candidate |
| d5-m5-c000047 | 4 | 8 | 1.72142 | completed/correct | exact_single_candidate |
| d5-m5-c000048 | 5 | 10 | 2.28606 | completed/correct | exact_single_candidate |
| d5-m5-c000049 | 3 | 6 | 1.29778 | completed/correct | exact_single_candidate |
| d5-m5-c000050 | 5 | 6 | 1.34106 | completed/correct | exact_single_candidate |
| d5-m5-c000051 | 5 | 6 | 1.451 | completed/correct | exact_single_candidate |
| d5-m5-c000052 | 4 | 8 | 1.45795 | completed/correct | exact_single_candidate |
| d5-m5-c000053 | 5 | 8 | 1.47863 | completed/correct | exact_single_candidate |
| d5-m5-c000054 | 5 | 6 | 1.7261 | completed/correct | exact_single_candidate |
| d5-m5-c000055 | 5 | 5 | 1.14937 | completed/correct | exact_single_candidate |
| d5-m5-c000056 | 3 | 5 | 0.998836 | completed/correct | exact_single_candidate |
| d5-m5-c000057 | 4 | 4 | 0.980931 | completed/correct | exact_single_candidate |
| d5-m5-c000058 | 5 | 22 | 4.33564 | completed/correct | exact_single_candidate |
| d5-m5-c000059 | 4 | 4 | 1.0631 | completed/correct | exact_single_candidate |
| d5-m5-c000060 | 5 | 8 | 1.54807 | completed/correct | exact_single_candidate |
| d5-m5-c000061 | 5 | 20 | 3.068 | completed/correct | exact_single_candidate |
| d5-m5-c000062 | 4 | 6 | 1.21513 | completed/correct | exact_single_candidate |
| d5-m5-c000063 | 4 | 4 | 1.12939 | completed/correct | exact_single_candidate |
| d5-m5-c000064 | 3 | 9 | 1.48182 | completed/correct | exact_single_candidate |
| d5-m5-c000065 | 3 | 7 | 1.20691 | completed/correct | exact_single_candidate |
| d5-m5-c000066 | 5 | 8 | 1.57644 | completed/correct | exact_single_candidate |
| d5-m5-c000067 | 3 | 20 | 2.37434 | completed/correct | exact_single_candidate |
| d5-m5-c000068 | 4 | 4 | 1.19705 | completed/correct | exact_single_candidate |
| d5-m5-c000069 | 3 | 4 | 0.908662 | completed/correct | exact_single_candidate |
| d5-m5-c000070 | 4 | 45 | 6.18001 | completed/correct | exact_single_candidate |
| d5-m5-c000071 | 5 | 20 | 2.87392 | completed/correct | exact_single_candidate |
| d5-m5-c000072 | 5 | 4 | 1.31804 | completed/correct | exact_single_candidate |
| d5-m5-c000073 | 3 | 8 | 1.47196 | completed/correct | exact_single_candidate |
| d5-m5-c000074 | 3 | 6 | 1.05148 | completed/correct | exact_single_candidate |
| d5-m5-c000075 | 3 | 10 | 1.48748 | completed/correct | exact_single_candidate |
| d5-m5-c000076 | 3 | 2 | 0.805551 | completed/correct | exact_single_candidate |
| d5-m5-c000077 | 4 | 6 | 1.19828 | completed/correct | exact_single_candidate |
| d5-m5-c000078 | 3 | 14 | 2.16417 | completed/correct | exact_single_candidate |
| d5-m5-c000079 | 3 | 4 | 0.990417 | completed/correct | exact_single_candidate |
| d5-m5-c000080 | 4 | 4 | 1.07005 | completed/correct | exact_single_candidate |
| d5-m5-c000081 | 4 | 4 | 1.08862 | completed/correct | exact_single_candidate |
| d5-m5-c000082 | 4 | 4 | 1.14122 | completed/correct | exact_single_candidate |
| d5-m5-c000083 | 5 | 4 | 1.38935 | completed/correct | exact_single_candidate |
| d5-m5-c000084 | 4 | 16 | 2.2198 | completed/correct | exact_single_candidate |
| d5-m5-c000085 | 4 | 4 | 1.10841 | completed/correct | exact_single_candidate |
| d5-m5-c000086 | 3 | 2 | 0.852417 | completed/correct | exact_single_candidate |
| d5-m5-c000087 | 3 | 2 | 0.854771 | completed/correct | exact_single_candidate |
| d5-m5-c000088 | 3 | 8 | 1.52543 | completed/correct | exact_single_candidate |
| d5-m5-c000089 | 5 | 4 | 1.19389 | completed/correct | exact_single_candidate |
| d5-m5-c000090 | 5 | 23 | 3.00347 | completed/correct | exact_single_candidate |
| d5-m5-c000091 | 5 | 10 | 1.64065 | completed/correct | exact_single_candidate |
| d5-m5-c000092 | 5 | 8 | 1.73596 | completed/correct | exact_single_candidate |
| d5-m5-c000093 | 3 | 2 | 0.812347 | completed/correct | exact_single_candidate |
| d5-m5-c000094 | 4 | 15 | 2.10818 | completed/correct | exact_single_candidate |
| d5-m5-c000095 | 5 | 8 | 1.99518 | completed/correct | exact_single_candidate |
| d5-m5-c000096 | 3 | 2 | 0.776537 | completed/correct | exact_single_candidate |
| d5-m5-c000097 | 4 | 8 | 1.88856 | completed/correct | exact_single_candidate |
| d5-m5-c000098 | 4 | 20 | 2.61535 | completed/correct | exact_single_candidate |
| d5-m5-c000099 | 4 | 14 | 2.21724 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `133061ab663f37931e551d101335a3f2ca668e458ad3b41e8d5cb1d72022c519`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
