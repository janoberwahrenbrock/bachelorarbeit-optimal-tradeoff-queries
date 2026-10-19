# d5-a5-n100-h2-grid5-grid-countdown-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
countdown, H2, Grid 5, Queryquelle grid, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 8.84 | 884 |
| Queries, korrekte Lösungen | 100 | 8.84 | 884 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 8.84 | 884 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 2.08641 | 208.641 |
| API-Sekunden, korrekte Lösungen | 100 | 2.08641 | 208.641 |
| Controller-Sekunden, sämtliche Versuche | 100 | 2.73046 | 273.046 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000025, d5-m5-c000036, d5-m5-c000046, d5-m5-c000058, d5-m5-c000070, d5-m5-c000071, d5-m5-c000078

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000000 | 2 | 7 | 1.41258 | completed/correct | exact_single_candidate |
| d5-m5-c000001 | 5 | 8 | 2.23815 | completed/correct | exact_single_candidate |
| d5-m5-c000002 | 5 | 4 | 1.19241 | completed/correct | exact_single_candidate |
| d5-m5-c000003 | 3 | 4 | 1.01761 | completed/correct | exact_single_candidate |
| d5-m5-c000004 | 5 | 10 | 3.75192 | completed/correct | exact_single_candidate |
| d5-m5-c000005 | 5 | 16 | 2.87265 | completed/correct | exact_single_candidate |
| d5-m5-c000006 | 3 | 4 | 0.980744 | completed/correct | exact_single_candidate |
| d5-m5-c000007 | 5 | 4 | 1.52798 | completed/correct | exact_single_candidate |
| d5-m5-c000008 | 4 | 14 | 3.19223 | completed/correct | exact_single_candidate |
| d5-m5-c000009 | 5 | 4 | 1.42786 | completed/correct | exact_single_candidate |
| d5-m5-c000010 | 3 | 2 | 0.873912 | completed/correct | exact_single_candidate |
| d5-m5-c000011 | 5 | 6 | 1.84604 | completed/correct | exact_single_candidate |
| d5-m5-c000012 | 4 | 6 | 1.35869 | completed/correct | exact_single_candidate |
| d5-m5-c000013 | 3 | 9 | 1.69045 | completed/correct | exact_single_candidate |
| d5-m5-c000014 | 5 | 26 | 4.27627 | completed/correct | exact_single_candidate |
| d5-m5-c000015 | 5 | 4 | 1.25988 | completed/correct | exact_single_candidate |
| d5-m5-c000016 | 3 | 2 | 0.83157 | completed/correct | exact_single_candidate |
| d5-m5-c000017 | 4 | 4 | 1.14248 | completed/correct | exact_single_candidate |
| d5-m5-c000018 | 4 | 6 | 1.40304 | completed/correct | exact_single_candidate |
| d5-m5-c000019 | 4 | 4 | 1.22775 | completed/correct | exact_single_candidate |
| d5-m5-c000020 | 5 | 14 | 3.40505 | completed/correct | exact_single_candidate |
| d5-m5-c000021 | 5 | 11 | 2.2427 | completed/correct | exact_single_candidate |
| d5-m5-c000022 | 5 | 8 | 2.48697 | completed/correct | exact_single_candidate |
| d5-m5-c000023 | 5 | 4 | 1.49353 | completed/correct | exact_single_candidate |
| d5-m5-c000024 | 5 | 12 | 2.31163 | completed/correct | exact_single_candidate |
| d5-m5-c000025 | 5 | 29 | 5.24598 | completed/correct | exact_single_candidate |
| d5-m5-c000026 | 3 | 4 | 0.932696 | completed/correct | exact_single_candidate |
| d5-m5-c000027 | 4 | 6 | 1.46377 | completed/correct | exact_single_candidate |
| d5-m5-c000028 | 4 | 4 | 1.35447 | completed/correct | exact_single_candidate |
| d5-m5-c000029 | 4 | 9 | 1.86927 | completed/correct | exact_single_candidate |
| d5-m5-c000030 | 4 | 2 | 0.992481 | completed/correct | exact_single_candidate |
| d5-m5-c000031 | 4 | 6 | 1.52922 | completed/correct | exact_single_candidate |
| d5-m5-c000032 | 4 | 2 | 1.00526 | completed/correct | exact_single_candidate |
| d5-m5-c000033 | 3 | 2 | 0.854389 | completed/correct | exact_single_candidate |
| d5-m5-c000034 | 5 | 10 | 2.4482 | completed/correct | exact_single_candidate |
| d5-m5-c000035 | 4 | 6 | 1.37956 | completed/correct | exact_single_candidate |
| d5-m5-c000036 | 5 | 24 | 4.91666 | completed/correct | exact_single_candidate |
| d5-m5-c000037 | 4 | 10 | 1.99276 | completed/correct | exact_single_candidate |
| d5-m5-c000038 | 3 | 8 | 2.04192 | completed/correct | exact_single_candidate |
| d5-m5-c000039 | 5 | 12 | 3.12486 | completed/correct | exact_single_candidate |
| d5-m5-c000040 | 4 | 14 | 2.75456 | completed/correct | exact_single_candidate |
| d5-m5-c000041 | 4 | 4 | 1.24539 | completed/correct | exact_single_candidate |
| d5-m5-c000042 | 5 | 4 | 1.23667 | completed/correct | exact_single_candidate |
| d5-m5-c000043 | 5 | 4 | 1.23654 | completed/correct | exact_single_candidate |
| d5-m5-c000044 | 4 | 10 | 2.12765 | completed/correct | exact_single_candidate |
| d5-m5-c000045 | 4 | 2 | 1.05405 | completed/correct | exact_single_candidate |
| d5-m5-c000046 | 4 | 34 | 7.69656 | completed/correct | exact_single_candidate |
| d5-m5-c000047 | 4 | 10 | 2.52122 | completed/correct | exact_single_candidate |
| d5-m5-c000048 | 5 | 12 | 3.64018 | completed/correct | exact_single_candidate |
| d5-m5-c000049 | 3 | 10 | 1.90378 | completed/correct | exact_single_candidate |
| d5-m5-c000050 | 5 | 6 | 1.60815 | completed/correct | exact_single_candidate |
| d5-m5-c000051 | 5 | 6 | 1.69889 | completed/correct | exact_single_candidate |
| d5-m5-c000052 | 4 | 10 | 2.44154 | completed/correct | exact_single_candidate |
| d5-m5-c000053 | 5 | 8 | 1.79404 | completed/correct | exact_single_candidate |
| d5-m5-c000054 | 5 | 6 | 1.68139 | completed/correct | exact_single_candidate |
| d5-m5-c000055 | 5 | 4 | 1.22175 | completed/correct | exact_single_candidate |
| d5-m5-c000056 | 3 | 16 | 2.61309 | completed/correct | exact_single_candidate |
| d5-m5-c000057 | 4 | 4 | 1.09195 | completed/correct | exact_single_candidate |
| d5-m5-c000058 | 5 | 20 | 5.29064 | completed/correct | exact_single_candidate |
| d5-m5-c000059 | 4 | 4 | 1.30827 | completed/correct | exact_single_candidate |
| d5-m5-c000060 | 5 | 14 | 2.99942 | completed/correct | exact_single_candidate |
| d5-m5-c000061 | 5 | 8 | 1.79601 | completed/correct | exact_single_candidate |
| d5-m5-c000062 | 4 | 6 | 1.3976 | completed/correct | exact_single_candidate |
| d5-m5-c000063 | 4 | 4 | 1.19665 | completed/correct | exact_single_candidate |
| d5-m5-c000064 | 3 | 11 | 2.05615 | completed/correct | exact_single_candidate |
| d5-m5-c000065 | 3 | 18 | 2.8027 | completed/correct | exact_single_candidate |
| d5-m5-c000066 | 5 | 8 | 2.1211 | completed/correct | exact_single_candidate |
| d5-m5-c000067 | 3 | 16 | 2.58733 | completed/correct | exact_single_candidate |
| d5-m5-c000068 | 4 | 4 | 1.25286 | completed/correct | exact_single_candidate |
| d5-m5-c000069 | 3 | 4 | 1.03626 | completed/correct | exact_single_candidate |
| d5-m5-c000070 | 4 | 52 | 11.1407 | completed/correct | exact_single_candidate |
| d5-m5-c000071 | 5 | 22 | 4.33992 | completed/correct | exact_single_candidate |
| d5-m5-c000072 | 5 | 4 | 1.37226 | completed/correct | exact_single_candidate |
| d5-m5-c000073 | 3 | 6 | 1.36313 | completed/correct | exact_single_candidate |
| d5-m5-c000074 | 3 | 4 | 1.14667 | completed/correct | exact_single_candidate |
| d5-m5-c000075 | 3 | 8 | 1.53585 | completed/correct | exact_single_candidate |
| d5-m5-c000076 | 3 | 2 | 0.853081 | completed/correct | exact_single_candidate |
| d5-m5-c000077 | 4 | 8 | 1.57772 | completed/correct | exact_single_candidate |
| d5-m5-c000078 | 3 | 21 | 4.97081 | completed/correct | exact_single_candidate |
| d5-m5-c000079 | 3 | 4 | 1.08697 | completed/correct | exact_single_candidate |
| d5-m5-c000080 | 4 | 8 | 1.537 | completed/correct | exact_single_candidate |
| d5-m5-c000081 | 4 | 4 | 1.12079 | completed/correct | exact_single_candidate |
| d5-m5-c000082 | 4 | 4 | 1.13227 | completed/correct | exact_single_candidate |
| d5-m5-c000083 | 5 | 6 | 1.65408 | completed/correct | exact_single_candidate |
| d5-m5-c000084 | 4 | 10 | 2.36241 | completed/correct | exact_single_candidate |
| d5-m5-c000085 | 4 | 4 | 1.25964 | completed/correct | exact_single_candidate |
| d5-m5-c000086 | 3 | 2 | 0.919118 | completed/correct | exact_single_candidate |
| d5-m5-c000087 | 3 | 2 | 0.969118 | completed/correct | exact_single_candidate |
| d5-m5-c000088 | 3 | 6 | 1.38608 | completed/correct | exact_single_candidate |
| d5-m5-c000089 | 5 | 4 | 1.53712 | completed/correct | exact_single_candidate |
| d5-m5-c000090 | 5 | 18 | 3.1971 | completed/correct | exact_single_candidate |
| d5-m5-c000091 | 5 | 15 | 2.64888 | completed/correct | exact_single_candidate |
| d5-m5-c000092 | 5 | 6 | 2.01527 | completed/correct | exact_single_candidate |
| d5-m5-c000093 | 3 | 2 | 0.840217 | completed/correct | exact_single_candidate |
| d5-m5-c000094 | 4 | 6 | 1.37125 | completed/correct | exact_single_candidate |
| d5-m5-c000095 | 5 | 6 | 1.98777 | completed/correct | exact_single_candidate |
| d5-m5-c000096 | 3 | 2 | 0.798331 | completed/correct | exact_single_candidate |
| d5-m5-c000097 | 4 | 4 | 1.16268 | completed/correct | exact_single_candidate |
| d5-m5-c000098 | 4 | 20 | 3.9645 | completed/correct | exact_single_candidate |
| d5-m5-c000099 | 4 | 16 | 3.36217 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `133061ab663f37931e551d101335a3f2ca668e458ad3b41e8d5cb1d72022c519`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
