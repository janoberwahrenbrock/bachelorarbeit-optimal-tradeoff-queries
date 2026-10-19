# d5-a10-n100-h2-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
adaptive, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 10.37 | 1037 |
| Queries, korrekte Lösungen | 100 | 10.37 | 1037 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 10.37 | 1037 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 6.06881 | 606.881 |
| API-Sekunden, korrekte Lösungen | 100 | 6.06881 | 606.881 |
| Controller-Sekunden, sämtliche Versuche | 100 | 6.78884 | 678.884 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m10-c000013, d5-m10-c000027, d5-m10-c000029, d5-m10-c000065, d5-m10-c000074, d5-m10-c000095

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m10-c000000 | 5 | 7 | 3.08192 | completed/correct | exact_single_candidate |
| d5-m10-c000001 | 8 | 15 | 7.43338 | completed/correct | exact_single_candidate |
| d5-m10-c000002 | 8 | 14 | 7.24812 | completed/correct | exact_single_candidate |
| d5-m10-c000003 | 5 | 10 | 5.37357 | completed/correct | exact_single_candidate |
| d5-m10-c000004 | 8 | 11 | 6.97818 | completed/correct | exact_single_candidate |
| d5-m10-c000005 | 10 | 12 | 6.80955 | completed/correct | exact_single_candidate |
| d5-m10-c000006 | 7 | 10 | 9.55325 | completed/correct | exact_single_candidate |
| d5-m10-c000007 | 5 | 24 | 8.23328 | completed/correct | exact_single_candidate |
| d5-m10-c000008 | 6 | 7 | 2.94181 | completed/correct | exact_single_candidate |
| d5-m10-c000009 | 8 | 10 | 6.09641 | completed/correct | exact_single_candidate |
| d5-m10-c000010 | 7 | 7 | 3.76855 | completed/correct | exact_single_candidate |
| d5-m10-c000011 | 9 | 6 | 4.31624 | completed/correct | exact_single_candidate |
| d5-m10-c000012 | 10 | 7 | 7.05754 | completed/correct | exact_single_candidate |
| d5-m10-c000013 | 6 | 24 | 14.8098 | completed/correct | exact_single_candidate |
| d5-m10-c000014 | 5 | 6 | 3.70966 | completed/correct | exact_single_candidate |
| d5-m10-c000015 | 6 | 6 | 3.59355 | completed/correct | exact_single_candidate |
| d5-m10-c000016 | 3 | 3 | 1.34017 | completed/correct | exact_single_candidate |
| d5-m10-c000017 | 5 | 11 | 4.3209 | completed/correct | exact_single_candidate |
| d5-m10-c000018 | 7 | 4 | 4.09384 | completed/correct | exact_single_candidate |
| d5-m10-c000019 | 5 | 5 | 2.33415 | completed/correct | exact_single_candidate |
| d5-m10-c000020 | 6 | 16 | 6.60045 | completed/correct | exact_single_candidate |
| d5-m10-c000021 | 7 | 8 | 4.4241 | completed/correct | exact_single_candidate |
| d5-m10-c000022 | 7 | 9 | 8.27903 | completed/correct | exact_single_candidate |
| d5-m10-c000023 | 7 | 7 | 3.70444 | completed/correct | exact_single_candidate |
| d5-m10-c000024 | 6 | 3 | 2.04086 | completed/correct | exact_single_candidate |
| d5-m10-c000025 | 9 | 12 | 6.91533 | completed/correct | exact_single_candidate |
| d5-m10-c000026 | 5 | 10 | 3.36943 | completed/correct | exact_single_candidate |
| d5-m10-c000027 | 8 | 17 | 15.3708 | completed/correct | exact_single_candidate |
| d5-m10-c000028 | 9 | 21 | 12.9017 | completed/correct | exact_single_candidate |
| d5-m10-c000029 | 8 | 35 | 19.0709 | completed/correct | exact_single_candidate |
| d5-m10-c000030 | 7 | 7 | 3.32768 | completed/correct | exact_single_candidate |
| d5-m10-c000031 | 6 | 4 | 2.30111 | completed/correct | exact_single_candidate |
| d5-m10-c000032 | 9 | 9 | 11.8952 | completed/correct | exact_single_candidate |
| d5-m10-c000033 | 7 | 12 | 9.02126 | completed/correct | exact_single_candidate |
| d5-m10-c000034 | 9 | 8 | 9.03834 | completed/correct | exact_single_candidate |
| d5-m10-c000035 | 4 | 5 | 2.06234 | completed/correct | exact_single_candidate |
| d5-m10-c000036 | 6 | 3 | 2.21422 | completed/correct | exact_single_candidate |
| d5-m10-c000037 | 6 | 9 | 3.47004 | completed/correct | exact_single_candidate |
| d5-m10-c000038 | 7 | 7 | 3.09659 | completed/correct | exact_single_candidate |
| d5-m10-c000039 | 5 | 35 | 12.3842 | completed/correct | exact_single_candidate |
| d5-m10-c000040 | 9 | 12 | 7.57172 | completed/correct | exact_single_candidate |
| d5-m10-c000041 | 6 | 5 | 3.32103 | completed/correct | exact_single_candidate |
| d5-m10-c000042 | 6 | 12 | 8.47811 | completed/correct | exact_single_candidate |
| d5-m10-c000043 | 8 | 5 | 4.41871 | completed/correct | exact_single_candidate |
| d5-m10-c000044 | 10 | 8 | 6.07611 | completed/correct | exact_single_candidate |
| d5-m10-c000045 | 8 | 15 | 5.751 | completed/correct | exact_single_candidate |
| d5-m10-c000046 | 6 | 4 | 3.23148 | completed/correct | exact_single_candidate |
| d5-m10-c000047 | 7 | 8 | 3.90851 | completed/correct | exact_single_candidate |
| d5-m10-c000048 | 7 | 14 | 6.66185 | completed/correct | exact_single_candidate |
| d5-m10-c000049 | 8 | 8 | 4.49834 | completed/correct | exact_single_candidate |
| d5-m10-c000050 | 9 | 7 | 9.31971 | completed/correct | exact_single_candidate |
| d5-m10-c000051 | 8 | 8 | 7.5042 | completed/correct | exact_single_candidate |
| d5-m10-c000052 | 7 | 5 | 2.72468 | completed/correct | exact_single_candidate |
| d5-m10-c000053 | 7 | 4 | 3.12635 | completed/correct | exact_single_candidate |
| d5-m10-c000054 | 6 | 4 | 2.33674 | completed/correct | exact_single_candidate |
| d5-m10-c000055 | 7 | 5 | 3.75389 | completed/correct | exact_single_candidate |
| d5-m10-c000056 | 7 | 14 | 8.65242 | completed/correct | exact_single_candidate |
| d5-m10-c000057 | 6 | 8 | 4.10503 | completed/correct | exact_single_candidate |
| d5-m10-c000058 | 8 | 6 | 4.57159 | completed/correct | exact_single_candidate |
| d5-m10-c000059 | 8 | 10 | 5.77032 | completed/correct | exact_single_candidate |
| d5-m10-c000060 | 6 | 24 | 9.80871 | completed/correct | exact_single_candidate |
| d5-m10-c000061 | 7 | 5 | 3.32984 | completed/correct | exact_single_candidate |
| d5-m10-c000062 | 6 | 6 | 4.93603 | completed/correct | exact_single_candidate |
| d5-m10-c000063 | 4 | 5 | 1.98002 | completed/correct | exact_single_candidate |
| d5-m10-c000064 | 7 | 20 | 9.3191 | completed/correct | exact_single_candidate |
| d5-m10-c000065 | 7 | 32 | 14.7034 | completed/correct | exact_single_candidate |
| d5-m10-c000066 | 8 | 7 | 5.55523 | completed/correct | exact_single_candidate |
| d5-m10-c000067 | 6 | 6 | 3.48046 | completed/correct | exact_single_candidate |
| d5-m10-c000068 | 6 | 13 | 5.35738 | completed/correct | exact_single_candidate |
| d5-m10-c000069 | 6 | 6 | 2.88299 | completed/correct | exact_single_candidate |
| d5-m10-c000070 | 5 | 3 | 1.85753 | completed/correct | exact_single_candidate |
| d5-m10-c000071 | 6 | 10 | 4.41698 | completed/correct | exact_single_candidate |
| d5-m10-c000072 | 8 | 12 | 5.99972 | completed/correct | exact_single_candidate |
| d5-m10-c000073 | 8 | 10 | 10.3149 | completed/correct | exact_single_candidate |
| d5-m10-c000074 | 9 | 16 | 19.3806 | completed/correct | exact_single_candidate |
| d5-m10-c000075 | 6 | 3 | 2.14354 | completed/correct | exact_single_candidate |
| d5-m10-c000076 | 7 | 17 | 9.53772 | completed/correct | exact_single_candidate |
| d5-m10-c000077 | 6 | 18 | 5.85492 | completed/correct | exact_single_candidate |
| d5-m10-c000078 | 7 | 11 | 8.2809 | completed/correct | exact_single_candidate |
| d5-m10-c000079 | 5 | 4 | 2.03836 | completed/correct | exact_single_candidate |
| d5-m10-c000080 | 8 | 9 | 7.13893 | completed/correct | exact_single_candidate |
| d5-m10-c000081 | 8 | 6 | 5.41194 | completed/correct | exact_single_candidate |
| d5-m10-c000082 | 6 | 2 | 1.83961 | completed/correct | exact_single_candidate |
| d5-m10-c000083 | 6 | 6 | 2.68035 | completed/correct | exact_single_candidate |
| d5-m10-c000084 | 6 | 18 | 5.83254 | completed/correct | exact_single_candidate |
| d5-m10-c000085 | 6 | 7 | 3.32195 | completed/correct | exact_single_candidate |
| d5-m10-c000086 | 8 | 3 | 3.13901 | completed/correct | exact_single_candidate |
| d5-m10-c000087 | 7 | 5 | 2.95685 | completed/correct | exact_single_candidate |
| d5-m10-c000088 | 8 | 8 | 3.80577 | completed/correct | exact_single_candidate |
| d5-m10-c000089 | 9 | 6 | 5.82417 | completed/correct | exact_single_candidate |
| d5-m10-c000090 | 6 | 5 | 2.7057 | completed/correct | exact_single_candidate |
| d5-m10-c000091 | 8 | 7 | 5.0973 | completed/correct | exact_single_candidate |
| d5-m10-c000092 | 6 | 5 | 2.60069 | completed/correct | exact_single_candidate |
| d5-m10-c000093 | 6 | 16 | 5.81992 | completed/correct | exact_single_candidate |
| d5-m10-c000094 | 7 | 15 | 6.76844 | completed/correct | exact_single_candidate |
| d5-m10-c000095 | 8 | 44 | 24.6704 | completed/correct | exact_single_candidate |
| d5-m10-c000096 | 7 | 9 | 6.02286 | completed/correct | exact_single_candidate |
| d5-m10-c000097 | 8 | 4 | 3.91928 | completed/correct | exact_single_candidate |
| d5-m10-c000098 | 7 | 15 | 7.15421 | completed/correct | exact_single_candidate |
| d5-m10-c000099 | 7 | 21 | 8.62876 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `0e134c0292a4dddc9a56cad99cafd0f3036279e9b1d47b80d2997bbd1e38b0cf`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
