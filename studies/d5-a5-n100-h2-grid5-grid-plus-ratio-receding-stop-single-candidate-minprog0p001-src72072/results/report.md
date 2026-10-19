# d5-a5-n100-h2-grid5-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
receding, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 11.63 | 1163 |
| Queries, korrekte Lösungen | 100 | 11.63 | 1163 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 11.63 | 1163 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 4.65968 | 465.968 |
| API-Sekunden, korrekte Lösungen | 100 | 4.65968 | 465.968 |
| Controller-Sekunden, sämtliche Versuche | 100 | 5.33591 | 533.591 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000024, d5-m5-c000036, d5-m5-c000046, d5-m5-c000070

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000000 | 2 | 11 | 2.66639 | completed/correct | exact_single_candidate |
| d5-m5-c000001 | 5 | 14 | 6.9029 | completed/correct | exact_single_candidate |
| d5-m5-c000002 | 5 | 6 | 2.33048 | completed/correct | exact_single_candidate |
| d5-m5-c000003 | 3 | 5 | 1.85757 | completed/correct | exact_single_candidate |
| d5-m5-c000004 | 5 | 17 | 10.4069 | completed/correct | exact_single_candidate |
| d5-m5-c000005 | 5 | 20 | 6.8869 | completed/correct | exact_single_candidate |
| d5-m5-c000006 | 3 | 13 | 4.89249 | completed/correct | exact_single_candidate |
| d5-m5-c000007 | 5 | 4 | 1.91336 | completed/correct | exact_single_candidate |
| d5-m5-c000008 | 4 | 14 | 5.33477 | completed/correct | exact_single_candidate |
| d5-m5-c000009 | 5 | 3 | 2.12728 | completed/correct | exact_single_candidate |
| d5-m5-c000010 | 3 | 13 | 4.10369 | completed/correct | exact_single_candidate |
| d5-m5-c000011 | 5 | 10 | 4.2987 | completed/correct | exact_single_candidate |
| d5-m5-c000012 | 4 | 4 | 1.87277 | completed/correct | exact_single_candidate |
| d5-m5-c000013 | 3 | 6 | 2.00982 | completed/correct | exact_single_candidate |
| d5-m5-c000014 | 5 | 21 | 7.31067 | completed/correct | exact_single_candidate |
| d5-m5-c000015 | 5 | 5 | 2.29888 | completed/correct | exact_single_candidate |
| d5-m5-c000016 | 3 | 2 | 1.06821 | completed/correct | exact_single_candidate |
| d5-m5-c000017 | 4 | 4 | 1.69229 | completed/correct | exact_single_candidate |
| d5-m5-c000018 | 4 | 16 | 6.20172 | completed/correct | exact_single_candidate |
| d5-m5-c000019 | 4 | 8 | 2.9981 | completed/correct | exact_single_candidate |
| d5-m5-c000020 | 5 | 15 | 7.77626 | completed/correct | exact_single_candidate |
| d5-m5-c000021 | 5 | 20 | 8.19743 | completed/correct | exact_single_candidate |
| d5-m5-c000022 | 5 | 9 | 4.46551 | completed/correct | exact_single_candidate |
| d5-m5-c000023 | 5 | 6 | 3.05214 | completed/correct | exact_single_candidate |
| d5-m5-c000024 | 5 | 45 | 17.2371 | completed/correct | exact_single_candidate |
| d5-m5-c000025 | 5 | 26 | 8.91539 | completed/correct | exact_single_candidate |
| d5-m5-c000026 | 3 | 7 | 2.63539 | completed/correct | exact_single_candidate |
| d5-m5-c000027 | 4 | 5 | 1.93615 | completed/correct | exact_single_candidate |
| d5-m5-c000028 | 4 | 5 | 2.34324 | completed/correct | exact_single_candidate |
| d5-m5-c000029 | 4 | 8 | 2.50979 | completed/correct | exact_single_candidate |
| d5-m5-c000030 | 4 | 3 | 1.48527 | completed/correct | exact_single_candidate |
| d5-m5-c000031 | 4 | 14 | 5.28065 | completed/correct | exact_single_candidate |
| d5-m5-c000032 | 4 | 2 | 1.2577 | completed/correct | exact_single_candidate |
| d5-m5-c000033 | 3 | 8 | 2.68729 | completed/correct | exact_single_candidate |
| d5-m5-c000034 | 5 | 14 | 8.44974 | completed/correct | exact_single_candidate |
| d5-m5-c000035 | 4 | 6 | 2.16819 | completed/correct | exact_single_candidate |
| d5-m5-c000036 | 5 | 33 | 13.4552 | completed/correct | exact_single_candidate |
| d5-m5-c000037 | 4 | 11 | 3.54944 | completed/correct | exact_single_candidate |
| d5-m5-c000038 | 3 | 10 | 3.6734 | completed/correct | exact_single_candidate |
| d5-m5-c000039 | 5 | 26 | 9.95802 | completed/correct | exact_single_candidate |
| d5-m5-c000040 | 4 | 17 | 6.37768 | completed/correct | exact_single_candidate |
| d5-m5-c000041 | 4 | 18 | 6.99359 | completed/correct | exact_single_candidate |
| d5-m5-c000042 | 5 | 12 | 3.99673 | completed/correct | exact_single_candidate |
| d5-m5-c000043 | 5 | 5 | 2.17358 | completed/correct | exact_single_candidate |
| d5-m5-c000044 | 4 | 19 | 7.35434 | completed/correct | exact_single_candidate |
| d5-m5-c000045 | 4 | 2 | 1.22579 | completed/correct | exact_single_candidate |
| d5-m5-c000046 | 4 | 31 | 15.1837 | completed/correct | exact_single_candidate |
| d5-m5-c000047 | 4 | 6 | 3.0276 | completed/correct | exact_single_candidate |
| d5-m5-c000048 | 5 | 10 | 4.29629 | completed/correct | exact_single_candidate |
| d5-m5-c000049 | 3 | 15 | 5.01821 | completed/correct | exact_single_candidate |
| d5-m5-c000050 | 5 | 4 | 2.30243 | completed/correct | exact_single_candidate |
| d5-m5-c000051 | 5 | 9 | 4.28413 | completed/correct | exact_single_candidate |
| d5-m5-c000052 | 4 | 10 | 4.43856 | completed/correct | exact_single_candidate |
| d5-m5-c000053 | 5 | 9 | 3.65204 | completed/correct | exact_single_candidate |
| d5-m5-c000054 | 5 | 8 | 3.2993 | completed/correct | exact_single_candidate |
| d5-m5-c000055 | 5 | 4 | 1.67462 | completed/correct | exact_single_candidate |
| d5-m5-c000056 | 3 | 12 | 3.91998 | completed/correct | exact_single_candidate |
| d5-m5-c000057 | 4 | 3 | 1.3185 | completed/correct | exact_single_candidate |
| d5-m5-c000058 | 5 | 22 | 11.7178 | completed/correct | exact_single_candidate |
| d5-m5-c000059 | 4 | 4 | 1.70055 | completed/correct | exact_single_candidate |
| d5-m5-c000060 | 5 | 9 | 3.79088 | completed/correct | exact_single_candidate |
| d5-m5-c000061 | 5 | 14 | 6.40798 | completed/correct | exact_single_candidate |
| d5-m5-c000062 | 4 | 7 | 2.42584 | completed/correct | exact_single_candidate |
| d5-m5-c000063 | 4 | 7 | 2.65401 | completed/correct | exact_single_candidate |
| d5-m5-c000064 | 3 | 15 | 5.34464 | completed/correct | exact_single_candidate |
| d5-m5-c000065 | 3 | 14 | 4.66622 | completed/correct | exact_single_candidate |
| d5-m5-c000066 | 5 | 20 | 7.25217 | completed/correct | exact_single_candidate |
| d5-m5-c000067 | 3 | 18 | 4.99255 | completed/correct | exact_single_candidate |
| d5-m5-c000068 | 4 | 18 | 6.57023 | completed/correct | exact_single_candidate |
| d5-m5-c000069 | 3 | 4 | 1.39692 | completed/correct | exact_single_candidate |
| d5-m5-c000070 | 4 | 42 | 16.5186 | completed/correct | exact_single_candidate |
| d5-m5-c000071 | 5 | 24 | 10.4057 | completed/correct | exact_single_candidate |
| d5-m5-c000072 | 5 | 6 | 2.81658 | completed/correct | exact_single_candidate |
| d5-m5-c000073 | 3 | 20 | 7.56566 | completed/correct | exact_single_candidate |
| d5-m5-c000074 | 3 | 3 | 1.15442 | completed/correct | exact_single_candidate |
| d5-m5-c000075 | 3 | 6 | 1.76484 | completed/correct | exact_single_candidate |
| d5-m5-c000076 | 3 | 2 | 1.01353 | completed/correct | exact_single_candidate |
| d5-m5-c000077 | 4 | 17 | 5.60211 | completed/correct | exact_single_candidate |
| d5-m5-c000078 | 3 | 13 | 6.15627 | completed/correct | exact_single_candidate |
| d5-m5-c000079 | 3 | 14 | 4.44953 | completed/correct | exact_single_candidate |
| d5-m5-c000080 | 4 | 7 | 2.59997 | completed/correct | exact_single_candidate |
| d5-m5-c000081 | 4 | 13 | 4.06804 | completed/correct | exact_single_candidate |
| d5-m5-c000082 | 4 | 6 | 2.48846 | completed/correct | exact_single_candidate |
| d5-m5-c000083 | 5 | 4 | 1.9591 | completed/correct | exact_single_candidate |
| d5-m5-c000084 | 4 | 18 | 7.16694 | completed/correct | exact_single_candidate |
| d5-m5-c000085 | 4 | 3 | 1.49244 | completed/correct | exact_single_candidate |
| d5-m5-c000086 | 3 | 2 | 1.11082 | completed/correct | exact_single_candidate |
| d5-m5-c000087 | 3 | 2 | 1.13161 | completed/correct | exact_single_candidate |
| d5-m5-c000088 | 3 | 9 | 3.14732 | completed/correct | exact_single_candidate |
| d5-m5-c000089 | 5 | 4 | 1.92129 | completed/correct | exact_single_candidate |
| d5-m5-c000090 | 5 | 22 | 7.61666 | completed/correct | exact_single_candidate |
| d5-m5-c000091 | 5 | 24 | 7.92854 | completed/correct | exact_single_candidate |
| d5-m5-c000092 | 5 | 7 | 3.60878 | completed/correct | exact_single_candidate |
| d5-m5-c000093 | 3 | 3 | 1.27604 | completed/correct | exact_single_candidate |
| d5-m5-c000094 | 4 | 7 | 2.8175 | completed/correct | exact_single_candidate |
| d5-m5-c000095 | 5 | 17 | 7.23025 | completed/correct | exact_single_candidate |
| d5-m5-c000096 | 3 | 11 | 3.51123 | completed/correct | exact_single_candidate |
| d5-m5-c000097 | 4 | 8 | 4.10175 | completed/correct | exact_single_candidate |
| d5-m5-c000098 | 4 | 20 | 8.62221 | completed/correct | exact_single_candidate |
| d5-m5-c000099 | 4 | 14 | 5.05811 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `133061ab663f37931e551d101335a3f2ca668e458ad3b41e8d5cb1d72022c519`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
