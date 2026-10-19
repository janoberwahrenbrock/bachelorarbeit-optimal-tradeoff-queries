# d5-a5-n100-h2-grid20-grid-adaptive-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
adaptive, H2, Grid 20, Queryquelle grid, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 8.31 | 831 |
| Queries, korrekte Lösungen | 100 | 8.31 | 831 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 8.31 | 831 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 8.90139 | 890.139 |
| API-Sekunden, korrekte Lösungen | 100 | 8.90139 | 890.139 |
| Controller-Sekunden, sämtliche Versuche | 100 | 9.59789 | 959.789 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000014, d5-m5-c000036, d5-m5-c000046, d5-m5-c000058, d5-m5-c000067, d5-m5-c000070, d5-m5-c000071, d5-m5-c000090, d5-m5-c000098

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000000 | 2 | 6 | 3.68454 | completed/correct | exact_single_candidate |
| d5-m5-c000001 | 5 | 6 | 7.90133 | completed/correct | exact_single_candidate |
| d5-m5-c000002 | 5 | 4 | 4.07656 | completed/correct | exact_single_candidate |
| d5-m5-c000003 | 3 | 3 | 2.59564 | completed/correct | exact_single_candidate |
| d5-m5-c000004 | 5 | 8 | 14.3274 | completed/correct | exact_single_candidate |
| d5-m5-c000005 | 5 | 14 | 20.2716 | completed/correct | exact_single_candidate |
| d5-m5-c000006 | 3 | 7 | 6.68658 | completed/correct | exact_single_candidate |
| d5-m5-c000007 | 5 | 2 | 3.52166 | completed/correct | exact_single_candidate |
| d5-m5-c000008 | 4 | 13 | 14.8239 | completed/correct | exact_single_candidate |
| d5-m5-c000009 | 5 | 3 | 4.4572 | completed/correct | exact_single_candidate |
| d5-m5-c000010 | 3 | 2 | 2.13862 | completed/correct | exact_single_candidate |
| d5-m5-c000011 | 5 | 6 | 11.2133 | completed/correct | exact_single_candidate |
| d5-m5-c000012 | 4 | 6 | 5.97848 | completed/correct | exact_single_candidate |
| d5-m5-c000013 | 3 | 10 | 7.32704 | completed/correct | exact_single_candidate |
| d5-m5-c000014 | 5 | 23 | 23.0484 | completed/correct | exact_single_candidate |
| d5-m5-c000015 | 5 | 3 | 4.22591 | completed/correct | exact_single_candidate |
| d5-m5-c000016 | 3 | 2 | 2.03199 | completed/correct | exact_single_candidate |
| d5-m5-c000017 | 4 | 3 | 3.28328 | completed/correct | exact_single_candidate |
| d5-m5-c000018 | 4 | 7 | 5.83427 | completed/correct | exact_single_candidate |
| d5-m5-c000019 | 4 | 7 | 9.11268 | completed/correct | exact_single_candidate |
| d5-m5-c000020 | 5 | 14 | 20.4411 | completed/correct | exact_single_candidate |
| d5-m5-c000021 | 5 | 13 | 13.3277 | completed/correct | exact_single_candidate |
| d5-m5-c000022 | 5 | 11 | 14.7705 | completed/correct | exact_single_candidate |
| d5-m5-c000023 | 5 | 4 | 6.75464 | completed/correct | exact_single_candidate |
| d5-m5-c000024 | 5 | 9 | 7.72291 | completed/correct | exact_single_candidate |
| d5-m5-c000025 | 5 | 18 | 16.5231 | completed/correct | exact_single_candidate |
| d5-m5-c000026 | 3 | 5 | 3.55195 | completed/correct | exact_single_candidate |
| d5-m5-c000027 | 4 | 4 | 4.0069 | completed/correct | exact_single_candidate |
| d5-m5-c000028 | 4 | 4 | 4.86563 | completed/correct | exact_single_candidate |
| d5-m5-c000029 | 4 | 7 | 5.39076 | completed/correct | exact_single_candidate |
| d5-m5-c000030 | 4 | 3 | 2.85093 | completed/correct | exact_single_candidate |
| d5-m5-c000031 | 4 | 8 | 6.65679 | completed/correct | exact_single_candidate |
| d5-m5-c000032 | 4 | 2 | 2.53823 | completed/correct | exact_single_candidate |
| d5-m5-c000033 | 3 | 2 | 2.18414 | completed/correct | exact_single_candidate |
| d5-m5-c000034 | 5 | 9 | 10.2611 | completed/correct | exact_single_candidate |
| d5-m5-c000035 | 4 | 7 | 5.1972 | completed/correct | exact_single_candidate |
| d5-m5-c000036 | 5 | 24 | 26.1756 | completed/correct | exact_single_candidate |
| d5-m5-c000037 | 4 | 6 | 5.39773 | completed/correct | exact_single_candidate |
| d5-m5-c000038 | 3 | 6 | 7.10361 | completed/correct | exact_single_candidate |
| d5-m5-c000039 | 5 | 8 | 10.5576 | completed/correct | exact_single_candidate |
| d5-m5-c000040 | 4 | 11 | 10.5669 | completed/correct | exact_single_candidate |
| d5-m5-c000041 | 4 | 3 | 3.28341 | completed/correct | exact_single_candidate |
| d5-m5-c000042 | 5 | 4 | 4.32993 | completed/correct | exact_single_candidate |
| d5-m5-c000043 | 5 | 4 | 4.10526 | completed/correct | exact_single_candidate |
| d5-m5-c000044 | 4 | 6 | 5.7723 | completed/correct | exact_single_candidate |
| d5-m5-c000045 | 4 | 2 | 2.466 | completed/correct | exact_single_candidate |
| d5-m5-c000046 | 4 | 40 | 50.137 | completed/correct | exact_single_candidate |
| d5-m5-c000047 | 4 | 6 | 8.58298 | completed/correct | exact_single_candidate |
| d5-m5-c000048 | 5 | 9 | 10.9906 | completed/correct | exact_single_candidate |
| d5-m5-c000049 | 3 | 11 | 10.046 | completed/correct | exact_single_candidate |
| d5-m5-c000050 | 5 | 4 | 5.21322 | completed/correct | exact_single_candidate |
| d5-m5-c000051 | 5 | 11 | 15.5891 | completed/correct | exact_single_candidate |
| d5-m5-c000052 | 4 | 6 | 5.50162 | completed/correct | exact_single_candidate |
| d5-m5-c000053 | 5 | 5 | 5.38711 | completed/correct | exact_single_candidate |
| d5-m5-c000054 | 5 | 6 | 7.76366 | completed/correct | exact_single_candidate |
| d5-m5-c000055 | 5 | 4 | 4.19634 | completed/correct | exact_single_candidate |
| d5-m5-c000056 | 3 | 13 | 10.7652 | completed/correct | exact_single_candidate |
| d5-m5-c000057 | 4 | 3 | 2.99913 | completed/correct | exact_single_candidate |
| d5-m5-c000058 | 5 | 17 | 22.7775 | completed/correct | exact_single_candidate |
| d5-m5-c000059 | 4 | 4 | 4.20327 | completed/correct | exact_single_candidate |
| d5-m5-c000060 | 5 | 11 | 11.5629 | completed/correct | exact_single_candidate |
| d5-m5-c000061 | 5 | 6 | 7.13865 | completed/correct | exact_single_candidate |
| d5-m5-c000062 | 4 | 5 | 4.75418 | completed/correct | exact_single_candidate |
| d5-m5-c000063 | 4 | 3 | 2.86559 | completed/correct | exact_single_candidate |
| d5-m5-c000064 | 3 | 6 | 4.00372 | completed/correct | exact_single_candidate |
| d5-m5-c000065 | 3 | 8 | 5.46036 | completed/correct | exact_single_candidate |
| d5-m5-c000066 | 5 | 5 | 5.12356 | completed/correct | exact_single_candidate |
| d5-m5-c000067 | 3 | 26 | 21.0453 | completed/correct | exact_single_candidate |
| d5-m5-c000068 | 4 | 4 | 5.23658 | completed/correct | exact_single_candidate |
| d5-m5-c000069 | 3 | 4 | 2.81623 | completed/correct | exact_single_candidate |
| d5-m5-c000070 | 4 | 47 | 49.6789 | completed/correct | exact_single_candidate |
| d5-m5-c000071 | 5 | 25 | 24.1126 | completed/correct | exact_single_candidate |
| d5-m5-c000072 | 5 | 5 | 5.30279 | completed/correct | exact_single_candidate |
| d5-m5-c000073 | 3 | 3 | 2.60758 | completed/correct | exact_single_candidate |
| d5-m5-c000074 | 3 | 4 | 3.06412 | completed/correct | exact_single_candidate |
| d5-m5-c000075 | 3 | 9 | 6.10346 | completed/correct | exact_single_candidate |
| d5-m5-c000076 | 3 | 2 | 2.01121 | completed/correct | exact_single_candidate |
| d5-m5-c000077 | 4 | 8 | 8.41232 | completed/correct | exact_single_candidate |
| d5-m5-c000078 | 3 | 19 | 20.0005 | completed/correct | exact_single_candidate |
| d5-m5-c000079 | 3 | 4 | 3.49985 | completed/correct | exact_single_candidate |
| d5-m5-c000080 | 4 | 5 | 4.80975 | completed/correct | exact_single_candidate |
| d5-m5-c000081 | 4 | 4 | 4.12356 | completed/correct | exact_single_candidate |
| d5-m5-c000082 | 4 | 6 | 6.74955 | completed/correct | exact_single_candidate |
| d5-m5-c000083 | 5 | 5 | 5.85446 | completed/correct | exact_single_candidate |
| d5-m5-c000084 | 4 | 6 | 5.48045 | completed/correct | exact_single_candidate |
| d5-m5-c000085 | 4 | 2 | 2.58639 | completed/correct | exact_single_candidate |
| d5-m5-c000086 | 3 | 2 | 2.29581 | completed/correct | exact_single_candidate |
| d5-m5-c000087 | 3 | 1 | 1.62432 | completed/correct | exact_single_candidate |
| d5-m5-c000088 | 3 | 5 | 4.75427 | completed/correct | exact_single_candidate |
| d5-m5-c000089 | 5 | 4 | 5.3447 | completed/correct | exact_single_candidate |
| d5-m5-c000090 | 5 | 27 | 26.9145 | completed/correct | exact_single_candidate |
| d5-m5-c000091 | 5 | 14 | 12.9438 | completed/correct | exact_single_candidate |
| d5-m5-c000092 | 5 | 7 | 9.4026 | completed/correct | exact_single_candidate |
| d5-m5-c000093 | 3 | 3 | 2.62866 | completed/correct | exact_single_candidate |
| d5-m5-c000094 | 4 | 12 | 10.7469 | completed/correct | exact_single_candidate |
| d5-m5-c000095 | 5 | 5 | 9.79962 | completed/correct | exact_single_candidate |
| d5-m5-c000096 | 3 | 3 | 2.45348 | completed/correct | exact_single_candidate |
| d5-m5-c000097 | 4 | 4 | 4.95149 | completed/correct | exact_single_candidate |
| d5-m5-c000098 | 4 | 27 | 28.4151 | completed/correct | exact_single_candidate |
| d5-m5-c000099 | 4 | 17 | 15.9645 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `133061ab663f37931e551d101335a3f2ca668e458ad3b41e8d5cb1d72022c519`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
