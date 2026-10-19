# d5-a5-n100-h2-grid20-grid-countdown-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
countdown, H2, Grid 20, Queryquelle grid, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 8.94 | 894 |
| Queries, korrekte Lösungen | 100 | 8.94 | 894 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 8.94 | 894 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 5.12321 | 512.321 |
| API-Sekunden, korrekte Lösungen | 100 | 5.12321 | 512.321 |
| Controller-Sekunden, sämtliche Versuche | 100 | 5.75954 | 575.954 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000014, d5-m5-c000025, d5-m5-c000036, d5-m5-c000046, d5-m5-c000058, d5-m5-c000067, d5-m5-c000070, d5-m5-c000071, d5-m5-c000098

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000000 | 2 | 8 | 2.51872 | completed/correct | exact_single_candidate |
| d5-m5-c000001 | 5 | 8 | 5.65077 | completed/correct | exact_single_candidate |
| d5-m5-c000002 | 5 | 6 | 3.65017 | completed/correct | exact_single_candidate |
| d5-m5-c000003 | 3 | 4 | 2.10691 | completed/correct | exact_single_candidate |
| d5-m5-c000004 | 5 | 10 | 10.2605 | completed/correct | exact_single_candidate |
| d5-m5-c000005 | 5 | 12 | 9.54802 | completed/correct | exact_single_candidate |
| d5-m5-c000006 | 3 | 8 | 3.61379 | completed/correct | exact_single_candidate |
| d5-m5-c000007 | 5 | 2 | 2.38193 | completed/correct | exact_single_candidate |
| d5-m5-c000008 | 4 | 17 | 9.88651 | completed/correct | exact_single_candidate |
| d5-m5-c000009 | 5 | 4 | 3.35129 | completed/correct | exact_single_candidate |
| d5-m5-c000010 | 3 | 2 | 1.48058 | completed/correct | exact_single_candidate |
| d5-m5-c000011 | 5 | 8 | 7.27148 | completed/correct | exact_single_candidate |
| d5-m5-c000012 | 4 | 6 | 2.79292 | completed/correct | exact_single_candidate |
| d5-m5-c000013 | 3 | 10 | 3.93268 | completed/correct | exact_single_candidate |
| d5-m5-c000014 | 5 | 26 | 12.2098 | completed/correct | exact_single_candidate |
| d5-m5-c000015 | 5 | 4 | 2.82482 | completed/correct | exact_single_candidate |
| d5-m5-c000016 | 3 | 2 | 1.36673 | completed/correct | exact_single_candidate |
| d5-m5-c000017 | 4 | 4 | 2.35752 | completed/correct | exact_single_candidate |
| d5-m5-c000018 | 4 | 8 | 3.575 | completed/correct | exact_single_candidate |
| d5-m5-c000019 | 4 | 4 | 2.65024 | completed/correct | exact_single_candidate |
| d5-m5-c000020 | 5 | 12 | 7.83837 | completed/correct | exact_single_candidate |
| d5-m5-c000021 | 5 | 12 | 6.77085 | completed/correct | exact_single_candidate |
| d5-m5-c000022 | 5 | 8 | 5.69853 | completed/correct | exact_single_candidate |
| d5-m5-c000023 | 5 | 4 | 3.52763 | completed/correct | exact_single_candidate |
| d5-m5-c000024 | 5 | 16 | 8.2027 | completed/correct | exact_single_candidate |
| d5-m5-c000025 | 5 | 28 | 14.9371 | completed/correct | exact_single_candidate |
| d5-m5-c000026 | 3 | 4 | 1.6004 | completed/correct | exact_single_candidate |
| d5-m5-c000027 | 4 | 4 | 2.27445 | completed/correct | exact_single_candidate |
| d5-m5-c000028 | 4 | 4 | 2.93576 | completed/correct | exact_single_candidate |
| d5-m5-c000029 | 4 | 8 | 3.99565 | completed/correct | exact_single_candidate |
| d5-m5-c000030 | 4 | 4 | 3.41165 | completed/correct | exact_single_candidate |
| d5-m5-c000031 | 4 | 4 | 2.40637 | completed/correct | exact_single_candidate |
| d5-m5-c000032 | 4 | 2 | 1.9905 | completed/correct | exact_single_candidate |
| d5-m5-c000033 | 3 | 2 | 1.48944 | completed/correct | exact_single_candidate |
| d5-m5-c000034 | 5 | 8 | 6.25679 | completed/correct | exact_single_candidate |
| d5-m5-c000035 | 4 | 4 | 2.31852 | completed/correct | exact_single_candidate |
| d5-m5-c000036 | 5 | 26 | 15.9768 | completed/correct | exact_single_candidate |
| d5-m5-c000037 | 4 | 6 | 3.0536 | completed/correct | exact_single_candidate |
| d5-m5-c000038 | 3 | 8 | 4.35449 | completed/correct | exact_single_candidate |
| d5-m5-c000039 | 5 | 6 | 4.73545 | completed/correct | exact_single_candidate |
| d5-m5-c000040 | 4 | 8 | 4.03248 | completed/correct | exact_single_candidate |
| d5-m5-c000041 | 4 | 4 | 2.42298 | completed/correct | exact_single_candidate |
| d5-m5-c000042 | 5 | 4 | 2.804 | completed/correct | exact_single_candidate |
| d5-m5-c000043 | 5 | 4 | 2.60998 | completed/correct | exact_single_candidate |
| d5-m5-c000044 | 4 | 12 | 5.95513 | completed/correct | exact_single_candidate |
| d5-m5-c000045 | 4 | 2 | 1.81105 | completed/correct | exact_single_candidate |
| d5-m5-c000046 | 4 | 38 | 24.9713 | completed/correct | exact_single_candidate |
| d5-m5-c000047 | 4 | 8 | 5.37136 | completed/correct | exact_single_candidate |
| d5-m5-c000048 | 5 | 10 | 6.65484 | completed/correct | exact_single_candidate |
| d5-m5-c000049 | 3 | 6 | 2.6582 | completed/correct | exact_single_candidate |
| d5-m5-c000050 | 5 | 4 | 3.45151 | completed/correct | exact_single_candidate |
| d5-m5-c000051 | 5 | 6 | 4.54274 | completed/correct | exact_single_candidate |
| d5-m5-c000052 | 4 | 6 | 2.66554 | completed/correct | exact_single_candidate |
| d5-m5-c000053 | 5 | 6 | 3.71949 | completed/correct | exact_single_candidate |
| d5-m5-c000054 | 5 | 6 | 3.65783 | completed/correct | exact_single_candidate |
| d5-m5-c000055 | 5 | 4 | 2.3663 | completed/correct | exact_single_candidate |
| d5-m5-c000056 | 3 | 12 | 4.69634 | completed/correct | exact_single_candidate |
| d5-m5-c000057 | 4 | 4 | 2.14406 | completed/correct | exact_single_candidate |
| d5-m5-c000058 | 5 | 24 | 16.2803 | completed/correct | exact_single_candidate |
| d5-m5-c000059 | 4 | 4 | 2.50597 | completed/correct | exact_single_candidate |
| d5-m5-c000060 | 5 | 12 | 7.17425 | completed/correct | exact_single_candidate |
| d5-m5-c000061 | 5 | 6 | 3.48485 | completed/correct | exact_single_candidate |
| d5-m5-c000062 | 4 | 6 | 3.10546 | completed/correct | exact_single_candidate |
| d5-m5-c000063 | 4 | 4 | 2.33395 | completed/correct | exact_single_candidate |
| d5-m5-c000064 | 3 | 6 | 2.62076 | completed/correct | exact_single_candidate |
| d5-m5-c000065 | 3 | 12 | 5.0768 | completed/correct | exact_single_candidate |
| d5-m5-c000066 | 5 | 8 | 4.65484 | completed/correct | exact_single_candidate |
| d5-m5-c000067 | 3 | 28 | 12.2394 | completed/correct | exact_single_candidate |
| d5-m5-c000068 | 4 | 2 | 1.87252 | completed/correct | exact_single_candidate |
| d5-m5-c000069 | 3 | 2 | 1.26956 | completed/correct | exact_single_candidate |
| d5-m5-c000070 | 4 | 50 | 27.409 | completed/correct | exact_single_candidate |
| d5-m5-c000071 | 5 | 30 | 15.1833 | completed/correct | exact_single_candidate |
| d5-m5-c000072 | 5 | 4 | 2.99882 | completed/correct | exact_single_candidate |
| d5-m5-c000073 | 3 | 4 | 1.90459 | completed/correct | exact_single_candidate |
| d5-m5-c000074 | 3 | 4 | 1.66992 | completed/correct | exact_single_candidate |
| d5-m5-c000075 | 3 | 10 | 4.24583 | completed/correct | exact_single_candidate |
| d5-m5-c000076 | 3 | 2 | 1.49267 | completed/correct | exact_single_candidate |
| d5-m5-c000077 | 4 | 10 | 4.48294 | completed/correct | exact_single_candidate |
| d5-m5-c000078 | 3 | 20 | 10.8436 | completed/correct | exact_single_candidate |
| d5-m5-c000079 | 3 | 4 | 1.88923 | completed/correct | exact_single_candidate |
| d5-m5-c000080 | 4 | 6 | 2.9444 | completed/correct | exact_single_candidate |
| d5-m5-c000081 | 4 | 4 | 2.18578 | completed/correct | exact_single_candidate |
| d5-m5-c000082 | 4 | 8 | 3.96163 | completed/correct | exact_single_candidate |
| d5-m5-c000083 | 5 | 6 | 4.04345 | completed/correct | exact_single_candidate |
| d5-m5-c000084 | 4 | 6 | 2.6571 | completed/correct | exact_single_candidate |
| d5-m5-c000085 | 4 | 2 | 2.06221 | completed/correct | exact_single_candidate |
| d5-m5-c000086 | 3 | 2 | 1.67504 | completed/correct | exact_single_candidate |
| d5-m5-c000087 | 3 | 2 | 1.54805 | completed/correct | exact_single_candidate |
| d5-m5-c000088 | 3 | 4 | 1.94285 | completed/correct | exact_single_candidate |
| d5-m5-c000089 | 5 | 4 | 3.02092 | completed/correct | exact_single_candidate |
| d5-m5-c000090 | 5 | 24 | 10.4434 | completed/correct | exact_single_candidate |
| d5-m5-c000091 | 5 | 16 | 7.27162 | completed/correct | exact_single_candidate |
| d5-m5-c000092 | 5 | 16 | 8.90629 | completed/correct | exact_single_candidate |
| d5-m5-c000093 | 3 | 2 | 1.48787 | completed/correct | exact_single_candidate |
| d5-m5-c000094 | 4 | 15 | 6.40823 | completed/correct | exact_single_candidate |
| d5-m5-c000095 | 5 | 6 | 5.38485 | completed/correct | exact_single_candidate |
| d5-m5-c000096 | 3 | 2 | 1.24171 | completed/correct | exact_single_candidate |
| d5-m5-c000097 | 4 | 4 | 2.75229 | completed/correct | exact_single_candidate |
| d5-m5-c000098 | 4 | 30 | 15.9119 | completed/correct | exact_single_candidate |
| d5-m5-c000099 | 4 | 16 | 7.99267 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `133061ab663f37931e551d101335a3f2ca668e458ad3b41e8d5cb1d72022c519`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
