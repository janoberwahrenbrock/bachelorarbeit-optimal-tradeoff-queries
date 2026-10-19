# d5-a5-n100-h2-grid20-grid-plus-ratio-countdown-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
countdown, H2, Grid 20, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 8.57 | 857 |
| Queries, korrekte Lösungen | 100 | 8.57 | 857 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 8.57 | 857 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 5.15851 | 515.851 |
| API-Sekunden, korrekte Lösungen | 100 | 5.15851 | 515.851 |
| Controller-Sekunden, sämtliche Versuche | 100 | 5.80176 | 580.176 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000025, d5-m5-c000036, d5-m5-c000046, d5-m5-c000058, d5-m5-c000070, d5-m5-c000098

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000000 | 2 | 8 | 2.49309 | completed/correct | exact_single_candidate |
| d5-m5-c000001 | 5 | 8 | 5.90044 | completed/correct | exact_single_candidate |
| d5-m5-c000002 | 5 | 4 | 2.57794 | completed/correct | exact_single_candidate |
| d5-m5-c000003 | 3 | 4 | 2.09841 | completed/correct | exact_single_candidate |
| d5-m5-c000004 | 5 | 10 | 11.4484 | completed/correct | exact_single_candidate |
| d5-m5-c000005 | 5 | 12 | 10.2728 | completed/correct | exact_single_candidate |
| d5-m5-c000006 | 3 | 8 | 3.50416 | completed/correct | exact_single_candidate |
| d5-m5-c000007 | 5 | 2 | 2.36115 | completed/correct | exact_single_candidate |
| d5-m5-c000008 | 4 | 11 | 7.7302 | completed/correct | exact_single_candidate |
| d5-m5-c000009 | 5 | 3 | 3.52609 | completed/correct | exact_single_candidate |
| d5-m5-c000010 | 3 | 2 | 1.49239 | completed/correct | exact_single_candidate |
| d5-m5-c000011 | 5 | 6 | 6.64797 | completed/correct | exact_single_candidate |
| d5-m5-c000012 | 4 | 6 | 2.81704 | completed/correct | exact_single_candidate |
| d5-m5-c000013 | 3 | 10 | 3.84892 | completed/correct | exact_single_candidate |
| d5-m5-c000014 | 5 | 18 | 9.08793 | completed/correct | exact_single_candidate |
| d5-m5-c000015 | 5 | 4 | 2.93852 | completed/correct | exact_single_candidate |
| d5-m5-c000016 | 3 | 2 | 1.35639 | completed/correct | exact_single_candidate |
| d5-m5-c000017 | 4 | 4 | 2.38391 | completed/correct | exact_single_candidate |
| d5-m5-c000018 | 4 | 8 | 3.6328 | completed/correct | exact_single_candidate |
| d5-m5-c000019 | 4 | 4 | 2.70385 | completed/correct | exact_single_candidate |
| d5-m5-c000020 | 5 | 14 | 9.22357 | completed/correct | exact_single_candidate |
| d5-m5-c000021 | 5 | 12 | 6.40831 | completed/correct | exact_single_candidate |
| d5-m5-c000022 | 5 | 8 | 6.01508 | completed/correct | exact_single_candidate |
| d5-m5-c000023 | 5 | 4 | 3.71373 | completed/correct | exact_single_candidate |
| d5-m5-c000024 | 5 | 13 | 6.44286 | completed/correct | exact_single_candidate |
| d5-m5-c000025 | 5 | 30 | 15.8817 | completed/correct | exact_single_candidate |
| d5-m5-c000026 | 3 | 4 | 1.62877 | completed/correct | exact_single_candidate |
| d5-m5-c000027 | 4 | 4 | 2.33586 | completed/correct | exact_single_candidate |
| d5-m5-c000028 | 4 | 4 | 2.96599 | completed/correct | exact_single_candidate |
| d5-m5-c000029 | 4 | 12 | 5.19363 | completed/correct | exact_single_candidate |
| d5-m5-c000030 | 4 | 4 | 3.58091 | completed/correct | exact_single_candidate |
| d5-m5-c000031 | 4 | 4 | 2.46966 | completed/correct | exact_single_candidate |
| d5-m5-c000032 | 4 | 2 | 2.06203 | completed/correct | exact_single_candidate |
| d5-m5-c000033 | 3 | 2 | 1.47579 | completed/correct | exact_single_candidate |
| d5-m5-c000034 | 5 | 8 | 6.45395 | completed/correct | exact_single_candidate |
| d5-m5-c000035 | 4 | 6 | 2.76762 | completed/correct | exact_single_candidate |
| d5-m5-c000036 | 5 | 26 | 16.8722 | completed/correct | exact_single_candidate |
| d5-m5-c000037 | 4 | 6 | 3.15621 | completed/correct | exact_single_candidate |
| d5-m5-c000038 | 3 | 8 | 4.53062 | completed/correct | exact_single_candidate |
| d5-m5-c000039 | 5 | 8 | 6.29548 | completed/correct | exact_single_candidate |
| d5-m5-c000040 | 4 | 8 | 4.21258 | completed/correct | exact_single_candidate |
| d5-m5-c000041 | 4 | 4 | 2.41972 | completed/correct | exact_single_candidate |
| d5-m5-c000042 | 5 | 4 | 2.87092 | completed/correct | exact_single_candidate |
| d5-m5-c000043 | 5 | 4 | 2.6944 | completed/correct | exact_single_candidate |
| d5-m5-c000044 | 4 | 12 | 6.14215 | completed/correct | exact_single_candidate |
| d5-m5-c000045 | 4 | 2 | 1.83037 | completed/correct | exact_single_candidate |
| d5-m5-c000046 | 4 | 36 | 27.8652 | completed/correct | exact_single_candidate |
| d5-m5-c000047 | 4 | 8 | 5.54918 | completed/correct | exact_single_candidate |
| d5-m5-c000048 | 5 | 10 | 6.87712 | completed/correct | exact_single_candidate |
| d5-m5-c000049 | 3 | 6 | 2.54534 | completed/correct | exact_single_candidate |
| d5-m5-c000050 | 5 | 6 | 3.89044 | completed/correct | exact_single_candidate |
| d5-m5-c000051 | 5 | 6 | 4.67328 | completed/correct | exact_single_candidate |
| d5-m5-c000052 | 4 | 6 | 2.7385 | completed/correct | exact_single_candidate |
| d5-m5-c000053 | 5 | 6 | 3.92002 | completed/correct | exact_single_candidate |
| d5-m5-c000054 | 5 | 6 | 3.72446 | completed/correct | exact_single_candidate |
| d5-m5-c000055 | 5 | 4 | 2.36026 | completed/correct | exact_single_candidate |
| d5-m5-c000056 | 3 | 12 | 4.8388 | completed/correct | exact_single_candidate |
| d5-m5-c000057 | 4 | 3 | 2.11446 | completed/correct | exact_single_candidate |
| d5-m5-c000058 | 5 | 26 | 18.7189 | completed/correct | exact_single_candidate |
| d5-m5-c000059 | 4 | 4 | 2.55703 | completed/correct | exact_single_candidate |
| d5-m5-c000060 | 5 | 10 | 5.82283 | completed/correct | exact_single_candidate |
| d5-m5-c000061 | 5 | 6 | 3.55377 | completed/correct | exact_single_candidate |
| d5-m5-c000062 | 4 | 6 | 3.1 | completed/correct | exact_single_candidate |
| d5-m5-c000063 | 4 | 4 | 2.38423 | completed/correct | exact_single_candidate |
| d5-m5-c000064 | 3 | 9 | 3.85444 | completed/correct | exact_single_candidate |
| d5-m5-c000065 | 3 | 12 | 4.98444 | completed/correct | exact_single_candidate |
| d5-m5-c000066 | 5 | 8 | 4.78407 | completed/correct | exact_single_candidate |
| d5-m5-c000067 | 3 | 20 | 7.68789 | completed/correct | exact_single_candidate |
| d5-m5-c000068 | 4 | 2 | 1.90035 | completed/correct | exact_single_candidate |
| d5-m5-c000069 | 3 | 2 | 1.24895 | completed/correct | exact_single_candidate |
| d5-m5-c000070 | 4 | 56 | 34.8114 | completed/correct | exact_single_candidate |
| d5-m5-c000071 | 5 | 21 | 11.6358 | completed/correct | exact_single_candidate |
| d5-m5-c000072 | 5 | 4 | 3.08523 | completed/correct | exact_single_candidate |
| d5-m5-c000073 | 3 | 4 | 1.90228 | completed/correct | exact_single_candidate |
| d5-m5-c000074 | 3 | 4 | 1.6463 | completed/correct | exact_single_candidate |
| d5-m5-c000075 | 3 | 9 | 3.72788 | completed/correct | exact_single_candidate |
| d5-m5-c000076 | 3 | 2 | 1.40334 | completed/correct | exact_single_candidate |
| d5-m5-c000077 | 4 | 10 | 4.57726 | completed/correct | exact_single_candidate |
| d5-m5-c000078 | 3 | 20 | 11.1992 | completed/correct | exact_single_candidate |
| d5-m5-c000079 | 3 | 3 | 1.84714 | completed/correct | exact_single_candidate |
| d5-m5-c000080 | 4 | 6 | 2.97572 | completed/correct | exact_single_candidate |
| d5-m5-c000081 | 4 | 4 | 2.20333 | completed/correct | exact_single_candidate |
| d5-m5-c000082 | 4 | 6 | 3.28234 | completed/correct | exact_single_candidate |
| d5-m5-c000083 | 5 | 6 | 4.17119 | completed/correct | exact_single_candidate |
| d5-m5-c000084 | 4 | 6 | 2.65753 | completed/correct | exact_single_candidate |
| d5-m5-c000085 | 4 | 2 | 2.13094 | completed/correct | exact_single_candidate |
| d5-m5-c000086 | 3 | 2 | 1.70314 | completed/correct | exact_single_candidate |
| d5-m5-c000087 | 3 | 2 | 1.55235 | completed/correct | exact_single_candidate |
| d5-m5-c000088 | 3 | 4 | 1.92755 | completed/correct | exact_single_candidate |
| d5-m5-c000089 | 5 | 4 | 2.96183 | completed/correct | exact_single_candidate |
| d5-m5-c000090 | 5 | 20 | 9.25967 | completed/correct | exact_single_candidate |
| d5-m5-c000091 | 5 | 16 | 7.52706 | completed/correct | exact_single_candidate |
| d5-m5-c000092 | 5 | 10 | 6.43656 | completed/correct | exact_single_candidate |
| d5-m5-c000093 | 3 | 2 | 1.345 | completed/correct | exact_single_candidate |
| d5-m5-c000094 | 4 | 15 | 6.62954 | completed/correct | exact_single_candidate |
| d5-m5-c000095 | 5 | 6 | 5.71916 | completed/correct | exact_single_candidate |
| d5-m5-c000096 | 3 | 2 | 1.22784 | completed/correct | exact_single_candidate |
| d5-m5-c000097 | 4 | 4 | 2.81636 | completed/correct | exact_single_candidate |
| d5-m5-c000098 | 4 | 30 | 16.8016 | completed/correct | exact_single_candidate |
| d5-m5-c000099 | 4 | 12 | 6.52585 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `133061ab663f37931e551d101335a3f2ca668e458ad3b41e8d5cb1d72022c519`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
