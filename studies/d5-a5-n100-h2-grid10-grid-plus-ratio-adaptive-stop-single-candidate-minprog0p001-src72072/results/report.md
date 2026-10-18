# d5-a5-n100-h2-grid10-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
adaptive, H2, Grid 10, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 8.3 | 830 |
| Queries, korrekte Lösungen | 100 | 8.3 | 830 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 8.3 | 830 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 5.53194 | 553.194 |
| API-Sekunden, korrekte Lösungen | 100 | 5.53194 | 553.194 |
| Controller-Sekunden, sämtliche Versuche | 100 | 6.20683 | 620.683 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000036, d5-m5-c000046, d5-m5-c000058, d5-m5-c000070, d5-m5-c000098

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000000 | 2 | 8 | 3.37541 | completed/correct | exact_single_candidate |
| d5-m5-c000001 | 5 | 9 | 6.64568 | completed/correct | exact_single_candidate |
| d5-m5-c000002 | 5 | 5 | 3.12156 | completed/correct | exact_single_candidate |
| d5-m5-c000003 | 3 | 3 | 1.77291 | completed/correct | exact_single_candidate |
| d5-m5-c000004 | 5 | 8 | 8.82673 | completed/correct | exact_single_candidate |
| d5-m5-c000005 | 5 | 13 | 9.73715 | completed/correct | exact_single_candidate |
| d5-m5-c000006 | 3 | 6 | 2.97609 | completed/correct | exact_single_candidate |
| d5-m5-c000007 | 5 | 2 | 2.27087 | completed/correct | exact_single_candidate |
| d5-m5-c000008 | 4 | 12 | 8.20001 | completed/correct | exact_single_candidate |
| d5-m5-c000009 | 5 | 3 | 2.92479 | completed/correct | exact_single_candidate |
| d5-m5-c000010 | 3 | 2 | 1.50356 | completed/correct | exact_single_candidate |
| d5-m5-c000011 | 5 | 6 | 7.03239 | completed/correct | exact_single_candidate |
| d5-m5-c000012 | 4 | 5 | 3.49036 | completed/correct | exact_single_candidate |
| d5-m5-c000013 | 3 | 11 | 4.7448 | completed/correct | exact_single_candidate |
| d5-m5-c000014 | 5 | 20 | 12.1305 | completed/correct | exact_single_candidate |
| d5-m5-c000015 | 5 | 3 | 2.80105 | completed/correct | exact_single_candidate |
| d5-m5-c000016 | 3 | 2 | 1.48796 | completed/correct | exact_single_candidate |
| d5-m5-c000017 | 4 | 3 | 2.20709 | completed/correct | exact_single_candidate |
| d5-m5-c000018 | 4 | 7 | 3.61648 | completed/correct | exact_single_candidate |
| d5-m5-c000019 | 4 | 4 | 2.95618 | completed/correct | exact_single_candidate |
| d5-m5-c000020 | 5 | 14 | 12.8686 | completed/correct | exact_single_candidate |
| d5-m5-c000021 | 5 | 12 | 7.10355 | completed/correct | exact_single_candidate |
| d5-m5-c000022 | 5 | 10 | 8.09463 | completed/correct | exact_single_candidate |
| d5-m5-c000023 | 5 | 4 | 4.00117 | completed/correct | exact_single_candidate |
| d5-m5-c000024 | 5 | 11 | 6.26287 | completed/correct | exact_single_candidate |
| d5-m5-c000025 | 5 | 19 | 12.0314 | completed/correct | exact_single_candidate |
| d5-m5-c000026 | 3 | 4 | 1.92882 | completed/correct | exact_single_candidate |
| d5-m5-c000027 | 4 | 4 | 2.5854 | completed/correct | exact_single_candidate |
| d5-m5-c000028 | 4 | 4 | 3.0681 | completed/correct | exact_single_candidate |
| d5-m5-c000029 | 4 | 7 | 3.29404 | completed/correct | exact_single_candidate |
| d5-m5-c000030 | 4 | 3 | 1.91472 | completed/correct | exact_single_candidate |
| d5-m5-c000031 | 4 | 8 | 4.07616 | completed/correct | exact_single_candidate |
| d5-m5-c000032 | 4 | 2 | 1.74372 | completed/correct | exact_single_candidate |
| d5-m5-c000033 | 3 | 2 | 1.49983 | completed/correct | exact_single_candidate |
| d5-m5-c000034 | 5 | 9 | 6.10952 | completed/correct | exact_single_candidate |
| d5-m5-c000035 | 4 | 6 | 3.08339 | completed/correct | exact_single_candidate |
| d5-m5-c000036 | 5 | 26 | 18.0141 | completed/correct | exact_single_candidate |
| d5-m5-c000037 | 4 | 8 | 4.15752 | completed/correct | exact_single_candidate |
| d5-m5-c000038 | 3 | 8 | 5.45973 | completed/correct | exact_single_candidate |
| d5-m5-c000039 | 5 | 9 | 7.10873 | completed/correct | exact_single_candidate |
| d5-m5-c000040 | 4 | 11 | 6.36158 | completed/correct | exact_single_candidate |
| d5-m5-c000041 | 4 | 3 | 2.13492 | completed/correct | exact_single_candidate |
| d5-m5-c000042 | 5 | 4 | 2.69964 | completed/correct | exact_single_candidate |
| d5-m5-c000043 | 5 | 4 | 2.66344 | completed/correct | exact_single_candidate |
| d5-m5-c000044 | 4 | 6 | 3.53208 | completed/correct | exact_single_candidate |
| d5-m5-c000045 | 4 | 2 | 1.62905 | completed/correct | exact_single_candidate |
| d5-m5-c000046 | 4 | 40 | 29.8568 | completed/correct | exact_single_candidate |
| d5-m5-c000047 | 4 | 6 | 5.30805 | completed/correct | exact_single_candidate |
| d5-m5-c000048 | 5 | 11 | 7.69579 | completed/correct | exact_single_candidate |
| d5-m5-c000049 | 3 | 9 | 4.98119 | completed/correct | exact_single_candidate |
| d5-m5-c000050 | 5 | 5 | 3.7534 | completed/correct | exact_single_candidate |
| d5-m5-c000051 | 5 | 11 | 9.22879 | completed/correct | exact_single_candidate |
| d5-m5-c000052 | 4 | 6 | 3.3141 | completed/correct | exact_single_candidate |
| d5-m5-c000053 | 5 | 7 | 4.09375 | completed/correct | exact_single_candidate |
| d5-m5-c000054 | 5 | 6 | 4.70101 | completed/correct | exact_single_candidate |
| d5-m5-c000055 | 5 | 5 | 3.03046 | completed/correct | exact_single_candidate |
| d5-m5-c000056 | 3 | 5 | 2.09288 | completed/correct | exact_single_candidate |
| d5-m5-c000057 | 4 | 3 | 2.00322 | completed/correct | exact_single_candidate |
| d5-m5-c000058 | 5 | 23 | 18.7627 | completed/correct | exact_single_candidate |
| d5-m5-c000059 | 4 | 4 | 2.6546 | completed/correct | exact_single_candidate |
| d5-m5-c000060 | 5 | 14 | 8.52117 | completed/correct | exact_single_candidate |
| d5-m5-c000061 | 5 | 9 | 5.61979 | completed/correct | exact_single_candidate |
| d5-m5-c000062 | 4 | 5 | 2.88136 | completed/correct | exact_single_candidate |
| d5-m5-c000063 | 4 | 3 | 1.87337 | completed/correct | exact_single_candidate |
| d5-m5-c000064 | 3 | 6 | 2.48376 | completed/correct | exact_single_candidate |
| d5-m5-c000065 | 3 | 6 | 2.71075 | completed/correct | exact_single_candidate |
| d5-m5-c000066 | 5 | 5 | 3.09513 | completed/correct | exact_single_candidate |
| d5-m5-c000067 | 3 | 17 | 9.28579 | completed/correct | exact_single_candidate |
| d5-m5-c000068 | 4 | 4 | 3.25525 | completed/correct | exact_single_candidate |
| d5-m5-c000069 | 3 | 3 | 1.67345 | completed/correct | exact_single_candidate |
| d5-m5-c000070 | 4 | 50 | 33.0985 | completed/correct | exact_single_candidate |
| d5-m5-c000071 | 5 | 14 | 12.0236 | completed/correct | exact_single_candidate |
| d5-m5-c000072 | 5 | 5 | 3.28126 | completed/correct | exact_single_candidate |
| d5-m5-c000073 | 3 | 3 | 1.73322 | completed/correct | exact_single_candidate |
| d5-m5-c000074 | 3 | 4 | 1.9923 | completed/correct | exact_single_candidate |
| d5-m5-c000075 | 3 | 8 | 3.65065 | completed/correct | exact_single_candidate |
| d5-m5-c000076 | 3 | 2 | 1.43711 | completed/correct | exact_single_candidate |
| d5-m5-c000077 | 4 | 5 | 3.0741 | completed/correct | exact_single_candidate |
| d5-m5-c000078 | 3 | 17 | 13.1461 | completed/correct | exact_single_candidate |
| d5-m5-c000079 | 3 | 4 | 2.13443 | completed/correct | exact_single_candidate |
| d5-m5-c000080 | 4 | 7 | 3.65454 | completed/correct | exact_single_candidate |
| d5-m5-c000081 | 4 | 6 | 3.18245 | completed/correct | exact_single_candidate |
| d5-m5-c000082 | 4 | 6 | 4.03312 | completed/correct | exact_single_candidate |
| d5-m5-c000083 | 5 | 5 | 3.4451 | completed/correct | exact_single_candidate |
| d5-m5-c000084 | 4 | 12 | 9.5968 | completed/correct | exact_single_candidate |
| d5-m5-c000085 | 4 | 2 | 1.7602 | completed/correct | exact_single_candidate |
| d5-m5-c000086 | 3 | 2 | 1.56253 | completed/correct | exact_single_candidate |
| d5-m5-c000087 | 3 | 1 | 1.203 | completed/correct | exact_single_candidate |
| d5-m5-c000088 | 3 | 8 | 4.24982 | completed/correct | exact_single_candidate |
| d5-m5-c000089 | 5 | 3 | 2.43465 | completed/correct | exact_single_candidate |
| d5-m5-c000090 | 5 | 24 | 12.6918 | completed/correct | exact_single_candidate |
| d5-m5-c000091 | 5 | 14 | 6.73324 | completed/correct | exact_single_candidate |
| d5-m5-c000092 | 5 | 7 | 5.67418 | completed/correct | exact_single_candidate |
| d5-m5-c000093 | 3 | 3 | 1.78312 | completed/correct | exact_single_candidate |
| d5-m5-c000094 | 4 | 12 | 6.07559 | completed/correct | exact_single_candidate |
| d5-m5-c000095 | 5 | 5 | 5.84943 | completed/correct | exact_single_candidate |
| d5-m5-c000096 | 3 | 3 | 1.69206 | completed/correct | exact_single_candidate |
| d5-m5-c000097 | 4 | 9 | 7.35572 | completed/correct | exact_single_candidate |
| d5-m5-c000098 | 4 | 28 | 17.7714 | completed/correct | exact_single_candidate |
| d5-m5-c000099 | 4 | 16 | 8.74919 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `133061ab663f37931e551d101335a3f2ca668e458ad3b41e8d5cb1d72022c519`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
