# d5-a5-n100-h2-grid3-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
receding, H2, Grid 3, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 11.18 | 1118 |
| Queries, korrekte Lösungen | 100 | 11.18 | 1118 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 11.18 | 1118 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 3.47266 | 347.266 |
| API-Sekunden, korrekte Lösungen | 100 | 3.47266 | 347.266 |
| Controller-Sekunden, sämtliche Versuche | 100 | 4.15123 | 415.123 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000036, d5-m5-c000046, d5-m5-c000058, d5-m5-c000070, d5-m5-c000078

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000000 | 2 | 14 | 3.4336 | completed/correct | exact_single_candidate |
| d5-m5-c000001 | 5 | 9 | 3.59518 | completed/correct | exact_single_candidate |
| d5-m5-c000002 | 5 | 6 | 1.93045 | completed/correct | exact_single_candidate |
| d5-m5-c000003 | 3 | 5 | 1.53755 | completed/correct | exact_single_candidate |
| d5-m5-c000004 | 5 | 15 | 6.70796 | completed/correct | exact_single_candidate |
| d5-m5-c000005 | 5 | 19 | 5.54356 | completed/correct | exact_single_candidate |
| d5-m5-c000006 | 3 | 8 | 2.19695 | completed/correct | exact_single_candidate |
| d5-m5-c000007 | 5 | 3 | 1.52156 | completed/correct | exact_single_candidate |
| d5-m5-c000008 | 4 | 13 | 3.87321 | completed/correct | exact_single_candidate |
| d5-m5-c000009 | 5 | 3 | 1.93166 | completed/correct | exact_single_candidate |
| d5-m5-c000010 | 3 | 18 | 4.6963 | completed/correct | exact_single_candidate |
| d5-m5-c000011 | 5 | 10 | 3.23393 | completed/correct | exact_single_candidate |
| d5-m5-c000012 | 4 | 4 | 1.57851 | completed/correct | exact_single_candidate |
| d5-m5-c000013 | 3 | 31 | 7.15846 | completed/correct | exact_single_candidate |
| d5-m5-c000014 | 5 | 19 | 5.37872 | completed/correct | exact_single_candidate |
| d5-m5-c000015 | 5 | 6 | 2.05098 | completed/correct | exact_single_candidate |
| d5-m5-c000016 | 3 | 2 | 0.920624 | completed/correct | exact_single_candidate |
| d5-m5-c000017 | 4 | 4 | 1.51549 | completed/correct | exact_single_candidate |
| d5-m5-c000018 | 4 | 13 | 4.20389 | completed/correct | exact_single_candidate |
| d5-m5-c000019 | 4 | 9 | 2.60453 | completed/correct | exact_single_candidate |
| d5-m5-c000020 | 5 | 14 | 5.42814 | completed/correct | exact_single_candidate |
| d5-m5-c000021 | 5 | 25 | 6.50161 | completed/correct | exact_single_candidate |
| d5-m5-c000022 | 5 | 11 | 3.9281 | completed/correct | exact_single_candidate |
| d5-m5-c000023 | 5 | 7 | 2.73941 | completed/correct | exact_single_candidate |
| d5-m5-c000024 | 5 | 25 | 7.72706 | completed/correct | exact_single_candidate |
| d5-m5-c000025 | 5 | 27 | 6.84392 | completed/correct | exact_single_candidate |
| d5-m5-c000026 | 3 | 11 | 3.35786 | completed/correct | exact_single_candidate |
| d5-m5-c000027 | 4 | 6 | 1.75966 | completed/correct | exact_single_candidate |
| d5-m5-c000028 | 4 | 5 | 1.87456 | completed/correct | exact_single_candidate |
| d5-m5-c000029 | 4 | 8 | 2.19223 | completed/correct | exact_single_candidate |
| d5-m5-c000030 | 4 | 3 | 1.23072 | completed/correct | exact_single_candidate |
| d5-m5-c000031 | 4 | 6 | 1.85654 | completed/correct | exact_single_candidate |
| d5-m5-c000032 | 4 | 2 | 1.12475 | completed/correct | exact_single_candidate |
| d5-m5-c000033 | 3 | 3 | 1.08904 | completed/correct | exact_single_candidate |
| d5-m5-c000034 | 5 | 14 | 5.10764 | completed/correct | exact_single_candidate |
| d5-m5-c000035 | 4 | 12 | 3.17216 | completed/correct | exact_single_candidate |
| d5-m5-c000036 | 5 | 28 | 8.74798 | completed/correct | exact_single_candidate |
| d5-m5-c000037 | 4 | 24 | 6.05035 | completed/correct | exact_single_candidate |
| d5-m5-c000038 | 3 | 13 | 3.58835 | completed/correct | exact_single_candidate |
| d5-m5-c000039 | 5 | 7 | 2.84809 | completed/correct | exact_single_candidate |
| d5-m5-c000040 | 4 | 13 | 3.55758 | completed/correct | exact_single_candidate |
| d5-m5-c000041 | 4 | 3 | 1.27842 | completed/correct | exact_single_candidate |
| d5-m5-c000042 | 5 | 14 | 3.83926 | completed/correct | exact_single_candidate |
| d5-m5-c000043 | 5 | 5 | 1.78664 | completed/correct | exact_single_candidate |
| d5-m5-c000044 | 4 | 7 | 2.41811 | completed/correct | exact_single_candidate |
| d5-m5-c000045 | 4 | 2 | 1.03313 | completed/correct | exact_single_candidate |
| d5-m5-c000046 | 4 | 30 | 10.5836 | completed/correct | exact_single_candidate |
| d5-m5-c000047 | 4 | 9 | 3.81144 | completed/correct | exact_single_candidate |
| d5-m5-c000048 | 5 | 14 | 4.663 | completed/correct | exact_single_candidate |
| d5-m5-c000049 | 3 | 9 | 2.42942 | completed/correct | exact_single_candidate |
| d5-m5-c000050 | 5 | 5 | 1.92975 | completed/correct | exact_single_candidate |
| d5-m5-c000051 | 5 | 16 | 4.54499 | completed/correct | exact_single_candidate |
| d5-m5-c000052 | 4 | 8 | 2.76914 | completed/correct | exact_single_candidate |
| d5-m5-c000053 | 5 | 8 | 2.54499 | completed/correct | exact_single_candidate |
| d5-m5-c000054 | 5 | 10 | 2.97222 | completed/correct | exact_single_candidate |
| d5-m5-c000055 | 5 | 7 | 1.89161 | completed/correct | exact_single_candidate |
| d5-m5-c000056 | 3 | 12 | 2.80087 | completed/correct | exact_single_candidate |
| d5-m5-c000057 | 4 | 3 | 1.27658 | completed/correct | exact_single_candidate |
| d5-m5-c000058 | 5 | 24 | 9.68353 | completed/correct | exact_single_candidate |
| d5-m5-c000059 | 4 | 4 | 1.45008 | completed/correct | exact_single_candidate |
| d5-m5-c000060 | 5 | 11 | 3.53753 | completed/correct | exact_single_candidate |
| d5-m5-c000061 | 5 | 19 | 6.8829 | completed/correct | exact_single_candidate |
| d5-m5-c000062 | 4 | 6 | 1.78719 | completed/correct | exact_single_candidate |
| d5-m5-c000063 | 4 | 6 | 2.23482 | completed/correct | exact_single_candidate |
| d5-m5-c000064 | 3 | 13 | 3.03313 | completed/correct | exact_single_candidate |
| d5-m5-c000065 | 3 | 9 | 2.04898 | completed/correct | exact_single_candidate |
| d5-m5-c000066 | 5 | 19 | 4.80067 | completed/correct | exact_single_candidate |
| d5-m5-c000067 | 3 | 19 | 4.80568 | completed/correct | exact_single_candidate |
| d5-m5-c000068 | 4 | 5 | 1.78217 | completed/correct | exact_single_candidate |
| d5-m5-c000069 | 3 | 3 | 1.05018 | completed/correct | exact_single_candidate |
| d5-m5-c000070 | 4 | 45 | 13.7519 | completed/correct | exact_single_candidate |
| d5-m5-c000071 | 5 | 21 | 6.35211 | completed/correct | exact_single_candidate |
| d5-m5-c000072 | 5 | 5 | 2.04343 | completed/correct | exact_single_candidate |
| d5-m5-c000073 | 3 | 3 | 1.14902 | completed/correct | exact_single_candidate |
| d5-m5-c000074 | 3 | 3 | 1.03493 | completed/correct | exact_single_candidate |
| d5-m5-c000075 | 3 | 6 | 1.48451 | completed/correct | exact_single_candidate |
| d5-m5-c000076 | 3 | 2 | 0.920173 | completed/correct | exact_single_candidate |
| d5-m5-c000077 | 4 | 16 | 4.32362 | completed/correct | exact_single_candidate |
| d5-m5-c000078 | 3 | 27 | 9.55333 | completed/correct | exact_single_candidate |
| d5-m5-c000079 | 3 | 12 | 3.38579 | completed/correct | exact_single_candidate |
| d5-m5-c000080 | 4 | 4 | 1.38915 | completed/correct | exact_single_candidate |
| d5-m5-c000081 | 4 | 10 | 2.55805 | completed/correct | exact_single_candidate |
| d5-m5-c000082 | 4 | 14 | 3.72279 | completed/correct | exact_single_candidate |
| d5-m5-c000083 | 5 | 4 | 1.57993 | completed/correct | exact_single_candidate |
| d5-m5-c000084 | 4 | 9 | 3.39746 | completed/correct | exact_single_candidate |
| d5-m5-c000085 | 4 | 7 | 1.92562 | completed/correct | exact_single_candidate |
| d5-m5-c000086 | 3 | 2 | 0.993058 | completed/correct | exact_single_candidate |
| d5-m5-c000087 | 3 | 2 | 1.01912 | completed/correct | exact_single_candidate |
| d5-m5-c000088 | 3 | 12 | 3.48306 | completed/correct | exact_single_candidate |
| d5-m5-c000089 | 5 | 5 | 1.76199 | completed/correct | exact_single_candidate |
| d5-m5-c000090 | 5 | 17 | 4.39304 | completed/correct | exact_single_candidate |
| d5-m5-c000091 | 5 | 24 | 6.06733 | completed/correct | exact_single_candidate |
| d5-m5-c000092 | 5 | 10 | 3.47661 | completed/correct | exact_single_candidate |
| d5-m5-c000093 | 3 | 2 | 0.909514 | completed/correct | exact_single_candidate |
| d5-m5-c000094 | 4 | 15 | 3.82365 | completed/correct | exact_single_candidate |
| d5-m5-c000095 | 5 | 9 | 3.65719 | completed/correct | exact_single_candidate |
| d5-m5-c000096 | 3 | 12 | 2.80032 | completed/correct | exact_single_candidate |
| d5-m5-c000097 | 4 | 8 | 3.21489 | completed/correct | exact_single_candidate |
| d5-m5-c000098 | 4 | 24 | 6.97607 | completed/correct | exact_single_candidate |
| d5-m5-c000099 | 4 | 13 | 4.10985 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `133061ab663f37931e551d101335a3f2ca668e458ad3b41e8d5cb1d72022c519`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
