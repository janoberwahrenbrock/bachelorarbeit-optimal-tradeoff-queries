# d3-a5-n100-h1-grid5-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
receding, H1, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 8 Worker, ein nativer Thread.

Korrekt: 70/100; regulär ungelöst: 30/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 2.42 | 242 |
| Queries, korrekte Lösungen | 70 | 2.01429 | 141 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 2.42 | 242 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 0.443149 | 44.3149 |
| API-Sekunden, korrekte Lösungen | 70 | 0.424112 | 29.6879 |
| Controller-Sekunden, sämtliche Versuche | 100 | 0.985139 | 98.5139 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d3-m5-c000024, d3-m5-c000038, d3-m5-c000042, d3-m5-c000051, d3-m5-c000056, d3-m5-c000066, d3-m5-c000079, d3-m5-c000099

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d3-m5-c000000 | 4 | 5 | 0.550301 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000001 | 4 | 2 | 0.458638 | completed/correct | exact_single_candidate |
| d3-m5-c000002 | 4 | 3 | 0.478421 | completed/correct | exact_single_candidate |
| d3-m5-c000003 | 3 | 2 | 0.400244 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000004 | 4 | 2 | 0.46149 | completed/correct | exact_single_candidate |
| d3-m5-c000005 | 2 | 1 | 0.34846 | completed/correct | exact_single_candidate |
| d3-m5-c000006 | 5 | 6 | 0.568515 | completed/correct | exact_single_candidate |
| d3-m5-c000007 | 3 | 1 | 0.410064 | completed/correct | exact_single_candidate |
| d3-m5-c000008 | 4 | 2 | 0.462934 | completed/correct | exact_single_candidate |
| d3-m5-c000009 | 4 | 2 | 0.456863 | completed/correct | exact_single_candidate |
| d3-m5-c000010 | 2 | 1 | 0.348362 | completed/correct | exact_single_candidate |
| d3-m5-c000011 | 2 | 1 | 0.359672 | completed/correct | exact_single_candidate |
| d3-m5-c000012 | 4 | 4 | 0.50624 | completed/correct | exact_single_candidate |
| d3-m5-c000013 | 4 | 5 | 0.543985 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000014 | 4 | 2 | 0.460249 | completed/correct | exact_single_candidate |
| d3-m5-c000015 | 3 | 2 | 0.426863 | completed/correct | exact_single_candidate |
| d3-m5-c000016 | 4 | 4 | 0.512213 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000017 | 4 | 3 | 0.488543 | completed/correct | exact_single_candidate |
| d3-m5-c000018 | 2 | 2 | 0.376225 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000019 | 3 | 2 | 0.401806 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000020 | 4 | 2 | 0.461104 | completed/correct | exact_single_candidate |
| d3-m5-c000021 | 3 | 2 | 0.431148 | completed/correct | exact_single_candidate |
| d3-m5-c000022 | 3 | 1 | 0.404558 | completed/correct | exact_single_candidate |
| d3-m5-c000023 | 4 | 2 | 0.463553 | completed/correct | exact_single_candidate |
| d3-m5-c000024 | 3 | 3 | 0.682564 | completed/correct | exact_single_candidate |
| d3-m5-c000025 | 1 | 0 | 0.0250194 | completed/correct | exact_single_candidate |
| d3-m5-c000026 | 2 | 1 | 0.345519 | completed/correct | exact_single_candidate |
| d3-m5-c000027 | 2 | 2 | 0.373788 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000028 | 3 | 2 | 0.427077 | completed/correct | exact_single_candidate |
| d3-m5-c000029 | 5 | 3 | 0.483609 | completed/correct | exact_single_candidate |
| d3-m5-c000030 | 3 | 3 | 0.454954 | completed/correct | exact_single_candidate |
| d3-m5-c000031 | 2 | 2 | 0.372477 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000032 | 3 | 2 | 0.398838 | completed/correct | exact_single_candidate |
| d3-m5-c000033 | 3 | 2 | 0.414146 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000034 | 4 | 2 | 0.43792 | completed/correct | exact_single_candidate |
| d3-m5-c000035 | 2 | 1 | 0.347417 | completed/correct | exact_single_candidate |
| d3-m5-c000036 | 3 | 1 | 0.406101 | completed/correct | exact_single_candidate |
| d3-m5-c000037 | 3 | 1 | 0.401723 | completed/correct | exact_single_candidate |
| d3-m5-c000038 | 3 | 4 | 0.658508 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000039 | 3 | 2 | 0.400036 | completed/correct | exact_single_candidate |
| d3-m5-c000040 | 4 | 5 | 0.548107 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000041 | 5 | 3 | 0.500451 | completed/correct | exact_single_candidate |
| d3-m5-c000042 | 3 | 4 | 0.656149 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000043 | 3 | 2 | 0.396973 | completed/correct | exact_single_candidate |
| d3-m5-c000044 | 3 | 4 | 0.473432 | completed/correct | exact_single_candidate |
| d3-m5-c000045 | 4 | 3 | 0.487849 | completed/correct | exact_single_candidate |
| d3-m5-c000046 | 3 | 2 | 0.398666 | completed/correct | exact_single_candidate |
| d3-m5-c000047 | 4 | 3 | 0.464028 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000048 | 2 | 2 | 0.370878 | completed/correct | exact_single_candidate |
| d3-m5-c000049 | 2 | 2 | 0.376627 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000050 | 3 | 4 | 0.483168 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000051 | 3 | 4 | 0.655752 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000052 | 4 | 3 | 0.485161 | completed/correct | exact_single_candidate |
| d3-m5-c000053 | 4 | 2 | 0.463049 | completed/correct | exact_single_candidate |
| d3-m5-c000054 | 3 | 5 | 0.504359 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000055 | 4 | 3 | 0.489647 | completed/correct | exact_single_candidate |
| d3-m5-c000056 | 3 | 2 | 0.651553 | completed/correct | exact_single_candidate |
| d3-m5-c000057 | 3 | 4 | 0.483391 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000058 | 2 | 2 | 0.376194 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000059 | 3 | 2 | 0.433969 | completed/correct | exact_single_candidate |
| d3-m5-c000060 | 3 | 2 | 0.396209 | completed/correct | exact_single_candidate |
| d3-m5-c000061 | 4 | 3 | 0.489564 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000062 | 3 | 3 | 0.463348 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000063 | 3 | 3 | 0.459591 | completed/correct | exact_single_candidate |
| d3-m5-c000064 | 4 | 4 | 0.504352 | completed/correct | exact_single_candidate |
| d3-m5-c000065 | 2 | 1 | 0.35095 | completed/correct | exact_single_candidate |
| d3-m5-c000066 | 3 | 4 | 0.667699 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000067 | 4 | 6 | 0.565022 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000068 | 3 | 4 | 0.4803 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000069 | 2 | 2 | 0.375258 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000070 | 2 | 2 | 0.379806 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000071 | 4 | 3 | 0.492873 | completed/correct | exact_single_candidate |
| d3-m5-c000072 | 2 | 2 | 0.375971 | completed/correct | exact_single_candidate |
| d3-m5-c000073 | 3 | 2 | 0.399344 | completed/correct | exact_single_candidate |
| d3-m5-c000074 | 3 | 2 | 0.432043 | completed/correct | exact_single_candidate |
| d3-m5-c000075 | 4 | 6 | 0.563652 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000076 | 2 | 1 | 0.345789 | completed/correct | exact_single_candidate |
| d3-m5-c000077 | 3 | 1 | 0.374284 | completed/correct | exact_single_candidate |
| d3-m5-c000078 | 3 | 1 | 0.410285 | completed/correct | exact_single_candidate |
| d3-m5-c000079 | 3 | 2 | 0.650843 | completed/correct | exact_single_candidate |
| d3-m5-c000080 | 2 | 2 | 0.369952 | completed/correct | exact_single_candidate |
| d3-m5-c000081 | 3 | 1 | 0.416739 | completed/correct | exact_single_candidate |
| d3-m5-c000082 | 3 | 2 | 0.396895 | completed/correct | exact_single_candidate |
| d3-m5-c000083 | 3 | 3 | 0.419904 | completed/correct | exact_single_candidate |
| d3-m5-c000084 | 2 | 1 | 0.346678 | completed/correct | exact_single_candidate |
| d3-m5-c000085 | 2 | 2 | 0.372243 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000086 | 3 | 1 | 0.377264 | completed/correct | exact_single_candidate |
| d3-m5-c000087 | 2 | 1 | 0.348992 | completed/correct | exact_single_candidate |
| d3-m5-c000088 | 3 | 1 | 0.401413 | completed/correct | exact_single_candidate |
| d3-m5-c000089 | 3 | 2 | 0.39227 | completed/correct | exact_single_candidate |
| d3-m5-c000090 | 3 | 2 | 0.395618 | completed/correct | exact_single_candidate |
| d3-m5-c000091 | 4 | 3 | 0.456059 | completed/regular_unsolved | insufficient_expected_progress |
| d3-m5-c000092 | 3 | 2 | 0.394247 | completed/correct | exact_single_candidate |
| d3-m5-c000093 | 4 | 2 | 0.458144 | completed/correct | exact_single_candidate |
| d3-m5-c000094 | 4 | 3 | 0.453265 | completed/correct | exact_single_candidate |
| d3-m5-c000095 | 4 | 3 | 0.488579 | completed/correct | exact_single_candidate |
| d3-m5-c000096 | 1 | 0 | 0.0247392 | completed/correct | exact_single_candidate |
| d3-m5-c000097 | 3 | 2 | 0.438036 | completed/correct | exact_single_candidate |
| d3-m5-c000098 | 3 | 1 | 0.414502 | completed/correct | exact_single_candidate |
| d3-m5-c000099 | 3 | 3 | 0.66259 | completed/regular_unsolved | insufficient_expected_progress |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `04f2ff2c8b25440a8be0770c6ccd90c759d7a5dfd1e53ca9f7c0c05ed5132652`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
