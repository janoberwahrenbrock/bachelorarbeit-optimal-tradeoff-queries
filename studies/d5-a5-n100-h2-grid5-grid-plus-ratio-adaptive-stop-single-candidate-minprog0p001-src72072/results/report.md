# d5-a5-n100-h2-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
adaptive, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 8.34 | 834 |
| Queries, korrekte Lösungen | 100 | 8.34 | 834 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 8.34 | 834 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 3.70781 | 370.781 |
| API-Sekunden, korrekte Lösungen | 100 | 3.70781 | 370.781 |
| Controller-Sekunden, sämtliche Versuche | 100 | 4.40658 | 440.658 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000014, d5-m5-c000020, d5-m5-c000025, d5-m5-c000036, d5-m5-c000046, d5-m5-c000058, d5-m5-c000070, d5-m5-c000071, d5-m5-c000078, d5-m5-c000098

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000000 | 2 | 7 | 1.69882 | completed/correct | exact_single_candidate |
| d5-m5-c000001 | 5 | 10 | 4.81677 | completed/correct | exact_single_candidate |
| d5-m5-c000002 | 5 | 4 | 1.90915 | completed/correct | exact_single_candidate |
| d5-m5-c000003 | 3 | 3 | 1.33362 | completed/correct | exact_single_candidate |
| d5-m5-c000004 | 5 | 8 | 6.47538 | completed/correct | exact_single_candidate |
| d5-m5-c000005 | 5 | 14 | 7.25008 | completed/correct | exact_single_candidate |
| d5-m5-c000006 | 3 | 4 | 1.6257 | completed/correct | exact_single_candidate |
| d5-m5-c000007 | 5 | 2 | 1.61564 | completed/correct | exact_single_candidate |
| d5-m5-c000008 | 4 | 10 | 4.79832 | completed/correct | exact_single_candidate |
| d5-m5-c000009 | 5 | 3 | 2.03722 | completed/correct | exact_single_candidate |
| d5-m5-c000010 | 3 | 2 | 1.18206 | completed/correct | exact_single_candidate |
| d5-m5-c000011 | 5 | 7 | 4.59228 | completed/correct | exact_single_candidate |
| d5-m5-c000012 | 4 | 5 | 2.33605 | completed/correct | exact_single_candidate |
| d5-m5-c000013 | 3 | 10 | 3.09945 | completed/correct | exact_single_candidate |
| d5-m5-c000014 | 5 | 21 | 9.46163 | completed/correct | exact_single_candidate |
| d5-m5-c000015 | 5 | 3 | 1.93477 | completed/correct | exact_single_candidate |
| d5-m5-c000016 | 3 | 2 | 1.21526 | completed/correct | exact_single_candidate |
| d5-m5-c000017 | 4 | 3 | 1.57307 | completed/correct | exact_single_candidate |
| d5-m5-c000018 | 4 | 5 | 2.10591 | completed/correct | exact_single_candidate |
| d5-m5-c000019 | 4 | 4 | 2.14044 | completed/correct | exact_single_candidate |
| d5-m5-c000020 | 5 | 17 | 10.0165 | completed/correct | exact_single_candidate |
| d5-m5-c000021 | 5 | 12 | 4.6151 | completed/correct | exact_single_candidate |
| d5-m5-c000022 | 5 | 8 | 4.7114 | completed/correct | exact_single_candidate |
| d5-m5-c000023 | 5 | 4 | 2.74687 | completed/correct | exact_single_candidate |
| d5-m5-c000024 | 5 | 11 | 4.11819 | completed/correct | exact_single_candidate |
| d5-m5-c000025 | 5 | 22 | 8.63078 | completed/correct | exact_single_candidate |
| d5-m5-c000026 | 3 | 4 | 1.41152 | completed/correct | exact_single_candidate |
| d5-m5-c000027 | 4 | 4 | 1.92484 | completed/correct | exact_single_candidate |
| d5-m5-c000028 | 4 | 4 | 2.1098 | completed/correct | exact_single_candidate |
| d5-m5-c000029 | 4 | 8 | 2.51822 | completed/correct | exact_single_candidate |
| d5-m5-c000030 | 4 | 3 | 1.45503 | completed/correct | exact_single_candidate |
| d5-m5-c000031 | 4 | 9 | 3.00464 | completed/correct | exact_single_candidate |
| d5-m5-c000032 | 4 | 2 | 1.32247 | completed/correct | exact_single_candidate |
| d5-m5-c000033 | 3 | 2 | 1.23772 | completed/correct | exact_single_candidate |
| d5-m5-c000034 | 5 | 9 | 3.92625 | completed/correct | exact_single_candidate |
| d5-m5-c000035 | 4 | 6 | 2.06829 | completed/correct | exact_single_candidate |
| d5-m5-c000036 | 5 | 23 | 10.4247 | completed/correct | exact_single_candidate |
| d5-m5-c000037 | 4 | 9 | 3.12188 | completed/correct | exact_single_candidate |
| d5-m5-c000038 | 3 | 8 | 4.17962 | completed/correct | exact_single_candidate |
| d5-m5-c000039 | 5 | 9 | 4.36568 | completed/correct | exact_single_candidate |
| d5-m5-c000040 | 4 | 12 | 4.45648 | completed/correct | exact_single_candidate |
| d5-m5-c000041 | 4 | 3 | 1.5789 | completed/correct | exact_single_candidate |
| d5-m5-c000042 | 5 | 4 | 2.00481 | completed/correct | exact_single_candidate |
| d5-m5-c000043 | 5 | 4 | 1.83531 | completed/correct | exact_single_candidate |
| d5-m5-c000044 | 4 | 5 | 2.22044 | completed/correct | exact_single_candidate |
| d5-m5-c000045 | 4 | 2 | 1.27853 | completed/correct | exact_single_candidate |
| d5-m5-c000046 | 4 | 40 | 19.0362 | completed/correct | exact_single_candidate |
| d5-m5-c000047 | 4 | 6 | 3.14098 | completed/correct | exact_single_candidate |
| d5-m5-c000048 | 5 | 9 | 4.19087 | completed/correct | exact_single_candidate |
| d5-m5-c000049 | 3 | 9 | 3.05701 | completed/correct | exact_single_candidate |
| d5-m5-c000050 | 5 | 5 | 2.39593 | completed/correct | exact_single_candidate |
| d5-m5-c000051 | 5 | 12 | 6.30489 | completed/correct | exact_single_candidate |
| d5-m5-c000052 | 4 | 8 | 3.43899 | completed/correct | exact_single_candidate |
| d5-m5-c000053 | 5 | 7 | 2.75585 | completed/correct | exact_single_candidate |
| d5-m5-c000054 | 5 | 6 | 3.0701 | completed/correct | exact_single_candidate |
| d5-m5-c000055 | 5 | 4 | 1.93047 | completed/correct | exact_single_candidate |
| d5-m5-c000056 | 3 | 17 | 5.20696 | completed/correct | exact_single_candidate |
| d5-m5-c000057 | 4 | 3 | 1.47855 | completed/correct | exact_single_candidate |
| d5-m5-c000058 | 5 | 20 | 10.6693 | completed/correct | exact_single_candidate |
| d5-m5-c000059 | 4 | 4 | 1.82535 | completed/correct | exact_single_candidate |
| d5-m5-c000060 | 5 | 11 | 4.47362 | completed/correct | exact_single_candidate |
| d5-m5-c000061 | 5 | 8 | 3.35399 | completed/correct | exact_single_candidate |
| d5-m5-c000062 | 4 | 5 | 2.10666 | completed/correct | exact_single_candidate |
| d5-m5-c000063 | 4 | 3 | 1.41021 | completed/correct | exact_single_candidate |
| d5-m5-c000064 | 3 | 7 | 2.21303 | completed/correct | exact_single_candidate |
| d5-m5-c000065 | 3 | 11 | 3.16332 | completed/correct | exact_single_candidate |
| d5-m5-c000066 | 5 | 4 | 1.94231 | completed/correct | exact_single_candidate |
| d5-m5-c000067 | 3 | 20 | 5.81179 | completed/correct | exact_single_candidate |
| d5-m5-c000068 | 4 | 4 | 2.20917 | completed/correct | exact_single_candidate |
| d5-m5-c000069 | 3 | 5 | 1.72249 | completed/correct | exact_single_candidate |
| d5-m5-c000070 | 4 | 47 | 18.2137 | completed/correct | exact_single_candidate |
| d5-m5-c000071 | 5 | 17 | 8.90121 | completed/correct | exact_single_candidate |
| d5-m5-c000072 | 5 | 5 | 2.28597 | completed/correct | exact_single_candidate |
| d5-m5-c000073 | 3 | 5 | 1.73957 | completed/correct | exact_single_candidate |
| d5-m5-c000074 | 3 | 4 | 1.45454 | completed/correct | exact_single_candidate |
| d5-m5-c000075 | 3 | 9 | 2.72952 | completed/correct | exact_single_candidate |
| d5-m5-c000076 | 3 | 2 | 1.12435 | completed/correct | exact_single_candidate |
| d5-m5-c000077 | 4 | 5 | 2.19713 | completed/correct | exact_single_candidate |
| d5-m5-c000078 | 3 | 22 | 12.2836 | completed/correct | exact_single_candidate |
| d5-m5-c000079 | 3 | 4 | 1.59533 | completed/correct | exact_single_candidate |
| d5-m5-c000080 | 4 | 9 | 3.00835 | completed/correct | exact_single_candidate |
| d5-m5-c000081 | 4 | 6 | 2.22247 | completed/correct | exact_single_candidate |
| d5-m5-c000082 | 4 | 6 | 2.71947 | completed/correct | exact_single_candidate |
| d5-m5-c000083 | 5 | 5 | 2.38216 | completed/correct | exact_single_candidate |
| d5-m5-c000084 | 4 | 10 | 4.56556 | completed/correct | exact_single_candidate |
| d5-m5-c000085 | 4 | 2 | 1.37937 | completed/correct | exact_single_candidate |
| d5-m5-c000086 | 3 | 2 | 1.30553 | completed/correct | exact_single_candidate |
| d5-m5-c000087 | 3 | 1 | 0.988283 | completed/correct | exact_single_candidate |
| d5-m5-c000088 | 3 | 8 | 2.80596 | completed/correct | exact_single_candidate |
| d5-m5-c000089 | 5 | 3 | 1.71786 | completed/correct | exact_single_candidate |
| d5-m5-c000090 | 5 | 23 | 7.30422 | completed/correct | exact_single_candidate |
| d5-m5-c000091 | 5 | 11 | 3.72525 | completed/correct | exact_single_candidate |
| d5-m5-c000092 | 5 | 7 | 3.75241 | completed/correct | exact_single_candidate |
| d5-m5-c000093 | 3 | 3 | 1.41575 | completed/correct | exact_single_candidate |
| d5-m5-c000094 | 4 | 5 | 2.03965 | completed/correct | exact_single_candidate |
| d5-m5-c000095 | 5 | 5 | 3.86565 | completed/correct | exact_single_candidate |
| d5-m5-c000096 | 3 | 3 | 1.39403 | completed/correct | exact_single_candidate |
| d5-m5-c000097 | 4 | 9 | 4.75802 | completed/correct | exact_single_candidate |
| d5-m5-c000098 | 4 | 23 | 10.0722 | completed/correct | exact_single_candidate |
| d5-m5-c000099 | 4 | 14 | 5.44016 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `133061ab663f37931e551d101335a3f2ca668e458ad3b41e8d5cb1d72022c519`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
