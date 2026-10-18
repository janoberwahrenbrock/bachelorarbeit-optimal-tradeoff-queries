# d5-a5-n100-h2-grid20-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
adaptive, H2, Grid 20, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 8.31 | 831 |
| Queries, korrekte Lösungen | 100 | 8.31 | 831 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 8.31 | 831 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 9.464 | 946.4 |
| API-Sekunden, korrekte Lösungen | 100 | 9.464 | 946.4 |
| Controller-Sekunden, sämtliche Versuche | 100 | 10.159 | 1015.9 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000014, d5-m5-c000020, d5-m5-c000036, d5-m5-c000046, d5-m5-c000058, d5-m5-c000070, d5-m5-c000071, d5-m5-c000090, d5-m5-c000098

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000000 | 2 | 6 | 3.90825 | completed/correct | exact_single_candidate |
| d5-m5-c000001 | 5 | 6 | 8.52423 | completed/correct | exact_single_candidate |
| d5-m5-c000002 | 5 | 4 | 4.13611 | completed/correct | exact_single_candidate |
| d5-m5-c000003 | 3 | 3 | 2.66646 | completed/correct | exact_single_candidate |
| d5-m5-c000004 | 5 | 8 | 15.7179 | completed/correct | exact_single_candidate |
| d5-m5-c000005 | 5 | 14 | 21.9264 | completed/correct | exact_single_candidate |
| d5-m5-c000006 | 3 | 7 | 6.95412 | completed/correct | exact_single_candidate |
| d5-m5-c000007 | 5 | 2 | 3.70949 | completed/correct | exact_single_candidate |
| d5-m5-c000008 | 4 | 10 | 12.9453 | completed/correct | exact_single_candidate |
| d5-m5-c000009 | 5 | 3 | 4.91912 | completed/correct | exact_single_candidate |
| d5-m5-c000010 | 3 | 2 | 2.22483 | completed/correct | exact_single_candidate |
| d5-m5-c000011 | 5 | 6 | 12.6018 | completed/correct | exact_single_candidate |
| d5-m5-c000012 | 4 | 6 | 6.31388 | completed/correct | exact_single_candidate |
| d5-m5-c000013 | 3 | 10 | 7.56122 | completed/correct | exact_single_candidate |
| d5-m5-c000014 | 5 | 23 | 25.1898 | completed/correct | exact_single_candidate |
| d5-m5-c000015 | 5 | 3 | 4.62896 | completed/correct | exact_single_candidate |
| d5-m5-c000016 | 3 | 2 | 2.19747 | completed/correct | exact_single_candidate |
| d5-m5-c000017 | 4 | 3 | 3.56502 | completed/correct | exact_single_candidate |
| d5-m5-c000018 | 4 | 7 | 6.07462 | completed/correct | exact_single_candidate |
| d5-m5-c000019 | 4 | 4 | 4.96411 | completed/correct | exact_single_candidate |
| d5-m5-c000020 | 5 | 14 | 22.9045 | completed/correct | exact_single_candidate |
| d5-m5-c000021 | 5 | 12 | 12.3157 | completed/correct | exact_single_candidate |
| d5-m5-c000022 | 5 | 10 | 14.0989 | completed/correct | exact_single_candidate |
| d5-m5-c000023 | 5 | 4 | 6.82384 | completed/correct | exact_single_candidate |
| d5-m5-c000024 | 5 | 9 | 7.79111 | completed/correct | exact_single_candidate |
| d5-m5-c000025 | 5 | 22 | 21.6093 | completed/correct | exact_single_candidate |
| d5-m5-c000026 | 3 | 5 | 3.78128 | completed/correct | exact_single_candidate |
| d5-m5-c000027 | 4 | 4 | 4.10985 | completed/correct | exact_single_candidate |
| d5-m5-c000028 | 4 | 4 | 5.1686 | completed/correct | exact_single_candidate |
| d5-m5-c000029 | 4 | 7 | 5.51459 | completed/correct | exact_single_candidate |
| d5-m5-c000030 | 4 | 3 | 2.94108 | completed/correct | exact_single_candidate |
| d5-m5-c000031 | 4 | 8 | 6.93799 | completed/correct | exact_single_candidate |
| d5-m5-c000032 | 4 | 2 | 2.78082 | completed/correct | exact_single_candidate |
| d5-m5-c000033 | 3 | 2 | 2.17622 | completed/correct | exact_single_candidate |
| d5-m5-c000034 | 5 | 9 | 10.7038 | completed/correct | exact_single_candidate |
| d5-m5-c000035 | 4 | 7 | 5.37751 | completed/correct | exact_single_candidate |
| d5-m5-c000036 | 5 | 24 | 28.358 | completed/correct | exact_single_candidate |
| d5-m5-c000037 | 4 | 6 | 5.61214 | completed/correct | exact_single_candidate |
| d5-m5-c000038 | 3 | 6 | 7.5148 | completed/correct | exact_single_candidate |
| d5-m5-c000039 | 5 | 9 | 12.6975 | completed/correct | exact_single_candidate |
| d5-m5-c000040 | 4 | 11 | 11.148 | completed/correct | exact_single_candidate |
| d5-m5-c000041 | 4 | 3 | 3.39936 | completed/correct | exact_single_candidate |
| d5-m5-c000042 | 5 | 4 | 4.74594 | completed/correct | exact_single_candidate |
| d5-m5-c000043 | 5 | 4 | 4.33909 | completed/correct | exact_single_candidate |
| d5-m5-c000044 | 4 | 6 | 5.95605 | completed/correct | exact_single_candidate |
| d5-m5-c000045 | 4 | 2 | 2.44473 | completed/correct | exact_single_candidate |
| d5-m5-c000046 | 4 | 40 | 53.9572 | completed/correct | exact_single_candidate |
| d5-m5-c000047 | 4 | 6 | 9.14871 | completed/correct | exact_single_candidate |
| d5-m5-c000048 | 5 | 9 | 11.5293 | completed/correct | exact_single_candidate |
| d5-m5-c000049 | 3 | 11 | 10.5032 | completed/correct | exact_single_candidate |
| d5-m5-c000050 | 5 | 5 | 5.9967 | completed/correct | exact_single_candidate |
| d5-m5-c000051 | 5 | 11 | 16.4892 | completed/correct | exact_single_candidate |
| d5-m5-c000052 | 4 | 6 | 5.62002 | completed/correct | exact_single_candidate |
| d5-m5-c000053 | 5 | 5 | 5.62415 | completed/correct | exact_single_candidate |
| d5-m5-c000054 | 5 | 6 | 8.09626 | completed/correct | exact_single_candidate |
| d5-m5-c000055 | 5 | 4 | 4.32635 | completed/correct | exact_single_candidate |
| d5-m5-c000056 | 3 | 13 | 11.0236 | completed/correct | exact_single_candidate |
| d5-m5-c000057 | 4 | 3 | 3.07947 | completed/correct | exact_single_candidate |
| d5-m5-c000058 | 5 | 20 | 30.1277 | completed/correct | exact_single_candidate |
| d5-m5-c000059 | 4 | 4 | 4.29777 | completed/correct | exact_single_candidate |
| d5-m5-c000060 | 5 | 11 | 12.2004 | completed/correct | exact_single_candidate |
| d5-m5-c000061 | 5 | 6 | 7.51594 | completed/correct | exact_single_candidate |
| d5-m5-c000062 | 4 | 5 | 4.87867 | completed/correct | exact_single_candidate |
| d5-m5-c000063 | 4 | 3 | 2.94055 | completed/correct | exact_single_candidate |
| d5-m5-c000064 | 3 | 6 | 4.04161 | completed/correct | exact_single_candidate |
| d5-m5-c000065 | 3 | 8 | 5.40425 | completed/correct | exact_single_candidate |
| d5-m5-c000066 | 5 | 5 | 5.38074 | completed/correct | exact_single_candidate |
| d5-m5-c000067 | 3 | 26 | 21.9466 | completed/correct | exact_single_candidate |
| d5-m5-c000068 | 4 | 4 | 5.45107 | completed/correct | exact_single_candidate |
| d5-m5-c000069 | 3 | 4 | 2.83402 | completed/correct | exact_single_candidate |
| d5-m5-c000070 | 4 | 42 | 50.6071 | completed/correct | exact_single_candidate |
| d5-m5-c000071 | 5 | 25 | 25.5636 | completed/correct | exact_single_candidate |
| d5-m5-c000072 | 5 | 5 | 5.64542 | completed/correct | exact_single_candidate |
| d5-m5-c000073 | 3 | 3 | 2.70329 | completed/correct | exact_single_candidate |
| d5-m5-c000074 | 3 | 4 | 3.1238 | completed/correct | exact_single_candidate |
| d5-m5-c000075 | 3 | 9 | 6.30983 | completed/correct | exact_single_candidate |
| d5-m5-c000076 | 3 | 2 | 2.04473 | completed/correct | exact_single_candidate |
| d5-m5-c000077 | 4 | 8 | 8.67685 | completed/correct | exact_single_candidate |
| d5-m5-c000078 | 3 | 19 | 21.1305 | completed/correct | exact_single_candidate |
| d5-m5-c000079 | 3 | 4 | 3.6763 | completed/correct | exact_single_candidate |
| d5-m5-c000080 | 4 | 5 | 4.91623 | completed/correct | exact_single_candidate |
| d5-m5-c000081 | 4 | 4 | 4.17897 | completed/correct | exact_single_candidate |
| d5-m5-c000082 | 4 | 6 | 6.83948 | completed/correct | exact_single_candidate |
| d5-m5-c000083 | 5 | 5 | 5.95629 | completed/correct | exact_single_candidate |
| d5-m5-c000084 | 4 | 6 | 5.50088 | completed/correct | exact_single_candidate |
| d5-m5-c000085 | 4 | 2 | 2.82296 | completed/correct | exact_single_candidate |
| d5-m5-c000086 | 3 | 2 | 2.34804 | completed/correct | exact_single_candidate |
| d5-m5-c000087 | 3 | 1 | 1.6563 | completed/correct | exact_single_candidate |
| d5-m5-c000088 | 3 | 5 | 4.81899 | completed/correct | exact_single_candidate |
| d5-m5-c000089 | 5 | 3 | 4.00964 | completed/correct | exact_single_candidate |
| d5-m5-c000090 | 5 | 27 | 28.3229 | completed/correct | exact_single_candidate |
| d5-m5-c000091 | 5 | 14 | 13.5815 | completed/correct | exact_single_candidate |
| d5-m5-c000092 | 5 | 7 | 10.2754 | completed/correct | exact_single_candidate |
| d5-m5-c000093 | 3 | 3 | 2.67316 | completed/correct | exact_single_candidate |
| d5-m5-c000094 | 4 | 12 | 11.279 | completed/correct | exact_single_candidate |
| d5-m5-c000095 | 5 | 5 | 10.5929 | completed/correct | exact_single_candidate |
| d5-m5-c000096 | 3 | 3 | 2.4891 | completed/correct | exact_single_candidate |
| d5-m5-c000097 | 4 | 9 | 13.0508 | completed/correct | exact_single_candidate |
| d5-m5-c000098 | 4 | 27 | 30.4844 | completed/correct | exact_single_candidate |
| d5-m5-c000099 | 4 | 17 | 16.7286 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `133061ab663f37931e551d101335a3f2ca668e458ad3b41e8d5cb1d72022c519`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
