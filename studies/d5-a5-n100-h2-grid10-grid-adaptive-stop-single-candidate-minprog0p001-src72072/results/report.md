# d5-a5-n100-h2-grid10-grid-adaptive-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
adaptive, H2, Grid 10, Queryquelle grid, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 8.1 | 810 |
| Queries, korrekte Lösungen | 100 | 8.1 | 810 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 8.1 | 810 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 5.21412 | 521.412 |
| API-Sekunden, korrekte Lösungen | 100 | 5.21412 | 521.412 |
| Controller-Sekunden, sämtliche Versuche | 100 | 5.9027 | 590.27 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000036, d5-m5-c000046, d5-m5-c000070, d5-m5-c000078, d5-m5-c000090, d5-m5-c000098

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000000 | 2 | 8 | 3.45095 | completed/correct | exact_single_candidate |
| d5-m5-c000001 | 5 | 9 | 7.49803 | completed/correct | exact_single_candidate |
| d5-m5-c000002 | 5 | 5 | 2.99063 | completed/correct | exact_single_candidate |
| d5-m5-c000003 | 3 | 3 | 1.76601 | completed/correct | exact_single_candidate |
| d5-m5-c000004 | 5 | 7 | 9.40912 | completed/correct | exact_single_candidate |
| d5-m5-c000005 | 5 | 13 | 9.21751 | completed/correct | exact_single_candidate |
| d5-m5-c000006 | 3 | 6 | 2.93669 | completed/correct | exact_single_candidate |
| d5-m5-c000007 | 5 | 2 | 2.15055 | completed/correct | exact_single_candidate |
| d5-m5-c000008 | 4 | 10 | 7.49815 | completed/correct | exact_single_candidate |
| d5-m5-c000009 | 5 | 3 | 2.68895 | completed/correct | exact_single_candidate |
| d5-m5-c000010 | 3 | 2 | 1.52418 | completed/correct | exact_single_candidate |
| d5-m5-c000011 | 5 | 6 | 6.43412 | completed/correct | exact_single_candidate |
| d5-m5-c000012 | 4 | 5 | 3.50443 | completed/correct | exact_single_candidate |
| d5-m5-c000013 | 3 | 11 | 4.70868 | completed/correct | exact_single_candidate |
| d5-m5-c000014 | 5 | 15 | 9.99634 | completed/correct | exact_single_candidate |
| d5-m5-c000015 | 5 | 3 | 2.674 | completed/correct | exact_single_candidate |
| d5-m5-c000016 | 3 | 2 | 1.50101 | completed/correct | exact_single_candidate |
| d5-m5-c000017 | 4 | 3 | 2.16599 | completed/correct | exact_single_candidate |
| d5-m5-c000018 | 4 | 7 | 3.58512 | completed/correct | exact_single_candidate |
| d5-m5-c000019 | 4 | 7 | 5.2831 | completed/correct | exact_single_candidate |
| d5-m5-c000020 | 5 | 10 | 8.02488 | completed/correct | exact_single_candidate |
| d5-m5-c000021 | 5 | 12 | 6.61269 | completed/correct | exact_single_candidate |
| d5-m5-c000022 | 5 | 11 | 8.22964 | completed/correct | exact_single_candidate |
| d5-m5-c000023 | 5 | 4 | 3.73429 | completed/correct | exact_single_candidate |
| d5-m5-c000024 | 5 | 11 | 5.99356 | completed/correct | exact_single_candidate |
| d5-m5-c000025 | 5 | 19 | 10.5369 | completed/correct | exact_single_candidate |
| d5-m5-c000026 | 3 | 4 | 1.99715 | completed/correct | exact_single_candidate |
| d5-m5-c000027 | 4 | 4 | 2.54681 | completed/correct | exact_single_candidate |
| d5-m5-c000028 | 4 | 4 | 2.9556 | completed/correct | exact_single_candidate |
| d5-m5-c000029 | 4 | 7 | 3.22882 | completed/correct | exact_single_candidate |
| d5-m5-c000030 | 4 | 3 | 1.87693 | completed/correct | exact_single_candidate |
| d5-m5-c000031 | 4 | 8 | 3.94448 | completed/correct | exact_single_candidate |
| d5-m5-c000032 | 4 | 2 | 1.6729 | completed/correct | exact_single_candidate |
| d5-m5-c000033 | 3 | 2 | 1.49334 | completed/correct | exact_single_candidate |
| d5-m5-c000034 | 5 | 9 | 5.9024 | completed/correct | exact_single_candidate |
| d5-m5-c000035 | 4 | 6 | 2.98528 | completed/correct | exact_single_candidate |
| d5-m5-c000036 | 5 | 26 | 16.6822 | completed/correct | exact_single_candidate |
| d5-m5-c000037 | 4 | 7 | 4.00165 | completed/correct | exact_single_candidate |
| d5-m5-c000038 | 3 | 8 | 5.41213 | completed/correct | exact_single_candidate |
| d5-m5-c000039 | 5 | 10 | 7.27558 | completed/correct | exact_single_candidate |
| d5-m5-c000040 | 4 | 11 | 6.10313 | completed/correct | exact_single_candidate |
| d5-m5-c000041 | 4 | 3 | 2.06179 | completed/correct | exact_single_candidate |
| d5-m5-c000042 | 5 | 4 | 2.65053 | completed/correct | exact_single_candidate |
| d5-m5-c000043 | 5 | 4 | 2.58606 | completed/correct | exact_single_candidate |
| d5-m5-c000044 | 4 | 6 | 3.46956 | completed/correct | exact_single_candidate |
| d5-m5-c000045 | 4 | 2 | 1.64971 | completed/correct | exact_single_candidate |
| d5-m5-c000046 | 4 | 43 | 30.6277 | completed/correct | exact_single_candidate |
| d5-m5-c000047 | 4 | 6 | 4.9228 | completed/correct | exact_single_candidate |
| d5-m5-c000048 | 5 | 6 | 4.99137 | completed/correct | exact_single_candidate |
| d5-m5-c000049 | 3 | 9 | 4.75804 | completed/correct | exact_single_candidate |
| d5-m5-c000050 | 5 | 6 | 4.10626 | completed/correct | exact_single_candidate |
| d5-m5-c000051 | 5 | 11 | 8.83056 | completed/correct | exact_single_candidate |
| d5-m5-c000052 | 4 | 6 | 3.2833 | completed/correct | exact_single_candidate |
| d5-m5-c000053 | 5 | 7 | 4.17646 | completed/correct | exact_single_candidate |
| d5-m5-c000054 | 5 | 6 | 4.48547 | completed/correct | exact_single_candidate |
| d5-m5-c000055 | 5 | 5 | 3.03957 | completed/correct | exact_single_candidate |
| d5-m5-c000056 | 3 | 5 | 2.11484 | completed/correct | exact_single_candidate |
| d5-m5-c000057 | 4 | 3 | 1.9698 | completed/correct | exact_single_candidate |
| d5-m5-c000058 | 5 | 17 | 11.6039 | completed/correct | exact_single_candidate |
| d5-m5-c000059 | 4 | 4 | 2.58182 | completed/correct | exact_single_candidate |
| d5-m5-c000060 | 5 | 14 | 8.19855 | completed/correct | exact_single_candidate |
| d5-m5-c000061 | 5 | 9 | 5.44817 | completed/correct | exact_single_candidate |
| d5-m5-c000062 | 4 | 5 | 3.02645 | completed/correct | exact_single_candidate |
| d5-m5-c000063 | 4 | 3 | 1.92634 | completed/correct | exact_single_candidate |
| d5-m5-c000064 | 3 | 6 | 2.49552 | completed/correct | exact_single_candidate |
| d5-m5-c000065 | 3 | 6 | 2.79075 | completed/correct | exact_single_candidate |
| d5-m5-c000066 | 5 | 5 | 3.00002 | completed/correct | exact_single_candidate |
| d5-m5-c000067 | 3 | 17 | 9.0938 | completed/correct | exact_single_candidate |
| d5-m5-c000068 | 4 | 4 | 3.08999 | completed/correct | exact_single_candidate |
| d5-m5-c000069 | 3 | 3 | 1.67093 | completed/correct | exact_single_candidate |
| d5-m5-c000070 | 4 | 47 | 28.5784 | completed/correct | exact_single_candidate |
| d5-m5-c000071 | 5 | 14 | 10.8818 | completed/correct | exact_single_candidate |
| d5-m5-c000072 | 5 | 5 | 3.18251 | completed/correct | exact_single_candidate |
| d5-m5-c000073 | 3 | 3 | 1.733 | completed/correct | exact_single_candidate |
| d5-m5-c000074 | 3 | 4 | 1.9876 | completed/correct | exact_single_candidate |
| d5-m5-c000075 | 3 | 8 | 3.59593 | completed/correct | exact_single_candidate |
| d5-m5-c000076 | 3 | 2 | 1.42242 | completed/correct | exact_single_candidate |
| d5-m5-c000077 | 4 | 5 | 3.026 | completed/correct | exact_single_candidate |
| d5-m5-c000078 | 3 | 17 | 12.9639 | completed/correct | exact_single_candidate |
| d5-m5-c000079 | 3 | 4 | 2.14896 | completed/correct | exact_single_candidate |
| d5-m5-c000080 | 4 | 7 | 3.66233 | completed/correct | exact_single_candidate |
| d5-m5-c000081 | 4 | 6 | 3.37134 | completed/correct | exact_single_candidate |
| d5-m5-c000082 | 4 | 6 | 3.97887 | completed/correct | exact_single_candidate |
| d5-m5-c000083 | 5 | 5 | 3.33474 | completed/correct | exact_single_candidate |
| d5-m5-c000084 | 4 | 12 | 9.07848 | completed/correct | exact_single_candidate |
| d5-m5-c000085 | 4 | 2 | 1.68405 | completed/correct | exact_single_candidate |
| d5-m5-c000086 | 3 | 2 | 1.55353 | completed/correct | exact_single_candidate |
| d5-m5-c000087 | 3 | 1 | 1.20809 | completed/correct | exact_single_candidate |
| d5-m5-c000088 | 3 | 8 | 4.21904 | completed/correct | exact_single_candidate |
| d5-m5-c000089 | 5 | 4 | 3.08229 | completed/correct | exact_single_candidate |
| d5-m5-c000090 | 5 | 24 | 12.6094 | completed/correct | exact_single_candidate |
| d5-m5-c000091 | 5 | 14 | 6.68717 | completed/correct | exact_single_candidate |
| d5-m5-c000092 | 5 | 7 | 5.28147 | completed/correct | exact_single_candidate |
| d5-m5-c000093 | 3 | 3 | 1.80372 | completed/correct | exact_single_candidate |
| d5-m5-c000094 | 4 | 12 | 5.93683 | completed/correct | exact_single_candidate |
| d5-m5-c000095 | 5 | 7 | 7.41829 | completed/correct | exact_single_candidate |
| d5-m5-c000096 | 3 | 3 | 1.70944 | completed/correct | exact_single_candidate |
| d5-m5-c000097 | 4 | 4 | 2.98701 | completed/correct | exact_single_candidate |
| d5-m5-c000098 | 4 | 28 | 16.9849 | completed/correct | exact_single_candidate |
| d5-m5-c000099 | 4 | 16 | 8.45697 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `133061ab663f37931e551d101335a3f2ca668e458ad3b41e8d5cb1d72022c519`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
