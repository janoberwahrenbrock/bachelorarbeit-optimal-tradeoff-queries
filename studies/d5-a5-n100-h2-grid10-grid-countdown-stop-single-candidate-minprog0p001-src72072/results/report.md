# d5-a5-n100-h2-grid10-grid-countdown-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
countdown, H2, Grid 10, Queryquelle grid, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 8.62 | 862 |
| Queries, korrekte Lösungen | 100 | 8.62 | 862 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 8.62 | 862 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 3.03607 | 303.607 |
| API-Sekunden, korrekte Lösungen | 100 | 3.03607 | 303.607 |
| Controller-Sekunden, sämtliche Versuche | 100 | 3.67861 | 367.861 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000046, d5-m5-c000070

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000000 | 2 | 10 | 2.17935 | completed/correct | exact_single_candidate |
| d5-m5-c000001 | 5 | 12 | 5.12562 | completed/correct | exact_single_candidate |
| d5-m5-c000002 | 5 | 6 | 2.35185 | completed/correct | exact_single_candidate |
| d5-m5-c000003 | 3 | 4 | 1.4425 | completed/correct | exact_single_candidate |
| d5-m5-c000004 | 5 | 8 | 5.21727 | completed/correct | exact_single_candidate |
| d5-m5-c000005 | 5 | 10 | 4.22785 | completed/correct | exact_single_candidate |
| d5-m5-c000006 | 3 | 6 | 1.67329 | completed/correct | exact_single_candidate |
| d5-m5-c000007 | 5 | 4 | 2.05867 | completed/correct | exact_single_candidate |
| d5-m5-c000008 | 4 | 12 | 4.39646 | completed/correct | exact_single_candidate |
| d5-m5-c000009 | 5 | 4 | 2.04173 | completed/correct | exact_single_candidate |
| d5-m5-c000010 | 3 | 2 | 1.08555 | completed/correct | exact_single_candidate |
| d5-m5-c000011 | 5 | 8 | 4.16053 | completed/correct | exact_single_candidate |
| d5-m5-c000012 | 4 | 6 | 1.86552 | completed/correct | exact_single_candidate |
| d5-m5-c000013 | 3 | 11 | 2.65264 | completed/correct | exact_single_candidate |
| d5-m5-c000014 | 5 | 23 | 6.38126 | completed/correct | exact_single_candidate |
| d5-m5-c000015 | 5 | 4 | 1.82479 | completed/correct | exact_single_candidate |
| d5-m5-c000016 | 3 | 2 | 1.04243 | completed/correct | exact_single_candidate |
| d5-m5-c000017 | 4 | 4 | 1.58967 | completed/correct | exact_single_candidate |
| d5-m5-c000018 | 4 | 6 | 1.95156 | completed/correct | exact_single_candidate |
| d5-m5-c000019 | 4 | 6 | 2.22445 | completed/correct | exact_single_candidate |
| d5-m5-c000020 | 5 | 16 | 5.07902 | completed/correct | exact_single_candidate |
| d5-m5-c000021 | 5 | 12 | 3.79214 | completed/correct | exact_single_candidate |
| d5-m5-c000022 | 5 | 8 | 3.46531 | completed/correct | exact_single_candidate |
| d5-m5-c000023 | 5 | 4 | 2.17541 | completed/correct | exact_single_candidate |
| d5-m5-c000024 | 5 | 14 | 4.57752 | completed/correct | exact_single_candidate |
| d5-m5-c000025 | 5 | 22 | 6.26093 | completed/correct | exact_single_candidate |
| d5-m5-c000026 | 3 | 4 | 1.21262 | completed/correct | exact_single_candidate |
| d5-m5-c000027 | 4 | 4 | 1.53754 | completed/correct | exact_single_candidate |
| d5-m5-c000028 | 4 | 4 | 1.85681 | completed/correct | exact_single_candidate |
| d5-m5-c000029 | 4 | 8 | 2.43643 | completed/correct | exact_single_candidate |
| d5-m5-c000030 | 4 | 4 | 2.17936 | completed/correct | exact_single_candidate |
| d5-m5-c000031 | 4 | 4 | 1.69703 | completed/correct | exact_single_candidate |
| d5-m5-c000032 | 4 | 2 | 1.37202 | completed/correct | exact_single_candidate |
| d5-m5-c000033 | 3 | 2 | 1.11192 | completed/correct | exact_single_candidate |
| d5-m5-c000034 | 5 | 12 | 4.37688 | completed/correct | exact_single_candidate |
| d5-m5-c000035 | 4 | 8 | 2.38506 | completed/correct | exact_single_candidate |
| d5-m5-c000036 | 5 | 24 | 7.46257 | completed/correct | exact_single_candidate |
| d5-m5-c000037 | 4 | 8 | 2.34454 | completed/correct | exact_single_candidate |
| d5-m5-c000038 | 3 | 8 | 2.68578 | completed/correct | exact_single_candidate |
| d5-m5-c000039 | 5 | 6 | 2.85288 | completed/correct | exact_single_candidate |
| d5-m5-c000040 | 4 | 12 | 3.49849 | completed/correct | exact_single_candidate |
| d5-m5-c000041 | 4 | 4 | 1.61911 | completed/correct | exact_single_candidate |
| d5-m5-c000042 | 5 | 4 | 1.80485 | completed/correct | exact_single_candidate |
| d5-m5-c000043 | 5 | 4 | 1.87819 | completed/correct | exact_single_candidate |
| d5-m5-c000044 | 4 | 10 | 3.22848 | completed/correct | exact_single_candidate |
| d5-m5-c000045 | 4 | 2 | 1.27278 | completed/correct | exact_single_candidate |
| d5-m5-c000046 | 4 | 43 | 15.0943 | completed/correct | exact_single_candidate |
| d5-m5-c000047 | 4 | 10 | 3.99469 | completed/correct | exact_single_candidate |
| d5-m5-c000048 | 5 | 10 | 4.11234 | completed/correct | exact_single_candidate |
| d5-m5-c000049 | 3 | 6 | 1.71901 | completed/correct | exact_single_candidate |
| d5-m5-c000050 | 5 | 6 | 2.31187 | completed/correct | exact_single_candidate |
| d5-m5-c000051 | 5 | 6 | 2.82149 | completed/correct | exact_single_candidate |
| d5-m5-c000052 | 4 | 6 | 1.7843 | completed/correct | exact_single_candidate |
| d5-m5-c000053 | 5 | 6 | 2.47629 | completed/correct | exact_single_candidate |
| d5-m5-c000054 | 5 | 6 | 2.27791 | completed/correct | exact_single_candidate |
| d5-m5-c000055 | 5 | 4 | 1.80909 | completed/correct | exact_single_candidate |
| d5-m5-c000056 | 3 | 5 | 1.36342 | completed/correct | exact_single_candidate |
| d5-m5-c000057 | 4 | 4 | 1.43841 | completed/correct | exact_single_candidate |
| d5-m5-c000058 | 5 | 16 | 5.74555 | completed/correct | exact_single_candidate |
| d5-m5-c000059 | 4 | 4 | 1.65753 | completed/correct | exact_single_candidate |
| d5-m5-c000060 | 5 | 13 | 4.40159 | completed/correct | exact_single_candidate |
| d5-m5-c000061 | 5 | 10 | 3.04774 | completed/correct | exact_single_candidate |
| d5-m5-c000062 | 4 | 6 | 2.01579 | completed/correct | exact_single_candidate |
| d5-m5-c000063 | 4 | 6 | 1.94648 | completed/correct | exact_single_candidate |
| d5-m5-c000064 | 3 | 8 | 2.14979 | completed/correct | exact_single_candidate |
| d5-m5-c000065 | 3 | 8 | 2.0072 | completed/correct | exact_single_candidate |
| d5-m5-c000066 | 5 | 8 | 2.80021 | completed/correct | exact_single_candidate |
| d5-m5-c000067 | 3 | 18 | 4.53209 | completed/correct | exact_single_candidate |
| d5-m5-c000068 | 4 | 4 | 1.87172 | completed/correct | exact_single_candidate |
| d5-m5-c000069 | 3 | 4 | 1.24683 | completed/correct | exact_single_candidate |
| d5-m5-c000070 | 4 | 46 | 14.2245 | completed/correct | exact_single_candidate |
| d5-m5-c000071 | 5 | 18 | 6.9278 | completed/correct | exact_single_candidate |
| d5-m5-c000072 | 5 | 4 | 1.9441 | completed/correct | exact_single_candidate |
| d5-m5-c000073 | 3 | 4 | 1.4097 | completed/correct | exact_single_candidate |
| d5-m5-c000074 | 3 | 4 | 1.33351 | completed/correct | exact_single_candidate |
| d5-m5-c000075 | 3 | 8 | 2.20306 | completed/correct | exact_single_candidate |
| d5-m5-c000076 | 3 | 2 | 1.07631 | completed/correct | exact_single_candidate |
| d5-m5-c000077 | 4 | 6 | 1.90725 | completed/correct | exact_single_candidate |
| d5-m5-c000078 | 3 | 18 | 6.44017 | completed/correct | exact_single_candidate |
| d5-m5-c000079 | 3 | 4 | 1.46231 | completed/correct | exact_single_candidate |
| d5-m5-c000080 | 4 | 8 | 2.9778 | completed/correct | exact_single_candidate |
| d5-m5-c000081 | 4 | 4 | 1.50464 | completed/correct | exact_single_candidate |
| d5-m5-c000082 | 4 | 4 | 1.57612 | completed/correct | exact_single_candidate |
| d5-m5-c000083 | 5 | 6 | 2.53341 | completed/correct | exact_single_candidate |
| d5-m5-c000084 | 4 | 12 | 4.74992 | completed/correct | exact_single_candidate |
| d5-m5-c000085 | 4 | 4 | 1.83673 | completed/correct | exact_single_candidate |
| d5-m5-c000086 | 3 | 2 | 1.20284 | completed/correct | exact_single_candidate |
| d5-m5-c000087 | 3 | 2 | 1.14258 | completed/correct | exact_single_candidate |
| d5-m5-c000088 | 3 | 4 | 1.38843 | completed/correct | exact_single_candidate |
| d5-m5-c000089 | 5 | 4 | 2.08741 | completed/correct | exact_single_candidate |
| d5-m5-c000090 | 5 | 24 | 6.92553 | completed/correct | exact_single_candidate |
| d5-m5-c000091 | 5 | 15 | 4.03257 | completed/correct | exact_single_candidate |
| d5-m5-c000092 | 5 | 16 | 5.44493 | completed/correct | exact_single_candidate |
| d5-m5-c000093 | 3 | 2 | 1.03845 | completed/correct | exact_single_candidate |
| d5-m5-c000094 | 4 | 14 | 3.88355 | completed/correct | exact_single_candidate |
| d5-m5-c000095 | 5 | 6 | 3.21685 | completed/correct | exact_single_candidate |
| d5-m5-c000096 | 3 | 2 | 0.97616 | completed/correct | exact_single_candidate |
| d5-m5-c000097 | 4 | 6 | 2.35113 | completed/correct | exact_single_candidate |
| d5-m5-c000098 | 4 | 24 | 7.21795 | completed/correct | exact_single_candidate |
| d5-m5-c000099 | 4 | 14 | 4.30909 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `133061ab663f37931e551d101335a3f2ca668e458ad3b41e8d5cb1d72022c519`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
