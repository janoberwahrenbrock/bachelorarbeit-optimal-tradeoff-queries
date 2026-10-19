# d5-a5-n100-h2-grid10-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
receding, H2, Grid 10, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 11.87 | 1187 |
| Queries, korrekte Lösungen | 100 | 11.87 | 1187 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 11.87 | 1187 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 7.58807 | 758.807 |
| API-Sekunden, korrekte Lösungen | 100 | 7.58807 | 758.807 |
| Controller-Sekunden, sämtliche Versuche | 100 | 8.26663 | 826.663 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000024, d5-m5-c000034, d5-m5-c000038, d5-m5-c000046, d5-m5-c000058, d5-m5-c000070, d5-m5-c000078

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000000 | 2 | 9 | 4.15263 | completed/correct | exact_single_candidate |
| d5-m5-c000001 | 5 | 9 | 7.35068 | completed/correct | exact_single_candidate |
| d5-m5-c000002 | 5 | 6 | 3.682 | completed/correct | exact_single_candidate |
| d5-m5-c000003 | 3 | 5 | 2.90276 | completed/correct | exact_single_candidate |
| d5-m5-c000004 | 5 | 9 | 10.9709 | completed/correct | exact_single_candidate |
| d5-m5-c000005 | 5 | 10 | 6.80883 | completed/correct | exact_single_candidate |
| d5-m5-c000006 | 3 | 8 | 3.93083 | completed/correct | exact_single_candidate |
| d5-m5-c000007 | 5 | 4 | 2.91422 | completed/correct | exact_single_candidate |
| d5-m5-c000008 | 4 | 16 | 9.81293 | completed/correct | exact_single_candidate |
| d5-m5-c000009 | 5 | 3 | 3.11098 | completed/correct | exact_single_candidate |
| d5-m5-c000010 | 3 | 19 | 10.1375 | completed/correct | exact_single_candidate |
| d5-m5-c000011 | 5 | 9 | 8.02715 | completed/correct | exact_single_candidate |
| d5-m5-c000012 | 4 | 7 | 3.9158 | completed/correct | exact_single_candidate |
| d5-m5-c000013 | 3 | 7 | 3.59662 | completed/correct | exact_single_candidate |
| d5-m5-c000014 | 5 | 22 | 12.9586 | completed/correct | exact_single_candidate |
| d5-m5-c000015 | 5 | 5 | 3.71712 | completed/correct | exact_single_candidate |
| d5-m5-c000016 | 3 | 2 | 1.33578 | completed/correct | exact_single_candidate |
| d5-m5-c000017 | 4 | 4 | 2.58915 | completed/correct | exact_single_candidate |
| d5-m5-c000018 | 4 | 7 | 4.53188 | completed/correct | exact_single_candidate |
| d5-m5-c000019 | 4 | 12 | 7.14249 | completed/correct | exact_single_candidate |
| d5-m5-c000020 | 5 | 12 | 9.93364 | completed/correct | exact_single_candidate |
| d5-m5-c000021 | 5 | 10 | 6.2788 | completed/correct | exact_single_candidate |
| d5-m5-c000022 | 5 | 7 | 6.09504 | completed/correct | exact_single_candidate |
| d5-m5-c000023 | 5 | 6 | 4.68741 | completed/correct | exact_single_candidate |
| d5-m5-c000024 | 5 | 42 | 26.5139 | completed/correct | exact_single_candidate |
| d5-m5-c000025 | 5 | 24 | 13.1849 | completed/correct | exact_single_candidate |
| d5-m5-c000026 | 3 | 16 | 8.12815 | completed/correct | exact_single_candidate |
| d5-m5-c000027 | 4 | 16 | 9.21253 | completed/correct | exact_single_candidate |
| d5-m5-c000028 | 4 | 5 | 3.42704 | completed/correct | exact_single_candidate |
| d5-m5-c000029 | 4 | 9 | 4.46111 | completed/correct | exact_single_candidate |
| d5-m5-c000030 | 4 | 4 | 2.40287 | completed/correct | exact_single_candidate |
| d5-m5-c000031 | 4 | 23 | 13.5407 | completed/correct | exact_single_candidate |
| d5-m5-c000032 | 4 | 2 | 1.73777 | completed/correct | exact_single_candidate |
| d5-m5-c000033 | 3 | 17 | 9.479 | completed/correct | exact_single_candidate |
| d5-m5-c000034 | 5 | 24 | 19.0085 | completed/correct | exact_single_candidate |
| d5-m5-c000035 | 4 | 12 | 6.14344 | completed/correct | exact_single_candidate |
| d5-m5-c000036 | 5 | 24 | 15.7236 | completed/correct | exact_single_candidate |
| d5-m5-c000037 | 4 | 16 | 8.99365 | completed/correct | exact_single_candidate |
| d5-m5-c000038 | 3 | 31 | 18.4679 | completed/correct | exact_single_candidate |
| d5-m5-c000039 | 5 | 7 | 5.89036 | completed/correct | exact_single_candidate |
| d5-m5-c000040 | 4 | 12 | 6.58787 | completed/correct | exact_single_candidate |
| d5-m5-c000041 | 4 | 19 | 10.6028 | completed/correct | exact_single_candidate |
| d5-m5-c000042 | 5 | 7 | 4.45392 | completed/correct | exact_single_candidate |
| d5-m5-c000043 | 5 | 8 | 4.73385 | completed/correct | exact_single_candidate |
| d5-m5-c000044 | 4 | 6 | 3.92379 | completed/correct | exact_single_candidate |
| d5-m5-c000045 | 4 | 2 | 1.56637 | completed/correct | exact_single_candidate |
| d5-m5-c000046 | 4 | 38 | 29.5131 | completed/correct | exact_single_candidate |
| d5-m5-c000047 | 4 | 10 | 7.09212 | completed/correct | exact_single_candidate |
| d5-m5-c000048 | 5 | 18 | 14.2205 | completed/correct | exact_single_candidate |
| d5-m5-c000049 | 3 | 9 | 4.78744 | completed/correct | exact_single_candidate |
| d5-m5-c000050 | 5 | 5 | 3.97766 | completed/correct | exact_single_candidate |
| d5-m5-c000051 | 5 | 14 | 8.61996 | completed/correct | exact_single_candidate |
| d5-m5-c000052 | 4 | 15 | 9.29242 | completed/correct | exact_single_candidate |
| d5-m5-c000053 | 5 | 21 | 13.7762 | completed/correct | exact_single_candidate |
| d5-m5-c000054 | 5 | 11 | 6.80206 | completed/correct | exact_single_candidate |
| d5-m5-c000055 | 5 | 6 | 3.08489 | completed/correct | exact_single_candidate |
| d5-m5-c000056 | 3 | 20 | 10.7552 | completed/correct | exact_single_candidate |
| d5-m5-c000057 | 4 | 3 | 1.89841 | completed/correct | exact_single_candidate |
| d5-m5-c000058 | 5 | 24 | 19.827 | completed/correct | exact_single_candidate |
| d5-m5-c000059 | 4 | 13 | 7.22421 | completed/correct | exact_single_candidate |
| d5-m5-c000060 | 5 | 12 | 9.45486 | completed/correct | exact_single_candidate |
| d5-m5-c000061 | 5 | 13 | 8.1822 | completed/correct | exact_single_candidate |
| d5-m5-c000062 | 4 | 9 | 4.91872 | completed/correct | exact_single_candidate |
| d5-m5-c000063 | 4 | 7 | 3.99122 | completed/correct | exact_single_candidate |
| d5-m5-c000064 | 3 | 19 | 9.46494 | completed/correct | exact_single_candidate |
| d5-m5-c000065 | 3 | 14 | 6.89364 | completed/correct | exact_single_candidate |
| d5-m5-c000066 | 5 | 8 | 5.10205 | completed/correct | exact_single_candidate |
| d5-m5-c000067 | 3 | 15 | 8.03386 | completed/correct | exact_single_candidate |
| d5-m5-c000068 | 4 | 5 | 3.32508 | completed/correct | exact_single_candidate |
| d5-m5-c000069 | 3 | 3 | 1.6059 | completed/correct | exact_single_candidate |
| d5-m5-c000070 | 4 | 37 | 26.1725 | completed/correct | exact_single_candidate |
| d5-m5-c000071 | 5 | 18 | 13.9195 | completed/correct | exact_single_candidate |
| d5-m5-c000072 | 5 | 6 | 4.4255 | completed/correct | exact_single_candidate |
| d5-m5-c000073 | 3 | 3 | 1.84733 | completed/correct | exact_single_candidate |
| d5-m5-c000074 | 3 | 3 | 1.59749 | completed/correct | exact_single_candidate |
| d5-m5-c000075 | 3 | 6 | 2.67815 | completed/correct | exact_single_candidate |
| d5-m5-c000076 | 3 | 2 | 1.33699 | completed/correct | exact_single_candidate |
| d5-m5-c000077 | 4 | 7 | 4.45718 | completed/correct | exact_single_candidate |
| d5-m5-c000078 | 3 | 28 | 18.7491 | completed/correct | exact_single_candidate |
| d5-m5-c000079 | 3 | 6 | 3.08973 | completed/correct | exact_single_candidate |
| d5-m5-c000080 | 4 | 11 | 5.90761 | completed/correct | exact_single_candidate |
| d5-m5-c000081 | 4 | 10 | 4.61576 | completed/correct | exact_single_candidate |
| d5-m5-c000082 | 4 | 6 | 3.92359 | completed/correct | exact_single_candidate |
| d5-m5-c000083 | 5 | 5 | 3.40763 | completed/correct | exact_single_candidate |
| d5-m5-c000084 | 4 | 19 | 13.4608 | completed/correct | exact_single_candidate |
| d5-m5-c000085 | 4 | 3 | 2.16925 | completed/correct | exact_single_candidate |
| d5-m5-c000086 | 3 | 2 | 1.5066 | completed/correct | exact_single_candidate |
| d5-m5-c000087 | 3 | 2 | 1.58178 | completed/correct | exact_single_candidate |
| d5-m5-c000088 | 3 | 12 | 7.15713 | completed/correct | exact_single_candidate |
| d5-m5-c000089 | 5 | 6 | 3.91068 | completed/correct | exact_single_candidate |
| d5-m5-c000090 | 5 | 27 | 13.3275 | completed/correct | exact_single_candidate |
| d5-m5-c000091 | 5 | 12 | 7.30237 | completed/correct | exact_single_candidate |
| d5-m5-c000092 | 5 | 11 | 8.01946 | completed/correct | exact_single_candidate |
| d5-m5-c000093 | 3 | 2 | 1.32806 | completed/correct | exact_single_candidate |
| d5-m5-c000094 | 4 | 26 | 17.2862 | completed/correct | exact_single_candidate |
| d5-m5-c000095 | 5 | 12 | 8.9397 | completed/correct | exact_single_candidate |
| d5-m5-c000096 | 3 | 18 | 8.56195 | completed/correct | exact_single_candidate |
| d5-m5-c000097 | 4 | 8 | 6.48495 | completed/correct | exact_single_candidate |
| d5-m5-c000098 | 4 | 20 | 13.265 | completed/correct | exact_single_candidate |
| d5-m5-c000099 | 4 | 13 | 7.7661 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `133061ab663f37931e551d101335a3f2ca668e458ad3b41e8d5cb1d72022c519`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
