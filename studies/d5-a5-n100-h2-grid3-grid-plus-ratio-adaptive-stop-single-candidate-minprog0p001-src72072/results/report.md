# d5-a5-n100-h2-grid3-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
adaptive, H2, Grid 3, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 8.13 | 813 |
| Queries, korrekte Lösungen | 100 | 8.13 | 813 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 8.13 | 813 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 2.784 | 278.4 |
| API-Sekunden, korrekte Lösungen | 100 | 2.784 | 278.4 |
| Controller-Sekunden, sämtliche Versuche | 100 | 3.46816 | 346.816 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000014, d5-m5-c000020, d5-m5-c000036, d5-m5-c000046, d5-m5-c000058, d5-m5-c000070, d5-m5-c000071, d5-m5-c000078, d5-m5-c000098

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000000 | 2 | 6 | 1.48951 | completed/correct | exact_single_candidate |
| d5-m5-c000001 | 5 | 9 | 3.39245 | completed/correct | exact_single_candidate |
| d5-m5-c000002 | 5 | 4 | 1.49267 | completed/correct | exact_single_candidate |
| d5-m5-c000003 | 3 | 3 | 1.07754 | completed/correct | exact_single_candidate |
| d5-m5-c000004 | 5 | 8 | 4.94989 | completed/correct | exact_single_candidate |
| d5-m5-c000005 | 5 | 14 | 5.10681 | completed/correct | exact_single_candidate |
| d5-m5-c000006 | 3 | 6 | 1.71051 | completed/correct | exact_single_candidate |
| d5-m5-c000007 | 5 | 2 | 1.28341 | completed/correct | exact_single_candidate |
| d5-m5-c000008 | 4 | 12 | 3.89505 | completed/correct | exact_single_candidate |
| d5-m5-c000009 | 5 | 3 | 1.69959 | completed/correct | exact_single_candidate |
| d5-m5-c000010 | 3 | 2 | 0.968828 | completed/correct | exact_single_candidate |
| d5-m5-c000011 | 5 | 7 | 3.11182 | completed/correct | exact_single_candidate |
| d5-m5-c000012 | 4 | 5 | 1.82423 | completed/correct | exact_single_candidate |
| d5-m5-c000013 | 3 | 9 | 2.15334 | completed/correct | exact_single_candidate |
| d5-m5-c000014 | 5 | 24 | 7.12806 | completed/correct | exact_single_candidate |
| d5-m5-c000015 | 5 | 3 | 1.48627 | completed/correct | exact_single_candidate |
| d5-m5-c000016 | 3 | 2 | 0.995679 | completed/correct | exact_single_candidate |
| d5-m5-c000017 | 4 | 3 | 1.31353 | completed/correct | exact_single_candidate |
| d5-m5-c000018 | 4 | 5 | 1.66108 | completed/correct | exact_single_candidate |
| d5-m5-c000019 | 4 | 4 | 1.57788 | completed/correct | exact_single_candidate |
| d5-m5-c000020 | 5 | 14 | 5.91246 | completed/correct | exact_single_candidate |
| d5-m5-c000021 | 5 | 11 | 3.39417 | completed/correct | exact_single_candidate |
| d5-m5-c000022 | 5 | 8 | 3.56916 | completed/correct | exact_single_candidate |
| d5-m5-c000023 | 5 | 4 | 2.16743 | completed/correct | exact_single_candidate |
| d5-m5-c000024 | 5 | 10 | 2.39966 | completed/correct | exact_single_candidate |
| d5-m5-c000025 | 5 | 18 | 5.34097 | completed/correct | exact_single_candidate |
| d5-m5-c000026 | 3 | 5 | 1.31385 | completed/correct | exact_single_candidate |
| d5-m5-c000027 | 4 | 5 | 1.55595 | completed/correct | exact_single_candidate |
| d5-m5-c000028 | 4 | 4 | 1.60582 | completed/correct | exact_single_candidate |
| d5-m5-c000029 | 4 | 8 | 1.886 | completed/correct | exact_single_candidate |
| d5-m5-c000030 | 4 | 3 | 1.13418 | completed/correct | exact_single_candidate |
| d5-m5-c000031 | 4 | 6 | 1.75065 | completed/correct | exact_single_candidate |
| d5-m5-c000032 | 4 | 2 | 1.08458 | completed/correct | exact_single_candidate |
| d5-m5-c000033 | 3 | 2 | 0.952109 | completed/correct | exact_single_candidate |
| d5-m5-c000034 | 5 | 9 | 3.03392 | completed/correct | exact_single_candidate |
| d5-m5-c000035 | 4 | 6 | 1.75729 | completed/correct | exact_single_candidate |
| d5-m5-c000036 | 5 | 19 | 6.24895 | completed/correct | exact_single_candidate |
| d5-m5-c000037 | 4 | 11 | 2.76268 | completed/correct | exact_single_candidate |
| d5-m5-c000038 | 3 | 8 | 2.77699 | completed/correct | exact_single_candidate |
| d5-m5-c000039 | 5 | 9 | 3.50074 | completed/correct | exact_single_candidate |
| d5-m5-c000040 | 4 | 13 | 3.30842 | completed/correct | exact_single_candidate |
| d5-m5-c000041 | 4 | 3 | 1.24563 | completed/correct | exact_single_candidate |
| d5-m5-c000042 | 5 | 4 | 1.49381 | completed/correct | exact_single_candidate |
| d5-m5-c000043 | 5 | 4 | 1.46329 | completed/correct | exact_single_candidate |
| d5-m5-c000044 | 4 | 5 | 1.77499 | completed/correct | exact_single_candidate |
| d5-m5-c000045 | 4 | 2 | 1.06357 | completed/correct | exact_single_candidate |
| d5-m5-c000046 | 4 | 44 | 18.0832 | completed/correct | exact_single_candidate |
| d5-m5-c000047 | 4 | 6 | 2.61176 | completed/correct | exact_single_candidate |
| d5-m5-c000048 | 5 | 9 | 3.16913 | completed/correct | exact_single_candidate |
| d5-m5-c000049 | 3 | 6 | 1.84432 | completed/correct | exact_single_candidate |
| d5-m5-c000050 | 5 | 5 | 2.02163 | completed/correct | exact_single_candidate |
| d5-m5-c000051 | 5 | 11 | 4.38628 | completed/correct | exact_single_candidate |
| d5-m5-c000052 | 4 | 7 | 2.21447 | completed/correct | exact_single_candidate |
| d5-m5-c000053 | 5 | 7 | 2.23941 | completed/correct | exact_single_candidate |
| d5-m5-c000054 | 5 | 6 | 2.35031 | completed/correct | exact_single_candidate |
| d5-m5-c000055 | 5 | 5 | 1.55815 | completed/correct | exact_single_candidate |
| d5-m5-c000056 | 3 | 5 | 1.33415 | completed/correct | exact_single_candidate |
| d5-m5-c000057 | 4 | 3 | 1.15873 | completed/correct | exact_single_candidate |
| d5-m5-c000058 | 5 | 23 | 9.63544 | completed/correct | exact_single_candidate |
| d5-m5-c000059 | 4 | 4 | 1.60625 | completed/correct | exact_single_candidate |
| d5-m5-c000060 | 5 | 12 | 3.72937 | completed/correct | exact_single_candidate |
| d5-m5-c000061 | 5 | 15 | 4.81801 | completed/correct | exact_single_candidate |
| d5-m5-c000062 | 4 | 5 | 1.62653 | completed/correct | exact_single_candidate |
| d5-m5-c000063 | 4 | 4 | 1.26639 | completed/correct | exact_single_candidate |
| d5-m5-c000064 | 3 | 7 | 1.66727 | completed/correct | exact_single_candidate |
| d5-m5-c000065 | 3 | 6 | 1.63704 | completed/correct | exact_single_candidate |
| d5-m5-c000066 | 5 | 4 | 1.63545 | completed/correct | exact_single_candidate |
| d5-m5-c000067 | 3 | 23 | 5.1636 | completed/correct | exact_single_candidate |
| d5-m5-c000068 | 4 | 4 | 1.70188 | completed/correct | exact_single_candidate |
| d5-m5-c000069 | 3 | 4 | 1.20876 | completed/correct | exact_single_candidate |
| d5-m5-c000070 | 4 | 38 | 11.8458 | completed/correct | exact_single_candidate |
| d5-m5-c000071 | 5 | 18 | 6.51003 | completed/correct | exact_single_candidate |
| d5-m5-c000072 | 5 | 5 | 1.77943 | completed/correct | exact_single_candidate |
| d5-m5-c000073 | 3 | 5 | 1.53625 | completed/correct | exact_single_candidate |
| d5-m5-c000074 | 3 | 5 | 1.298 | completed/correct | exact_single_candidate |
| d5-m5-c000075 | 3 | 8 | 1.98392 | completed/correct | exact_single_candidate |
| d5-m5-c000076 | 3 | 2 | 0.922127 | completed/correct | exact_single_candidate |
| d5-m5-c000077 | 4 | 5 | 1.75242 | completed/correct | exact_single_candidate |
| d5-m5-c000078 | 3 | 17 | 6.15981 | completed/correct | exact_single_candidate |
| d5-m5-c000079 | 3 | 4 | 1.2184 | completed/correct | exact_single_candidate |
| d5-m5-c000080 | 4 | 8 | 2.21123 | completed/correct | exact_single_candidate |
| d5-m5-c000081 | 4 | 6 | 1.83321 | completed/correct | exact_single_candidate |
| d5-m5-c000082 | 4 | 6 | 2.29881 | completed/correct | exact_single_candidate |
| d5-m5-c000083 | 5 | 5 | 2.01231 | completed/correct | exact_single_candidate |
| d5-m5-c000084 | 4 | 14 | 3.78643 | completed/correct | exact_single_candidate |
| d5-m5-c000085 | 4 | 2 | 1.0807 | completed/correct | exact_single_candidate |
| d5-m5-c000086 | 3 | 2 | 1.05794 | completed/correct | exact_single_candidate |
| d5-m5-c000087 | 3 | 1 | 0.852843 | completed/correct | exact_single_candidate |
| d5-m5-c000088 | 3 | 8 | 2.21511 | completed/correct | exact_single_candidate |
| d5-m5-c000089 | 5 | 3 | 1.46938 | completed/correct | exact_single_candidate |
| d5-m5-c000090 | 5 | 22 | 5.54038 | completed/correct | exact_single_candidate |
| d5-m5-c000091 | 5 | 12 | 2.94417 | completed/correct | exact_single_candidate |
| d5-m5-c000092 | 5 | 7 | 2.88077 | completed/correct | exact_single_candidate |
| d5-m5-c000093 | 3 | 3 | 1.24293 | completed/correct | exact_single_candidate |
| d5-m5-c000094 | 4 | 5 | 1.55664 | completed/correct | exact_single_candidate |
| d5-m5-c000095 | 5 | 5 | 3.08129 | completed/correct | exact_single_candidate |
| d5-m5-c000096 | 3 | 3 | 1.12602 | completed/correct | exact_single_candidate |
| d5-m5-c000097 | 4 | 9 | 3.74009 | completed/correct | exact_single_candidate |
| d5-m5-c000098 | 4 | 25 | 7.86994 | completed/correct | exact_single_candidate |
| d5-m5-c000099 | 4 | 11 | 3.11077 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `133061ab663f37931e551d101335a3f2ca668e458ad3b41e8d5cb1d72022c519`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
