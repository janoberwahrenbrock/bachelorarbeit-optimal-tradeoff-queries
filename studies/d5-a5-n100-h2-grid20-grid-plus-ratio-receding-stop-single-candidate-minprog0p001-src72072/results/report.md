# d5-a5-n100-h2-grid20-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
receding, H2, Grid 20, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 12.68 | 1268 |
| Queries, korrekte Lösungen | 100 | 12.68 | 1268 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 12.68 | 1268 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 13.7322 | 1373.22 |
| API-Sekunden, korrekte Lösungen | 100 | 13.7322 | 1373.22 |
| Controller-Sekunden, sämtliche Versuche | 100 | 14.4352 | 1443.52 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000004, d5-m5-c000038, d5-m5-c000070, d5-m5-c000090, d5-m5-c000098

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000000 | 2 | 17 | 14.6546 | completed/correct | exact_single_candidate |
| d5-m5-c000001 | 5 | 11 | 15.3362 | completed/correct | exact_single_candidate |
| d5-m5-c000002 | 5 | 5 | 5.3474 | completed/correct | exact_single_candidate |
| d5-m5-c000003 | 3 | 5 | 4.81066 | completed/correct | exact_single_candidate |
| d5-m5-c000004 | 5 | 25 | 37.6499 | completed/correct | exact_single_candidate |
| d5-m5-c000005 | 5 | 15 | 22.7432 | completed/correct | exact_single_candidate |
| d5-m5-c000006 | 3 | 15 | 14.9801 | completed/correct | exact_single_candidate |
| d5-m5-c000007 | 5 | 4 | 4.84794 | completed/correct | exact_single_candidate |
| d5-m5-c000008 | 4 | 11 | 11.5121 | completed/correct | exact_single_candidate |
| d5-m5-c000009 | 5 | 3 | 5.24467 | completed/correct | exact_single_candidate |
| d5-m5-c000010 | 3 | 32 | 32.1893 | completed/correct | exact_single_candidate |
| d5-m5-c000011 | 5 | 11 | 13.4234 | completed/correct | exact_single_candidate |
| d5-m5-c000012 | 4 | 11 | 9.83012 | completed/correct | exact_single_candidate |
| d5-m5-c000013 | 3 | 9 | 7.83378 | completed/correct | exact_single_candidate |
| d5-m5-c000014 | 5 | 21 | 22.042 | completed/correct | exact_single_candidate |
| d5-m5-c000015 | 5 | 6 | 6.81004 | completed/correct | exact_single_candidate |
| d5-m5-c000016 | 3 | 2 | 1.84387 | completed/correct | exact_single_candidate |
| d5-m5-c000017 | 4 | 4 | 4.12708 | completed/correct | exact_single_candidate |
| d5-m5-c000018 | 4 | 13 | 13.5952 | completed/correct | exact_single_candidate |
| d5-m5-c000019 | 4 | 8 | 8.27313 | completed/correct | exact_single_candidate |
| d5-m5-c000020 | 5 | 12 | 18.3197 | completed/correct | exact_single_candidate |
| d5-m5-c000021 | 5 | 10 | 10.4617 | completed/correct | exact_single_candidate |
| d5-m5-c000022 | 5 | 8 | 11.3652 | completed/correct | exact_single_candidate |
| d5-m5-c000023 | 5 | 6 | 8.15065 | completed/correct | exact_single_candidate |
| d5-m5-c000024 | 5 | 21 | 20.4144 | completed/correct | exact_single_candidate |
| d5-m5-c000025 | 5 | 26 | 27.3503 | completed/correct | exact_single_candidate |
| d5-m5-c000026 | 3 | 18 | 15.5885 | completed/correct | exact_single_candidate |
| d5-m5-c000027 | 4 | 19 | 18.3157 | completed/correct | exact_single_candidate |
| d5-m5-c000028 | 4 | 5 | 5.79224 | completed/correct | exact_single_candidate |
| d5-m5-c000029 | 4 | 12 | 8.97471 | completed/correct | exact_single_candidate |
| d5-m5-c000030 | 4 | 4 | 4.93173 | completed/correct | exact_single_candidate |
| d5-m5-c000031 | 4 | 12 | 12.4999 | completed/correct | exact_single_candidate |
| d5-m5-c000032 | 4 | 3 | 3.20222 | completed/correct | exact_single_candidate |
| d5-m5-c000033 | 3 | 12 | 11.6994 | completed/correct | exact_single_candidate |
| d5-m5-c000034 | 5 | 20 | 29.5147 | completed/correct | exact_single_candidate |
| d5-m5-c000035 | 4 | 5 | 4.40397 | completed/correct | exact_single_candidate |
| d5-m5-c000036 | 5 | 30 | 31.875 | completed/correct | exact_single_candidate |
| d5-m5-c000037 | 4 | 25 | 21.2597 | completed/correct | exact_single_candidate |
| d5-m5-c000038 | 3 | 38 | 38.1708 | completed/correct | exact_single_candidate |
| d5-m5-c000039 | 5 | 7 | 10.1801 | completed/correct | exact_single_candidate |
| d5-m5-c000040 | 4 | 15 | 16.0924 | completed/correct | exact_single_candidate |
| d5-m5-c000041 | 4 | 26 | 27.1611 | completed/correct | exact_single_candidate |
| d5-m5-c000042 | 5 | 14 | 12.9979 | completed/correct | exact_single_candidate |
| d5-m5-c000043 | 5 | 6 | 6.27661 | completed/correct | exact_single_candidate |
| d5-m5-c000044 | 4 | 7 | 7.5515 | completed/correct | exact_single_candidate |
| d5-m5-c000045 | 4 | 2 | 2.31701 | completed/correct | exact_single_candidate |
| d5-m5-c000046 | 4 | 27 | 34.6231 | completed/correct | exact_single_candidate |
| d5-m5-c000047 | 4 | 7 | 9.79298 | completed/correct | exact_single_candidate |
| d5-m5-c000048 | 5 | 8 | 10.1261 | completed/correct | exact_single_candidate |
| d5-m5-c000049 | 3 | 12 | 11.0346 | completed/correct | exact_single_candidate |
| d5-m5-c000050 | 5 | 6 | 7.97078 | completed/correct | exact_single_candidate |
| d5-m5-c000051 | 5 | 14 | 14.3519 | completed/correct | exact_single_candidate |
| d5-m5-c000052 | 4 | 9 | 10.1625 | completed/correct | exact_single_candidate |
| d5-m5-c000053 | 5 | 9 | 10.2059 | completed/correct | exact_single_candidate |
| d5-m5-c000054 | 5 | 8 | 8.78797 | completed/correct | exact_single_candidate |
| d5-m5-c000055 | 5 | 4 | 4.01394 | completed/correct | exact_single_candidate |
| d5-m5-c000056 | 3 | 32 | 30.0395 | completed/correct | exact_single_candidate |
| d5-m5-c000057 | 4 | 3 | 2.91159 | completed/correct | exact_single_candidate |
| d5-m5-c000058 | 5 | 25 | 35.3889 | completed/correct | exact_single_candidate |
| d5-m5-c000059 | 4 | 5 | 5.01292 | completed/correct | exact_single_candidate |
| d5-m5-c000060 | 5 | 29 | 32.4932 | completed/correct | exact_single_candidate |
| d5-m5-c000061 | 5 | 6 | 7.23589 | completed/correct | exact_single_candidate |
| d5-m5-c000062 | 4 | 7 | 6.5782 | completed/correct | exact_single_candidate |
| d5-m5-c000063 | 4 | 6 | 5.85283 | completed/correct | exact_single_candidate |
| d5-m5-c000064 | 3 | 33 | 35.233 | completed/correct | exact_single_candidate |
| d5-m5-c000065 | 3 | 17 | 12.1306 | completed/correct | exact_single_candidate |
| d5-m5-c000066 | 5 | 17 | 16.3444 | completed/correct | exact_single_candidate |
| d5-m5-c000067 | 3 | 27 | 23.0236 | completed/correct | exact_single_candidate |
| d5-m5-c000068 | 4 | 6 | 6.49692 | completed/correct | exact_single_candidate |
| d5-m5-c000069 | 3 | 5 | 3.8333 | completed/correct | exact_single_candidate |
| d5-m5-c000070 | 4 | 47 | 54.7071 | completed/correct | exact_single_candidate |
| d5-m5-c000071 | 5 | 18 | 20.0953 | completed/correct | exact_single_candidate |
| d5-m5-c000072 | 5 | 5 | 5.9542 | completed/correct | exact_single_candidate |
| d5-m5-c000073 | 3 | 3 | 2.80471 | completed/correct | exact_single_candidate |
| d5-m5-c000074 | 3 | 3 | 2.34144 | completed/correct | exact_single_candidate |
| d5-m5-c000075 | 3 | 9 | 6.82661 | completed/correct | exact_single_candidate |
| d5-m5-c000076 | 3 | 2 | 1.89147 | completed/correct | exact_single_candidate |
| d5-m5-c000077 | 4 | 11 | 13.0664 | completed/correct | exact_single_candidate |
| d5-m5-c000078 | 3 | 14 | 17.8547 | completed/correct | exact_single_candidate |
| d5-m5-c000079 | 3 | 7 | 5.98814 | completed/correct | exact_single_candidate |
| d5-m5-c000080 | 4 | 8 | 7.50943 | completed/correct | exact_single_candidate |
| d5-m5-c000081 | 4 | 10 | 7.9665 | completed/correct | exact_single_candidate |
| d5-m5-c000082 | 4 | 6 | 6.49676 | completed/correct | exact_single_candidate |
| d5-m5-c000083 | 5 | 9 | 9.08895 | completed/correct | exact_single_candidate |
| d5-m5-c000084 | 4 | 22 | 30.6562 | completed/correct | exact_single_candidate |
| d5-m5-c000085 | 4 | 5 | 4.48982 | completed/correct | exact_single_candidate |
| d5-m5-c000086 | 3 | 2 | 2.19836 | completed/correct | exact_single_candidate |
| d5-m5-c000087 | 3 | 2 | 2.24946 | completed/correct | exact_single_candidate |
| d5-m5-c000088 | 3 | 7 | 6.90016 | completed/correct | exact_single_candidate |
| d5-m5-c000089 | 5 | 4 | 4.85316 | completed/correct | exact_single_candidate |
| d5-m5-c000090 | 5 | 41 | 39.4368 | completed/correct | exact_single_candidate |
| d5-m5-c000091 | 5 | 12 | 11.3912 | completed/correct | exact_single_candidate |
| d5-m5-c000092 | 5 | 6 | 9.01687 | completed/correct | exact_single_candidate |
| d5-m5-c000093 | 3 | 2 | 1.87803 | completed/correct | exact_single_candidate |
| d5-m5-c000094 | 4 | 20 | 21.5683 | completed/correct | exact_single_candidate |
| d5-m5-c000095 | 5 | 14 | 17.4976 | completed/correct | exact_single_candidate |
| d5-m5-c000096 | 3 | 10 | 7.76228 | completed/correct | exact_single_candidate |
| d5-m5-c000097 | 4 | 8 | 11.4229 | completed/correct | exact_single_candidate |
| d5-m5-c000098 | 4 | 36 | 41.3776 | completed/correct | exact_single_candidate |
| d5-m5-c000099 | 4 | 12 | 12.3223 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `133061ab663f37931e551d101335a3f2ca668e458ad3b41e8d5cb1d72022c519`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
