# d5-a20-n100-h2-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
adaptive, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 10.71 | 1071 |
| Queries, korrekte Lösungen | 100 | 10.71 | 1071 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 10.71 | 1071 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 10.4503 | 1045.03 |
| API-Sekunden, korrekte Lösungen | 100 | 10.4503 | 1045.03 |
| Controller-Sekunden, sämtliche Versuche | 100 | 11.1958 | 1119.58 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m20-c000000, d5-m20-c000048, d5-m20-c000054, d5-m20-c000063

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m20-c000000 | 12 | 14 | 24.4195 | completed/correct | exact_single_candidate |
| d5-m20-c000001 | 11 | 10 | 15.7299 | completed/correct | exact_single_candidate |
| d5-m20-c000002 | 12 | 7 | 6.16487 | completed/correct | exact_single_candidate |
| d5-m20-c000003 | 12 | 6 | 8.44828 | completed/correct | exact_single_candidate |
| d5-m20-c000004 | 8 | 6 | 4.28959 | completed/correct | exact_single_candidate |
| d5-m20-c000005 | 14 | 9 | 13.8692 | completed/correct | exact_single_candidate |
| d5-m20-c000006 | 12 | 16 | 11.514 | completed/correct | exact_single_candidate |
| d5-m20-c000007 | 14 | 6 | 10.9494 | completed/correct | exact_single_candidate |
| d5-m20-c000008 | 11 | 10 | 8.11242 | completed/correct | exact_single_candidate |
| d5-m20-c000009 | 10 | 6 | 6.51705 | completed/correct | exact_single_candidate |
| d5-m20-c000010 | 12 | 15 | 10.9031 | completed/correct | exact_single_candidate |
| d5-m20-c000011 | 6 | 7 | 4.02834 | completed/correct | exact_single_candidate |
| d5-m20-c000012 | 11 | 7 | 9.98311 | completed/correct | exact_single_candidate |
| d5-m20-c000013 | 13 | 15 | 13.6963 | completed/correct | exact_single_candidate |
| d5-m20-c000014 | 15 | 20 | 19.1578 | completed/correct | exact_single_candidate |
| d5-m20-c000015 | 8 | 5 | 6.16826 | completed/correct | exact_single_candidate |
| d5-m20-c000016 | 10 | 22 | 11.0322 | completed/correct | exact_single_candidate |
| d5-m20-c000017 | 9 | 5 | 4.37541 | completed/correct | exact_single_candidate |
| d5-m20-c000018 | 10 | 9 | 7.77675 | completed/correct | exact_single_candidate |
| d5-m20-c000019 | 8 | 16 | 9.43345 | completed/correct | exact_single_candidate |
| d5-m20-c000020 | 7 | 4 | 2.80423 | completed/correct | exact_single_candidate |
| d5-m20-c000021 | 12 | 10 | 11.3728 | completed/correct | exact_single_candidate |
| d5-m20-c000022 | 9 | 12 | 8.72081 | completed/correct | exact_single_candidate |
| d5-m20-c000023 | 7 | 8 | 4.4736 | completed/correct | exact_single_candidate |
| d5-m20-c000024 | 10 | 10 | 18.1175 | completed/correct | exact_single_candidate |
| d5-m20-c000025 | 4 | 3 | 1.52179 | completed/correct | exact_single_candidate |
| d5-m20-c000026 | 11 | 6 | 6.42504 | completed/correct | exact_single_candidate |
| d5-m20-c000027 | 12 | 7 | 6.99091 | completed/correct | exact_single_candidate |
| d5-m20-c000028 | 6 | 33 | 13.8558 | completed/correct | exact_single_candidate |
| d5-m20-c000029 | 9 | 7 | 4.11184 | completed/correct | exact_single_candidate |
| d5-m20-c000030 | 13 | 6 | 10.8193 | completed/correct | exact_single_candidate |
| d5-m20-c000031 | 7 | 3 | 2.27888 | completed/correct | exact_single_candidate |
| d5-m20-c000032 | 9 | 13 | 8.97534 | completed/correct | exact_single_candidate |
| d5-m20-c000033 | 11 | 8 | 8.63933 | completed/correct | exact_single_candidate |
| d5-m20-c000034 | 13 | 6 | 7.27384 | completed/correct | exact_single_candidate |
| d5-m20-c000035 | 11 | 13 | 13.3729 | completed/correct | exact_single_candidate |
| d5-m20-c000036 | 14 | 16 | 15.4131 | completed/correct | exact_single_candidate |
| d5-m20-c000037 | 14 | 11 | 15.5782 | completed/correct | exact_single_candidate |
| d5-m20-c000038 | 13 | 6 | 9.26127 | completed/correct | exact_single_candidate |
| d5-m20-c000039 | 11 | 25 | 15.0373 | completed/correct | exact_single_candidate |
| d5-m20-c000040 | 16 | 5 | 13.5157 | completed/correct | exact_single_candidate |
| d5-m20-c000041 | 11 | 6 | 5.20027 | completed/correct | exact_single_candidate |
| d5-m20-c000042 | 10 | 5 | 5.46109 | completed/correct | exact_single_candidate |
| d5-m20-c000043 | 9 | 6 | 5.14016 | completed/correct | exact_single_candidate |
| d5-m20-c000044 | 12 | 12 | 14.1263 | completed/correct | exact_single_candidate |
| d5-m20-c000045 | 10 | 5 | 4.28342 | completed/correct | exact_single_candidate |
| d5-m20-c000046 | 14 | 9 | 20.552 | completed/correct | exact_single_candidate |
| d5-m20-c000047 | 11 | 8 | 15.2084 | completed/correct | exact_single_candidate |
| d5-m20-c000048 | 12 | 12 | 24.8667 | completed/correct | exact_single_candidate |
| d5-m20-c000049 | 13 | 16 | 17.5171 | completed/correct | exact_single_candidate |
| d5-m20-c000050 | 13 | 8 | 10.6472 | completed/correct | exact_single_candidate |
| d5-m20-c000051 | 11 | 13 | 10.2643 | completed/correct | exact_single_candidate |
| d5-m20-c000052 | 8 | 11 | 11.1901 | completed/correct | exact_single_candidate |
| d5-m20-c000053 | 15 | 12 | 19.3307 | completed/correct | exact_single_candidate |
| d5-m20-c000054 | 11 | 39 | 32.9066 | completed/correct | exact_single_candidate |
| d5-m20-c000055 | 11 | 8 | 7.5296 | completed/correct | exact_single_candidate |
| d5-m20-c000056 | 10 | 7 | 5.67158 | completed/correct | exact_single_candidate |
| d5-m20-c000057 | 8 | 14 | 7.34495 | completed/correct | exact_single_candidate |
| d5-m20-c000058 | 8 | 3 | 3.05028 | completed/correct | exact_single_candidate |
| d5-m20-c000059 | 10 | 11 | 13.4889 | completed/correct | exact_single_candidate |
| d5-m20-c000060 | 12 | 7 | 7.44161 | completed/correct | exact_single_candidate |
| d5-m20-c000061 | 10 | 7 | 6.57264 | completed/correct | exact_single_candidate |
| d5-m20-c000062 | 12 | 8 | 12.2158 | completed/correct | exact_single_candidate |
| d5-m20-c000063 | 11 | 27 | 24.9147 | completed/correct | exact_single_candidate |
| d5-m20-c000064 | 10 | 12 | 7.6251 | completed/correct | exact_single_candidate |
| d5-m20-c000065 | 12 | 8 | 10.9499 | completed/correct | exact_single_candidate |
| d5-m20-c000066 | 8 | 11 | 7.13909 | completed/correct | exact_single_candidate |
| d5-m20-c000067 | 9 | 12 | 9.92016 | completed/correct | exact_single_candidate |
| d5-m20-c000068 | 7 | 14 | 6.4865 | completed/correct | exact_single_candidate |
| d5-m20-c000069 | 9 | 8 | 5.80562 | completed/correct | exact_single_candidate |
| d5-m20-c000070 | 13 | 10 | 16.1647 | completed/correct | exact_single_candidate |
| d5-m20-c000071 | 14 | 13 | 16.7782 | completed/correct | exact_single_candidate |
| d5-m20-c000072 | 13 | 7 | 8.57066 | completed/correct | exact_single_candidate |
| d5-m20-c000073 | 10 | 9 | 11.0484 | completed/correct | exact_single_candidate |
| d5-m20-c000074 | 12 | 6 | 10.5546 | completed/correct | exact_single_candidate |
| d5-m20-c000075 | 9 | 11 | 5.78526 | completed/correct | exact_single_candidate |
| d5-m20-c000076 | 11 | 6 | 6.9058 | completed/correct | exact_single_candidate |
| d5-m20-c000077 | 8 | 6 | 4.69737 | completed/correct | exact_single_candidate |
| d5-m20-c000078 | 9 | 6 | 4.87692 | completed/correct | exact_single_candidate |
| d5-m20-c000079 | 10 | 4 | 5.32755 | completed/correct | exact_single_candidate |
| d5-m20-c000080 | 10 | 14 | 12.6918 | completed/correct | exact_single_candidate |
| d5-m20-c000081 | 9 | 9 | 6.86356 | completed/correct | exact_single_candidate |
| d5-m20-c000082 | 13 | 7 | 9.05955 | completed/correct | exact_single_candidate |
| d5-m20-c000083 | 9 | 20 | 11.2879 | completed/correct | exact_single_candidate |
| d5-m20-c000084 | 12 | 14 | 13.2125 | completed/correct | exact_single_candidate |
| d5-m20-c000085 | 8 | 2 | 2.53718 | completed/correct | exact_single_candidate |
| d5-m20-c000086 | 16 | 24 | 21.8175 | completed/correct | exact_single_candidate |
| d5-m20-c000087 | 14 | 14 | 16.9881 | completed/correct | exact_single_candidate |
| d5-m20-c000088 | 11 | 8 | 7.20431 | completed/correct | exact_single_candidate |
| d5-m20-c000089 | 9 | 7 | 5.28537 | completed/correct | exact_single_candidate |
| d5-m20-c000090 | 11 | 14 | 9.55307 | completed/correct | exact_single_candidate |
| d5-m20-c000091 | 12 | 9 | 12.2008 | completed/correct | exact_single_candidate |
| d5-m20-c000092 | 8 | 18 | 12.1195 | completed/correct | exact_single_candidate |
| d5-m20-c000093 | 10 | 6 | 6.11926 | completed/correct | exact_single_candidate |
| d5-m20-c000094 | 11 | 6 | 6.37008 | completed/correct | exact_single_candidate |
| d5-m20-c000095 | 11 | 36 | 22.2936 | completed/correct | exact_single_candidate |
| d5-m20-c000096 | 10 | 7 | 6.88888 | completed/correct | exact_single_candidate |
| d5-m20-c000097 | 9 | 14 | 13.7669 | completed/correct | exact_single_candidate |
| d5-m20-c000098 | 11 | 11 | 11.1961 | completed/correct | exact_single_candidate |
| d5-m20-c000099 | 11 | 11 | 8.88362 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `bab6e260f0d2d94473a54a431ded8e8cdc6ea5f0f12781a293e6c3ed1a09a973`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
