# d5-a5-n100-h2-grid3-grid-plus-ratio-countdown-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
countdown, H2, Grid 3, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 8.76 | 876 |
| Queries, korrekte Lösungen | 100 | 8.76 | 876 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 8.76 | 876 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 1.82451 | 182.451 |
| API-Sekunden, korrekte Lösungen | 100 | 1.82451 | 182.451 |
| Controller-Sekunden, sämtliche Versuche | 100 | 2.46782 | 246.782 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000004, d5-m5-c000014, d5-m5-c000025, d5-m5-c000036, d5-m5-c000046, d5-m5-c000058, d5-m5-c000070

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000000 | 2 | 7 | 1.1249 | completed/correct | exact_single_candidate |
| d5-m5-c000001 | 5 | 8 | 1.96738 | completed/correct | exact_single_candidate |
| d5-m5-c000002 | 5 | 4 | 1.13684 | completed/correct | exact_single_candidate |
| d5-m5-c000003 | 3 | 4 | 1.26343 | completed/correct | exact_single_candidate |
| d5-m5-c000004 | 5 | 12 | 3.72311 | completed/correct | exact_single_candidate |
| d5-m5-c000005 | 5 | 11 | 2.07345 | completed/correct | exact_single_candidate |
| d5-m5-c000006 | 3 | 6 | 1.11214 | completed/correct | exact_single_candidate |
| d5-m5-c000007 | 5 | 2 | 1.0678 | completed/correct | exact_single_candidate |
| d5-m5-c000008 | 4 | 12 | 2.54144 | completed/correct | exact_single_candidate |
| d5-m5-c000009 | 5 | 4 | 1.42953 | completed/correct | exact_single_candidate |
| d5-m5-c000010 | 3 | 2 | 0.848263 | completed/correct | exact_single_candidate |
| d5-m5-c000011 | 5 | 8 | 2.08465 | completed/correct | exact_single_candidate |
| d5-m5-c000012 | 4 | 5 | 1.22914 | completed/correct | exact_single_candidate |
| d5-m5-c000013 | 3 | 14 | 1.83387 | completed/correct | exact_single_candidate |
| d5-m5-c000014 | 5 | 26 | 4.05523 | completed/correct | exact_single_candidate |
| d5-m5-c000015 | 5 | 4 | 1.19632 | completed/correct | exact_single_candidate |
| d5-m5-c000016 | 3 | 2 | 0.814949 | completed/correct | exact_single_candidate |
| d5-m5-c000017 | 4 | 4 | 1.03517 | completed/correct | exact_single_candidate |
| d5-m5-c000018 | 4 | 6 | 1.43756 | completed/correct | exact_single_candidate |
| d5-m5-c000019 | 4 | 4 | 1.10215 | completed/correct | exact_single_candidate |
| d5-m5-c000020 | 5 | 14 | 2.79083 | completed/correct | exact_single_candidate |
| d5-m5-c000021 | 5 | 12 | 2.09861 | completed/correct | exact_single_candidate |
| d5-m5-c000022 | 5 | 10 | 2.15329 | completed/correct | exact_single_candidate |
| d5-m5-c000023 | 5 | 4 | 1.37886 | completed/correct | exact_single_candidate |
| d5-m5-c000024 | 5 | 12 | 2.03565 | completed/correct | exact_single_candidate |
| d5-m5-c000025 | 5 | 29 | 4.59376 | completed/correct | exact_single_candidate |
| d5-m5-c000026 | 3 | 5 | 1.01246 | completed/correct | exact_single_candidate |
| d5-m5-c000027 | 4 | 4 | 1.04288 | completed/correct | exact_single_candidate |
| d5-m5-c000028 | 4 | 4 | 1.18985 | completed/correct | exact_single_candidate |
| d5-m5-c000029 | 4 | 9 | 1.52852 | completed/correct | exact_single_candidate |
| d5-m5-c000030 | 4 | 2 | 0.943053 | completed/correct | exact_single_candidate |
| d5-m5-c000031 | 4 | 4 | 1.16344 | completed/correct | exact_single_candidate |
| d5-m5-c000032 | 4 | 2 | 0.995734 | completed/correct | exact_single_candidate |
| d5-m5-c000033 | 3 | 2 | 0.831816 | completed/correct | exact_single_candidate |
| d5-m5-c000034 | 5 | 14 | 3.27776 | completed/correct | exact_single_candidate |
| d5-m5-c000035 | 4 | 6 | 1.21815 | completed/correct | exact_single_candidate |
| d5-m5-c000036 | 5 | 24 | 3.94543 | completed/correct | exact_single_candidate |
| d5-m5-c000037 | 4 | 8 | 1.45356 | completed/correct | exact_single_candidate |
| d5-m5-c000038 | 3 | 8 | 1.56736 | completed/correct | exact_single_candidate |
| d5-m5-c000039 | 5 | 8 | 2.09932 | completed/correct | exact_single_candidate |
| d5-m5-c000040 | 4 | 15 | 2.14412 | completed/correct | exact_single_candidate |
| d5-m5-c000041 | 4 | 4 | 1.11148 | completed/correct | exact_single_candidate |
| d5-m5-c000042 | 5 | 4 | 1.26028 | completed/correct | exact_single_candidate |
| d5-m5-c000043 | 5 | 4 | 1.24338 | completed/correct | exact_single_candidate |
| d5-m5-c000044 | 4 | 6 | 1.24133 | completed/correct | exact_single_candidate |
| d5-m5-c000045 | 4 | 2 | 0.929483 | completed/correct | exact_single_candidate |
| d5-m5-c000046 | 4 | 42 | 8.45557 | completed/correct | exact_single_candidate |
| d5-m5-c000047 | 4 | 8 | 2.08585 | completed/correct | exact_single_candidate |
| d5-m5-c000048 | 5 | 10 | 2.25235 | completed/correct | exact_single_candidate |
| d5-m5-c000049 | 3 | 6 | 1.15923 | completed/correct | exact_single_candidate |
| d5-m5-c000050 | 5 | 6 | 1.49594 | completed/correct | exact_single_candidate |
| d5-m5-c000051 | 5 | 8 | 1.85581 | completed/correct | exact_single_candidate |
| d5-m5-c000052 | 4 | 8 | 1.52386 | completed/correct | exact_single_candidate |
| d5-m5-c000053 | 5 | 8 | 1.62968 | completed/correct | exact_single_candidate |
| d5-m5-c000054 | 5 | 6 | 1.788 | completed/correct | exact_single_candidate |
| d5-m5-c000055 | 5 | 5 | 1.19466 | completed/correct | exact_single_candidate |
| d5-m5-c000056 | 3 | 5 | 0.974652 | completed/correct | exact_single_candidate |
| d5-m5-c000057 | 4 | 3 | 1.0042 | completed/correct | exact_single_candidate |
| d5-m5-c000058 | 5 | 26 | 5.92991 | completed/correct | exact_single_candidate |
| d5-m5-c000059 | 4 | 4 | 1.12915 | completed/correct | exact_single_candidate |
| d5-m5-c000060 | 5 | 6 | 1.51605 | completed/correct | exact_single_candidate |
| d5-m5-c000061 | 5 | 18 | 3.17707 | completed/correct | exact_single_candidate |
| d5-m5-c000062 | 4 | 6 | 1.31494 | completed/correct | exact_single_candidate |
| d5-m5-c000063 | 4 | 4 | 1.08041 | completed/correct | exact_single_candidate |
| d5-m5-c000064 | 3 | 5 | 1.04467 | completed/correct | exact_single_candidate |
| d5-m5-c000065 | 3 | 9 | 1.46341 | completed/correct | exact_single_candidate |
| d5-m5-c000066 | 5 | 8 | 1.70698 | completed/correct | exact_single_candidate |
| d5-m5-c000067 | 3 | 21 | 2.81987 | completed/correct | exact_single_candidate |
| d5-m5-c000068 | 4 | 2 | 1.0698 | completed/correct | exact_single_candidate |
| d5-m5-c000069 | 3 | 2 | 0.791377 | completed/correct | exact_single_candidate |
| d5-m5-c000070 | 4 | 43 | 7.33777 | completed/correct | exact_single_candidate |
| d5-m5-c000071 | 5 | 22 | 3.59117 | completed/correct | exact_single_candidate |
| d5-m5-c000072 | 5 | 4 | 1.2752 | completed/correct | exact_single_candidate |
| d5-m5-c000073 | 3 | 8 | 1.43386 | completed/correct | exact_single_candidate |
| d5-m5-c000074 | 3 | 6 | 1.07309 | completed/correct | exact_single_candidate |
| d5-m5-c000075 | 3 | 9 | 1.64836 | completed/correct | exact_single_candidate |
| d5-m5-c000076 | 3 | 2 | 0.824431 | completed/correct | exact_single_candidate |
| d5-m5-c000077 | 4 | 6 | 1.2322 | completed/correct | exact_single_candidate |
| d5-m5-c000078 | 3 | 16 | 2.71754 | completed/correct | exact_single_candidate |
| d5-m5-c000079 | 3 | 4 | 1.00908 | completed/correct | exact_single_candidate |
| d5-m5-c000080 | 4 | 8 | 1.46709 | completed/correct | exact_single_candidate |
| d5-m5-c000081 | 4 | 4 | 1.02099 | completed/correct | exact_single_candidate |
| d5-m5-c000082 | 4 | 4 | 1.08394 | completed/correct | exact_single_candidate |
| d5-m5-c000083 | 5 | 6 | 1.52603 | completed/correct | exact_single_candidate |
| d5-m5-c000084 | 4 | 16 | 2.38685 | completed/correct | exact_single_candidate |
| d5-m5-c000085 | 4 | 2 | 1.01272 | completed/correct | exact_single_candidate |
| d5-m5-c000086 | 3 | 2 | 0.891603 | completed/correct | exact_single_candidate |
| d5-m5-c000087 | 3 | 2 | 0.867346 | completed/correct | exact_single_candidate |
| d5-m5-c000088 | 3 | 6 | 1.11863 | completed/correct | exact_single_candidate |
| d5-m5-c000089 | 5 | 4 | 1.1936 | completed/correct | exact_single_candidate |
| d5-m5-c000090 | 5 | 24 | 3.48532 | completed/correct | exact_single_candidate |
| d5-m5-c000091 | 5 | 14 | 2.07644 | completed/correct | exact_single_candidate |
| d5-m5-c000092 | 5 | 14 | 2.66773 | completed/correct | exact_single_candidate |
| d5-m5-c000093 | 3 | 2 | 0.813845 | completed/correct | exact_single_candidate |
| d5-m5-c000094 | 4 | 15 | 2.34924 | completed/correct | exact_single_candidate |
| d5-m5-c000095 | 5 | 6 | 1.91866 | completed/correct | exact_single_candidate |
| d5-m5-c000096 | 3 | 2 | 0.779047 | completed/correct | exact_single_candidate |
| d5-m5-c000097 | 4 | 4 | 1.19343 | completed/correct | exact_single_candidate |
| d5-m5-c000098 | 4 | 20 | 2.99644 | completed/correct | exact_single_candidate |
| d5-m5-c000099 | 4 | 14 | 2.66819 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `133061ab663f37931e551d101335a3f2ca668e458ad3b41e8d5cb1d72022c519`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
