# d5-a5-n100-h2-grid10-grid-plus-ratio-countdown-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
countdown, H2, Grid 10, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 8.44 | 844 |
| Queries, korrekte Lösungen | 100 | 8.44 | 844 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 8.44 | 844 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 3.1634 | 316.34 |
| API-Sekunden, korrekte Lösungen | 100 | 3.1634 | 316.34 |
| Controller-Sekunden, sämtliche Versuche | 100 | 3.79788 | 379.788 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000014, d5-m5-c000025, d5-m5-c000036, d5-m5-c000046, d5-m5-c000058, d5-m5-c000070, d5-m5-c000071, d5-m5-c000078, d5-m5-c000090, d5-m5-c000098

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000000 | 2 | 10 | 2.22989 | completed/correct | exact_single_candidate |
| d5-m5-c000001 | 5 | 8 | 3.58118 | completed/correct | exact_single_candidate |
| d5-m5-c000002 | 5 | 4 | 1.86678 | completed/correct | exact_single_candidate |
| d5-m5-c000003 | 3 | 4 | 1.45995 | completed/correct | exact_single_candidate |
| d5-m5-c000004 | 5 | 8 | 4.66623 | completed/correct | exact_single_candidate |
| d5-m5-c000005 | 5 | 12 | 5.44801 | completed/correct | exact_single_candidate |
| d5-m5-c000006 | 3 | 6 | 1.89031 | completed/correct | exact_single_candidate |
| d5-m5-c000007 | 5 | 2 | 1.62196 | completed/correct | exact_single_candidate |
| d5-m5-c000008 | 4 | 12 | 4.59956 | completed/correct | exact_single_candidate |
| d5-m5-c000009 | 5 | 3 | 2.24568 | completed/correct | exact_single_candidate |
| d5-m5-c000010 | 3 | 2 | 1.12789 | completed/correct | exact_single_candidate |
| d5-m5-c000011 | 5 | 6 | 3.98003 | completed/correct | exact_single_candidate |
| d5-m5-c000012 | 4 | 6 | 1.93182 | completed/correct | exact_single_candidate |
| d5-m5-c000013 | 3 | 11 | 2.61455 | completed/correct | exact_single_candidate |
| d5-m5-c000014 | 5 | 30 | 9.15967 | completed/correct | exact_single_candidate |
| d5-m5-c000015 | 5 | 4 | 1.90874 | completed/correct | exact_single_candidate |
| d5-m5-c000016 | 3 | 2 | 1.03853 | completed/correct | exact_single_candidate |
| d5-m5-c000017 | 4 | 4 | 1.59663 | completed/correct | exact_single_candidate |
| d5-m5-c000018 | 4 | 6 | 1.97115 | completed/correct | exact_single_candidate |
| d5-m5-c000019 | 4 | 4 | 1.77046 | completed/correct | exact_single_candidate |
| d5-m5-c000020 | 5 | 12 | 4.77389 | completed/correct | exact_single_candidate |
| d5-m5-c000021 | 5 | 12 | 3.83852 | completed/correct | exact_single_candidate |
| d5-m5-c000022 | 5 | 8 | 3.67013 | completed/correct | exact_single_candidate |
| d5-m5-c000023 | 5 | 4 | 2.34146 | completed/correct | exact_single_candidate |
| d5-m5-c000024 | 5 | 11 | 3.72851 | completed/correct | exact_single_candidate |
| d5-m5-c000025 | 5 | 26 | 7.95791 | completed/correct | exact_single_candidate |
| d5-m5-c000026 | 3 | 4 | 1.2084 | completed/correct | exact_single_candidate |
| d5-m5-c000027 | 4 | 4 | 1.56692 | completed/correct | exact_single_candidate |
| d5-m5-c000028 | 4 | 4 | 1.94932 | completed/correct | exact_single_candidate |
| d5-m5-c000029 | 4 | 8 | 2.55758 | completed/correct | exact_single_candidate |
| d5-m5-c000030 | 4 | 2 | 1.37901 | completed/correct | exact_single_candidate |
| d5-m5-c000031 | 4 | 4 | 1.70287 | completed/correct | exact_single_candidate |
| d5-m5-c000032 | 4 | 2 | 1.4635 | completed/correct | exact_single_candidate |
| d5-m5-c000033 | 3 | 2 | 1.14118 | completed/correct | exact_single_candidate |
| d5-m5-c000034 | 5 | 10 | 5.04906 | completed/correct | exact_single_candidate |
| d5-m5-c000035 | 4 | 6 | 1.90908 | completed/correct | exact_single_candidate |
| d5-m5-c000036 | 5 | 30 | 10.0551 | completed/correct | exact_single_candidate |
| d5-m5-c000037 | 4 | 8 | 2.44404 | completed/correct | exact_single_candidate |
| d5-m5-c000038 | 3 | 8 | 2.84059 | completed/correct | exact_single_candidate |
| d5-m5-c000039 | 5 | 8 | 3.87779 | completed/correct | exact_single_candidate |
| d5-m5-c000040 | 4 | 12 | 3.65179 | completed/correct | exact_single_candidate |
| d5-m5-c000041 | 4 | 4 | 1.66367 | completed/correct | exact_single_candidate |
| d5-m5-c000042 | 5 | 4 | 1.8455 | completed/correct | exact_single_candidate |
| d5-m5-c000043 | 5 | 4 | 1.79497 | completed/correct | exact_single_candidate |
| d5-m5-c000044 | 4 | 10 | 3.2915 | completed/correct | exact_single_candidate |
| d5-m5-c000045 | 4 | 2 | 1.31049 | completed/correct | exact_single_candidate |
| d5-m5-c000046 | 4 | 36 | 13.8136 | completed/correct | exact_single_candidate |
| d5-m5-c000047 | 4 | 8 | 3.44038 | completed/correct | exact_single_candidate |
| d5-m5-c000048 | 5 | 12 | 4.74698 | completed/correct | exact_single_candidate |
| d5-m5-c000049 | 3 | 6 | 1.75079 | completed/correct | exact_single_candidate |
| d5-m5-c000050 | 5 | 6 | 2.45037 | completed/correct | exact_single_candidate |
| d5-m5-c000051 | 5 | 6 | 2.84979 | completed/correct | exact_single_candidate |
| d5-m5-c000052 | 4 | 6 | 1.79089 | completed/correct | exact_single_candidate |
| d5-m5-c000053 | 5 | 8 | 2.8192 | completed/correct | exact_single_candidate |
| d5-m5-c000054 | 5 | 6 | 2.37308 | completed/correct | exact_single_candidate |
| d5-m5-c000055 | 5 | 4 | 1.60407 | completed/correct | exact_single_candidate |
| d5-m5-c000056 | 3 | 5 | 1.44477 | completed/correct | exact_single_candidate |
| d5-m5-c000057 | 4 | 3 | 1.48282 | completed/correct | exact_single_candidate |
| d5-m5-c000058 | 5 | 18 | 8.4423 | completed/correct | exact_single_candidate |
| d5-m5-c000059 | 4 | 4 | 1.72795 | completed/correct | exact_single_candidate |
| d5-m5-c000060 | 5 | 10 | 3.5966 | completed/correct | exact_single_candidate |
| d5-m5-c000061 | 5 | 10 | 3.29854 | completed/correct | exact_single_candidate |
| d5-m5-c000062 | 4 | 6 | 2.09882 | completed/correct | exact_single_candidate |
| d5-m5-c000063 | 4 | 4 | 1.63724 | completed/correct | exact_single_candidate |
| d5-m5-c000064 | 3 | 6 | 1.79143 | completed/correct | exact_single_candidate |
| d5-m5-c000065 | 3 | 8 | 2.03815 | completed/correct | exact_single_candidate |
| d5-m5-c000066 | 5 | 8 | 2.92273 | completed/correct | exact_single_candidate |
| d5-m5-c000067 | 3 | 17 | 4.58825 | completed/correct | exact_single_candidate |
| d5-m5-c000068 | 4 | 2 | 1.36224 | completed/correct | exact_single_candidate |
| d5-m5-c000069 | 3 | 2 | 0.99739 | completed/correct | exact_single_candidate |
| d5-m5-c000070 | 4 | 54 | 18.6221 | completed/correct | exact_single_candidate |
| d5-m5-c000071 | 5 | 18 | 7.57634 | completed/correct | exact_single_candidate |
| d5-m5-c000072 | 5 | 4 | 2.02467 | completed/correct | exact_single_candidate |
| d5-m5-c000073 | 3 | 4 | 1.33693 | completed/correct | exact_single_candidate |
| d5-m5-c000074 | 3 | 4 | 1.22844 | completed/correct | exact_single_candidate |
| d5-m5-c000075 | 3 | 10 | 2.61592 | completed/correct | exact_single_candidate |
| d5-m5-c000076 | 3 | 2 | 1.09211 | completed/correct | exact_single_candidate |
| d5-m5-c000077 | 4 | 6 | 1.92257 | completed/correct | exact_single_candidate |
| d5-m5-c000078 | 3 | 18 | 7.05258 | completed/correct | exact_single_candidate |
| d5-m5-c000079 | 3 | 3 | 1.32999 | completed/correct | exact_single_candidate |
| d5-m5-c000080 | 4 | 6 | 1.93536 | completed/correct | exact_single_candidate |
| d5-m5-c000081 | 4 | 4 | 1.51774 | completed/correct | exact_single_candidate |
| d5-m5-c000082 | 4 | 4 | 1.69499 | completed/correct | exact_single_candidate |
| d5-m5-c000083 | 5 | 6 | 2.60126 | completed/correct | exact_single_candidate |
| d5-m5-c000084 | 4 | 12 | 5.01809 | completed/correct | exact_single_candidate |
| d5-m5-c000085 | 4 | 2 | 1.50448 | completed/correct | exact_single_candidate |
| d5-m5-c000086 | 3 | 2 | 1.24323 | completed/correct | exact_single_candidate |
| d5-m5-c000087 | 3 | 2 | 1.16213 | completed/correct | exact_single_candidate |
| d5-m5-c000088 | 3 | 4 | 1.38535 | completed/correct | exact_single_candidate |
| d5-m5-c000089 | 5 | 4 | 1.92523 | completed/correct | exact_single_candidate |
| d5-m5-c000090 | 5 | 24 | 7.09149 | completed/correct | exact_single_candidate |
| d5-m5-c000091 | 5 | 15 | 4.22693 | completed/correct | exact_single_candidate |
| d5-m5-c000092 | 5 | 16 | 5.80244 | completed/correct | exact_single_candidate |
| d5-m5-c000093 | 3 | 2 | 1.04416 | completed/correct | exact_single_candidate |
| d5-m5-c000094 | 4 | 14 | 3.92641 | completed/correct | exact_single_candidate |
| d5-m5-c000095 | 5 | 6 | 3.37398 | completed/correct | exact_single_candidate |
| d5-m5-c000096 | 3 | 2 | 0.985721 | completed/correct | exact_single_candidate |
| d5-m5-c000097 | 4 | 4 | 1.84222 | completed/correct | exact_single_candidate |
| d5-m5-c000098 | 4 | 24 | 7.92601 | completed/correct | exact_single_candidate |
| d5-m5-c000099 | 4 | 14 | 4.54106 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `133061ab663f37931e551d101335a3f2ca668e458ad3b41e8d5cb1d72022c519`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
