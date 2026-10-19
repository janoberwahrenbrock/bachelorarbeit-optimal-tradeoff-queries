# d5-a5-n100-h2-grid5-grid-adaptive-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
adaptive, H2, Grid 5, Queryquelle grid, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 8.63 | 863 |
| Queries, korrekte Lösungen | 100 | 8.63 | 863 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 8.63 | 863 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 3.50536 | 350.536 |
| API-Sekunden, korrekte Lösungen | 100 | 3.50536 | 350.536 |
| Controller-Sekunden, sämtliche Versuche | 100 | 4.20948 | 420.948 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000014, d5-m5-c000036, d5-m5-c000046, d5-m5-c000058, d5-m5-c000070, d5-m5-c000071, d5-m5-c000078, d5-m5-c000098

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000000 | 2 | 7 | 1.67411 | completed/correct | exact_single_candidate |
| d5-m5-c000001 | 5 | 10 | 4.77731 | completed/correct | exact_single_candidate |
| d5-m5-c000002 | 5 | 4 | 1.75725 | completed/correct | exact_single_candidate |
| d5-m5-c000003 | 3 | 3 | 1.26732 | completed/correct | exact_single_candidate |
| d5-m5-c000004 | 5 | 9 | 6.07905 | completed/correct | exact_single_candidate |
| d5-m5-c000005 | 5 | 14 | 6.04754 | completed/correct | exact_single_candidate |
| d5-m5-c000006 | 3 | 4 | 1.67849 | completed/correct | exact_single_candidate |
| d5-m5-c000007 | 5 | 2 | 1.46636 | completed/correct | exact_single_candidate |
| d5-m5-c000008 | 4 | 11 | 4.96488 | completed/correct | exact_single_candidate |
| d5-m5-c000009 | 5 | 3 | 1.88069 | completed/correct | exact_single_candidate |
| d5-m5-c000010 | 3 | 2 | 1.14848 | completed/correct | exact_single_candidate |
| d5-m5-c000011 | 5 | 6 | 3.19257 | completed/correct | exact_single_candidate |
| d5-m5-c000012 | 4 | 5 | 2.25176 | completed/correct | exact_single_candidate |
| d5-m5-c000013 | 3 | 10 | 3.06894 | completed/correct | exact_single_candidate |
| d5-m5-c000014 | 5 | 30 | 10.6351 | completed/correct | exact_single_candidate |
| d5-m5-c000015 | 5 | 3 | 1.67778 | completed/correct | exact_single_candidate |
| d5-m5-c000016 | 3 | 2 | 1.29764 | completed/correct | exact_single_candidate |
| d5-m5-c000017 | 4 | 3 | 1.48136 | completed/correct | exact_single_candidate |
| d5-m5-c000018 | 4 | 5 | 2.00884 | completed/correct | exact_single_candidate |
| d5-m5-c000019 | 4 | 9 | 3.97519 | completed/correct | exact_single_candidate |
| d5-m5-c000020 | 5 | 13 | 5.56177 | completed/correct | exact_single_candidate |
| d5-m5-c000021 | 5 | 10 | 3.69004 | completed/correct | exact_single_candidate |
| d5-m5-c000022 | 5 | 9 | 4.52818 | completed/correct | exact_single_candidate |
| d5-m5-c000023 | 5 | 4 | 2.33892 | completed/correct | exact_single_candidate |
| d5-m5-c000024 | 5 | 11 | 3.86858 | completed/correct | exact_single_candidate |
| d5-m5-c000025 | 5 | 21 | 7.24659 | completed/correct | exact_single_candidate |
| d5-m5-c000026 | 3 | 4 | 1.42661 | completed/correct | exact_single_candidate |
| d5-m5-c000027 | 4 | 6 | 2.55426 | completed/correct | exact_single_candidate |
| d5-m5-c000028 | 4 | 4 | 1.97601 | completed/correct | exact_single_candidate |
| d5-m5-c000029 | 4 | 8 | 2.39362 | completed/correct | exact_single_candidate |
| d5-m5-c000030 | 4 | 3 | 1.3798 | completed/correct | exact_single_candidate |
| d5-m5-c000031 | 4 | 9 | 2.83582 | completed/correct | exact_single_candidate |
| d5-m5-c000032 | 4 | 2 | 1.2456 | completed/correct | exact_single_candidate |
| d5-m5-c000033 | 3 | 2 | 1.11822 | completed/correct | exact_single_candidate |
| d5-m5-c000034 | 5 | 9 | 3.73403 | completed/correct | exact_single_candidate |
| d5-m5-c000035 | 4 | 6 | 1.92309 | completed/correct | exact_single_candidate |
| d5-m5-c000036 | 5 | 26 | 10.7538 | completed/correct | exact_single_candidate |
| d5-m5-c000037 | 4 | 9 | 3.11964 | completed/correct | exact_single_candidate |
| d5-m5-c000038 | 3 | 8 | 3.75353 | completed/correct | exact_single_candidate |
| d5-m5-c000039 | 5 | 9 | 3.90269 | completed/correct | exact_single_candidate |
| d5-m5-c000040 | 4 | 12 | 4.44508 | completed/correct | exact_single_candidate |
| d5-m5-c000041 | 4 | 3 | 1.4788 | completed/correct | exact_single_candidate |
| d5-m5-c000042 | 5 | 4 | 1.77531 | completed/correct | exact_single_candidate |
| d5-m5-c000043 | 5 | 4 | 1.87281 | completed/correct | exact_single_candidate |
| d5-m5-c000044 | 4 | 5 | 2.04309 | completed/correct | exact_single_candidate |
| d5-m5-c000045 | 4 | 2 | 1.1951 | completed/correct | exact_single_candidate |
| d5-m5-c000046 | 4 | 40 | 16.6864 | completed/correct | exact_single_candidate |
| d5-m5-c000047 | 4 | 6 | 2.93396 | completed/correct | exact_single_candidate |
| d5-m5-c000048 | 5 | 9 | 3.8227 | completed/correct | exact_single_candidate |
| d5-m5-c000049 | 3 | 9 | 2.8337 | completed/correct | exact_single_candidate |
| d5-m5-c000050 | 5 | 6 | 2.58613 | completed/correct | exact_single_candidate |
| d5-m5-c000051 | 5 | 12 | 5.67782 | completed/correct | exact_single_candidate |
| d5-m5-c000052 | 4 | 8 | 3.33712 | completed/correct | exact_single_candidate |
| d5-m5-c000053 | 5 | 7 | 2.55908 | completed/correct | exact_single_candidate |
| d5-m5-c000054 | 5 | 6 | 2.84459 | completed/correct | exact_single_candidate |
| d5-m5-c000055 | 5 | 4 | 1.74166 | completed/correct | exact_single_candidate |
| d5-m5-c000056 | 3 | 17 | 4.9061 | completed/correct | exact_single_candidate |
| d5-m5-c000057 | 4 | 3 | 1.39603 | completed/correct | exact_single_candidate |
| d5-m5-c000058 | 5 | 29 | 13.6549 | completed/correct | exact_single_candidate |
| d5-m5-c000059 | 4 | 4 | 1.76635 | completed/correct | exact_single_candidate |
| d5-m5-c000060 | 5 | 15 | 5.96532 | completed/correct | exact_single_candidate |
| d5-m5-c000061 | 5 | 8 | 3.08971 | completed/correct | exact_single_candidate |
| d5-m5-c000062 | 4 | 5 | 2.09422 | completed/correct | exact_single_candidate |
| d5-m5-c000063 | 4 | 3 | 1.32731 | completed/correct | exact_single_candidate |
| d5-m5-c000064 | 3 | 7 | 2.13994 | completed/correct | exact_single_candidate |
| d5-m5-c000065 | 3 | 11 | 2.98104 | completed/correct | exact_single_candidate |
| d5-m5-c000066 | 5 | 4 | 1.78628 | completed/correct | exact_single_candidate |
| d5-m5-c000067 | 3 | 20 | 5.35606 | completed/correct | exact_single_candidate |
| d5-m5-c000068 | 4 | 4 | 2.05117 | completed/correct | exact_single_candidate |
| d5-m5-c000069 | 3 | 5 | 1.684 | completed/correct | exact_single_candidate |
| d5-m5-c000070 | 4 | 47 | 18.5967 | completed/correct | exact_single_candidate |
| d5-m5-c000071 | 5 | 17 | 7.49058 | completed/correct | exact_single_candidate |
| d5-m5-c000072 | 5 | 5 | 2.19715 | completed/correct | exact_single_candidate |
| d5-m5-c000073 | 3 | 5 | 1.71893 | completed/correct | exact_single_candidate |
| d5-m5-c000074 | 3 | 4 | 1.42761 | completed/correct | exact_single_candidate |
| d5-m5-c000075 | 3 | 9 | 3.38865 | completed/correct | exact_single_candidate |
| d5-m5-c000076 | 3 | 2 | 1.08127 | completed/correct | exact_single_candidate |
| d5-m5-c000077 | 4 | 5 | 2.08159 | completed/correct | exact_single_candidate |
| d5-m5-c000078 | 3 | 22 | 10.4593 | completed/correct | exact_single_candidate |
| d5-m5-c000079 | 3 | 4 | 1.50694 | completed/correct | exact_single_candidate |
| d5-m5-c000080 | 4 | 9 | 2.98981 | completed/correct | exact_single_candidate |
| d5-m5-c000081 | 4 | 6 | 2.28462 | completed/correct | exact_single_candidate |
| d5-m5-c000082 | 4 | 6 | 2.54404 | completed/correct | exact_single_candidate |
| d5-m5-c000083 | 5 | 5 | 2.16439 | completed/correct | exact_single_candidate |
| d5-m5-c000084 | 4 | 10 | 4.05079 | completed/correct | exact_single_candidate |
| d5-m5-c000085 | 4 | 2 | 1.22677 | completed/correct | exact_single_candidate |
| d5-m5-c000086 | 3 | 2 | 1.13721 | completed/correct | exact_single_candidate |
| d5-m5-c000087 | 3 | 1 | 0.963612 | completed/correct | exact_single_candidate |
| d5-m5-c000088 | 3 | 8 | 2.81201 | completed/correct | exact_single_candidate |
| d5-m5-c000089 | 5 | 3 | 1.59951 | completed/correct | exact_single_candidate |
| d5-m5-c000090 | 5 | 23 | 6.85292 | completed/correct | exact_single_candidate |
| d5-m5-c000091 | 5 | 11 | 3.62251 | completed/correct | exact_single_candidate |
| d5-m5-c000092 | 5 | 12 | 4.50985 | completed/correct | exact_single_candidate |
| d5-m5-c000093 | 3 | 3 | 1.39764 | completed/correct | exact_single_candidate |
| d5-m5-c000094 | 4 | 5 | 1.98445 | completed/correct | exact_single_candidate |
| d5-m5-c000095 | 5 | 6 | 3.60099 | completed/correct | exact_single_candidate |
| d5-m5-c000096 | 3 | 3 | 1.36301 | completed/correct | exact_single_candidate |
| d5-m5-c000097 | 4 | 4 | 2.188 | completed/correct | exact_single_candidate |
| d5-m5-c000098 | 4 | 23 | 8.70095 | completed/correct | exact_single_candidate |
| d5-m5-c000099 | 4 | 14 | 4.88068 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `133061ab663f37931e551d101335a3f2ca668e458ad3b41e8d5cb1d72022c519`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
