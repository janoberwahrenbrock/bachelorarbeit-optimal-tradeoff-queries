# d3-a5-n100-h2-grid5-grid-plus-ratio-countdown-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
countdown, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 8 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 3.27 | 327 |
| Queries, korrekte Lösungen | 100 | 3.27 | 327 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 3.27 | 327 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 0.609621 | 60.9621 |
| API-Sekunden, korrekte Lösungen | 100 | 0.609621 | 60.9621 |
| Controller-Sekunden, sämtliche Versuche | 100 | 1.15384 | 115.384 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d3-m5-c000000, d3-m5-c000013, d3-m5-c000016, d3-m5-c000019, d3-m5-c000047, d3-m5-c000066, d3-m5-c000067, d3-m5-c000075, d3-m5-c000099

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d3-m5-c000000 | 4 | 8 | 1.01504 | completed/correct | exact_single_candidate |
| d3-m5-c000001 | 4 | 2 | 0.636472 | completed/correct | exact_single_candidate |
| d3-m5-c000002 | 4 | 4 | 0.674245 | completed/correct | exact_single_candidate |
| d3-m5-c000003 | 3 | 4 | 0.609368 | completed/correct | exact_single_candidate |
| d3-m5-c000004 | 4 | 2 | 0.572475 | completed/correct | exact_single_candidate |
| d3-m5-c000005 | 2 | 2 | 0.513454 | completed/correct | exact_single_candidate |
| d3-m5-c000006 | 5 | 2 | 0.737588 | completed/correct | exact_single_candidate |
| d3-m5-c000007 | 3 | 2 | 0.536418 | completed/correct | exact_single_candidate |
| d3-m5-c000008 | 4 | 2 | 0.585918 | completed/correct | exact_single_candidate |
| d3-m5-c000009 | 4 | 2 | 0.594369 | completed/correct | exact_single_candidate |
| d3-m5-c000010 | 2 | 1 | 0.476068 | completed/correct | exact_single_candidate |
| d3-m5-c000011 | 2 | 1 | 0.471232 | completed/correct | exact_single_candidate |
| d3-m5-c000012 | 4 | 4 | 0.761409 | completed/correct | exact_single_candidate |
| d3-m5-c000013 | 4 | 6 | 0.837663 | completed/correct | exact_single_candidate |
| d3-m5-c000014 | 4 | 2 | 0.563939 | completed/correct | exact_single_candidate |
| d3-m5-c000015 | 3 | 2 | 0.53866 | completed/correct | exact_single_candidate |
| d3-m5-c000016 | 4 | 12 | 1.20908 | completed/correct | exact_single_candidate |
| d3-m5-c000017 | 4 | 3 | 0.660347 | completed/correct | exact_single_candidate |
| d3-m5-c000018 | 2 | 4 | 0.586557 | completed/correct | exact_single_candidate |
| d3-m5-c000019 | 3 | 12 | 1.04643 | completed/correct | exact_single_candidate |
| d3-m5-c000020 | 4 | 2 | 0.586759 | completed/correct | exact_single_candidate |
| d3-m5-c000021 | 3 | 2 | 0.541926 | completed/correct | exact_single_candidate |
| d3-m5-c000022 | 3 | 2 | 0.539623 | completed/correct | exact_single_candidate |
| d3-m5-c000023 | 4 | 2 | 0.584766 | completed/correct | exact_single_candidate |
| d3-m5-c000024 | 3 | 4 | 0.651454 | completed/correct | exact_single_candidate |
| d3-m5-c000025 | 1 | 0 | 0.0245936 | completed/correct | exact_single_candidate |
| d3-m5-c000026 | 2 | 2 | 0.591976 | completed/correct | exact_single_candidate |
| d3-m5-c000027 | 2 | 2 | 0.498511 | completed/correct | exact_single_candidate |
| d3-m5-c000028 | 3 | 2 | 0.538175 | completed/correct | exact_single_candidate |
| d3-m5-c000029 | 5 | 3 | 0.670801 | completed/correct | exact_single_candidate |
| d3-m5-c000030 | 3 | 2 | 0.646676 | completed/correct | exact_single_candidate |
| d3-m5-c000031 | 2 | 2 | 0.503644 | completed/correct | exact_single_candidate |
| d3-m5-c000032 | 3 | 2 | 0.524447 | completed/correct | exact_single_candidate |
| d3-m5-c000033 | 3 | 4 | 0.608387 | completed/correct | exact_single_candidate |
| d3-m5-c000034 | 4 | 2 | 0.558927 | completed/correct | exact_single_candidate |
| d3-m5-c000035 | 2 | 1 | 0.474682 | completed/correct | exact_single_candidate |
| d3-m5-c000036 | 3 | 2 | 0.537113 | completed/correct | exact_single_candidate |
| d3-m5-c000037 | 3 | 2 | 0.538052 | completed/correct | exact_single_candidate |
| d3-m5-c000038 | 3 | 2 | 0.532524 | completed/correct | exact_single_candidate |
| d3-m5-c000039 | 3 | 4 | 0.615976 | completed/correct | exact_single_candidate |
| d3-m5-c000040 | 4 | 2 | 0.592173 | completed/correct | exact_single_candidate |
| d3-m5-c000041 | 5 | 4 | 0.732084 | completed/correct | exact_single_candidate |
| d3-m5-c000042 | 3 | 4 | 0.610387 | completed/correct | exact_single_candidate |
| d3-m5-c000043 | 3 | 2 | 0.510548 | completed/correct | exact_single_candidate |
| d3-m5-c000044 | 3 | 4 | 0.672891 | completed/correct | exact_single_candidate |
| d3-m5-c000045 | 4 | 2 | 0.60181 | completed/correct | exact_single_candidate |
| d3-m5-c000046 | 3 | 2 | 0.514363 | completed/correct | exact_single_candidate |
| d3-m5-c000047 | 4 | 10 | 0.979897 | completed/correct | exact_single_candidate |
| d3-m5-c000048 | 2 | 4 | 0.593938 | completed/correct | exact_single_candidate |
| d3-m5-c000049 | 2 | 2 | 0.49391 | completed/correct | exact_single_candidate |
| d3-m5-c000050 | 3 | 4 | 0.629251 | completed/correct | exact_single_candidate |
| d3-m5-c000051 | 3 | 4 | 0.647543 | completed/correct | exact_single_candidate |
| d3-m5-c000052 | 4 | 4 | 0.73075 | completed/correct | exact_single_candidate |
| d3-m5-c000053 | 4 | 2 | 0.590577 | completed/correct | exact_single_candidate |
| d3-m5-c000054 | 3 | 2 | 0.525789 | completed/correct | exact_single_candidate |
| d3-m5-c000055 | 4 | 4 | 0.695879 | completed/correct | exact_single_candidate |
| d3-m5-c000056 | 3 | 4 | 0.629488 | completed/correct | exact_single_candidate |
| d3-m5-c000057 | 3 | 4 | 0.738724 | completed/correct | exact_single_candidate |
| d3-m5-c000058 | 2 | 4 | 0.592653 | completed/correct | exact_single_candidate |
| d3-m5-c000059 | 3 | 2 | 0.535323 | completed/correct | exact_single_candidate |
| d3-m5-c000060 | 3 | 2 | 0.515915 | completed/correct | exact_single_candidate |
| d3-m5-c000061 | 4 | 4 | 0.651928 | completed/correct | exact_single_candidate |
| d3-m5-c000062 | 3 | 4 | 0.627816 | completed/correct | exact_single_candidate |
| d3-m5-c000063 | 3 | 2 | 0.530635 | completed/correct | exact_single_candidate |
| d3-m5-c000064 | 4 | 4 | 0.674196 | completed/correct | exact_single_candidate |
| d3-m5-c000065 | 2 | 2 | 0.492584 | completed/correct | exact_single_candidate |
| d3-m5-c000066 | 3 | 8 | 0.866049 | completed/correct | exact_single_candidate |
| d3-m5-c000067 | 4 | 16 | 1.44879 | completed/correct | exact_single_candidate |
| d3-m5-c000068 | 3 | 6 | 0.739867 | completed/correct | exact_single_candidate |
| d3-m5-c000069 | 2 | 2 | 0.49216 | completed/correct | exact_single_candidate |
| d3-m5-c000070 | 2 | 4 | 0.585038 | completed/correct | exact_single_candidate |
| d3-m5-c000071 | 4 | 2 | 0.577955 | completed/correct | exact_single_candidate |
| d3-m5-c000072 | 2 | 4 | 0.58182 | completed/correct | exact_single_candidate |
| d3-m5-c000073 | 3 | 2 | 0.509482 | completed/correct | exact_single_candidate |
| d3-m5-c000074 | 3 | 2 | 0.539735 | completed/correct | exact_single_candidate |
| d3-m5-c000075 | 4 | 8 | 0.936264 | completed/correct | exact_single_candidate |
| d3-m5-c000076 | 2 | 2 | 0.489858 | completed/correct | exact_single_candidate |
| d3-m5-c000077 | 3 | 2 | 0.514608 | completed/correct | exact_single_candidate |
| d3-m5-c000078 | 3 | 2 | 0.52879 | completed/correct | exact_single_candidate |
| d3-m5-c000079 | 3 | 2 | 0.534272 | completed/correct | exact_single_candidate |
| d3-m5-c000080 | 2 | 2 | 0.503172 | completed/correct | exact_single_candidate |
| d3-m5-c000081 | 3 | 2 | 0.53928 | completed/correct | exact_single_candidate |
| d3-m5-c000082 | 3 | 2 | 0.614287 | completed/correct | exact_single_candidate |
| d3-m5-c000083 | 3 | 4 | 0.593591 | completed/correct | exact_single_candidate |
| d3-m5-c000084 | 2 | 2 | 0.490678 | completed/correct | exact_single_candidate |
| d3-m5-c000085 | 2 | 4 | 0.57199 | completed/correct | exact_single_candidate |
| d3-m5-c000086 | 3 | 2 | 0.516555 | completed/correct | exact_single_candidate |
| d3-m5-c000087 | 2 | 1 | 0.468822 | completed/correct | exact_single_candidate |
| d3-m5-c000088 | 3 | 2 | 0.51967 | completed/correct | exact_single_candidate |
| d3-m5-c000089 | 3 | 2 | 0.515154 | completed/correct | exact_single_candidate |
| d3-m5-c000090 | 3 | 2 | 0.566606 | completed/correct | exact_single_candidate |
| d3-m5-c000091 | 4 | 4 | 0.627699 | completed/correct | exact_single_candidate |
| d3-m5-c000092 | 3 | 2 | 0.516867 | completed/correct | exact_single_candidate |
| d3-m5-c000093 | 4 | 4 | 0.681763 | completed/correct | exact_single_candidate |
| d3-m5-c000094 | 4 | 4 | 0.641833 | completed/correct | exact_single_candidate |
| d3-m5-c000095 | 4 | 2 | 0.57824 | completed/correct | exact_single_candidate |
| d3-m5-c000096 | 1 | 0 | 0.0244899 | completed/correct | exact_single_candidate |
| d3-m5-c000097 | 3 | 3 | 0.60435 | completed/correct | exact_single_candidate |
| d3-m5-c000098 | 3 | 2 | 0.520302 | completed/correct | exact_single_candidate |
| d3-m5-c000099 | 3 | 10 | 1.01532 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `04f2ff2c8b25440a8be0770c6ccd90c759d7a5dfd1e53ca9f7c0c05ed5132652`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
