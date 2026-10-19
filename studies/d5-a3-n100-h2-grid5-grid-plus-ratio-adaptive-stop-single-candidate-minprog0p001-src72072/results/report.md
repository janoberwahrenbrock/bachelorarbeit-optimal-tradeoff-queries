# d5-a3-n100-h2-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
adaptive, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 7.27 | 727 |
| Queries, korrekte Lösungen | 100 | 7.27 | 727 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 7.27 | 727 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 2.594 | 259.4 |
| API-Sekunden, korrekte Lösungen | 100 | 2.594 | 259.4 |
| Controller-Sekunden, sämtliche Versuche | 100 | 3.25304 | 325.304 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m3-c000001, d5-m3-c000014, d5-m3-c000063, d5-m3-c000070, d5-m3-c000083, d5-m3-c000088, d5-m3-c000090, d5-m3-c000097

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m3-c000000 | 3 | 10 | 4.44079 | completed/correct | exact_single_candidate |
| d5-m3-c000001 | 3 | 23 | 6.88177 | completed/correct | exact_single_candidate |
| d5-m3-c000002 | 3 | 4 | 2.14829 | completed/correct | exact_single_candidate |
| d5-m3-c000003 | 3 | 2 | 1.1777 | completed/correct | exact_single_candidate |
| d5-m3-c000004 | 3 | 6 | 2.3775 | completed/correct | exact_single_candidate |
| d5-m3-c000005 | 3 | 9 | 2.59787 | completed/correct | exact_single_candidate |
| d5-m3-c000006 | 3 | 8 | 2.33905 | completed/correct | exact_single_candidate |
| d5-m3-c000007 | 3 | 3 | 1.36432 | completed/correct | exact_single_candidate |
| d5-m3-c000008 | 3 | 8 | 2.57594 | completed/correct | exact_single_candidate |
| d5-m3-c000009 | 3 | 2 | 1.14094 | completed/correct | exact_single_candidate |
| d5-m3-c000010 | 3 | 12 | 3.71664 | completed/correct | exact_single_candidate |
| d5-m3-c000011 | 3 | 8 | 3.28546 | completed/correct | exact_single_candidate |
| d5-m3-c000012 | 3 | 7 | 3.41505 | completed/correct | exact_single_candidate |
| d5-m3-c000013 | 2 | 6 | 1.7603 | completed/correct | exact_single_candidate |
| d5-m3-c000014 | 3 | 20 | 6.21983 | completed/correct | exact_single_candidate |
| d5-m3-c000015 | 3 | 8 | 2.76766 | completed/correct | exact_single_candidate |
| d5-m3-c000016 | 3 | 3 | 1.34911 | completed/correct | exact_single_candidate |
| d5-m3-c000017 | 2 | 12 | 3.68739 | completed/correct | exact_single_candidate |
| d5-m3-c000018 | 3 | 3 | 1.34645 | completed/correct | exact_single_candidate |
| d5-m3-c000019 | 2 | 3 | 1.1463 | completed/correct | exact_single_candidate |
| d5-m3-c000020 | 3 | 2 | 1.17574 | completed/correct | exact_single_candidate |
| d5-m3-c000021 | 2 | 8 | 2.35125 | completed/correct | exact_single_candidate |
| d5-m3-c000022 | 3 | 3 | 1.30656 | completed/correct | exact_single_candidate |
| d5-m3-c000023 | 3 | 15 | 4.81395 | completed/correct | exact_single_candidate |
| d5-m3-c000024 | 3 | 4 | 1.78278 | completed/correct | exact_single_candidate |
| d5-m3-c000025 | 3 | 16 | 5.24407 | completed/correct | exact_single_candidate |
| d5-m3-c000026 | 3 | 8 | 2.44891 | completed/correct | exact_single_candidate |
| d5-m3-c000027 | 3 | 5 | 1.83222 | completed/correct | exact_single_candidate |
| d5-m3-c000028 | 2 | 1 | 0.918136 | completed/correct | exact_single_candidate |
| d5-m3-c000029 | 3 | 2 | 1.26534 | completed/correct | exact_single_candidate |
| d5-m3-c000030 | 3 | 9 | 2.54081 | completed/correct | exact_single_candidate |
| d5-m3-c000031 | 3 | 6 | 2.07956 | completed/correct | exact_single_candidate |
| d5-m3-c000032 | 3 | 4 | 1.85009 | completed/correct | exact_single_candidate |
| d5-m3-c000033 | 3 | 6 | 2.406 | completed/correct | exact_single_candidate |
| d5-m3-c000034 | 3 | 3 | 1.33314 | completed/correct | exact_single_candidate |
| d5-m3-c000035 | 3 | 4 | 1.75714 | completed/correct | exact_single_candidate |
| d5-m3-c000036 | 3 | 7 | 2.34524 | completed/correct | exact_single_candidate |
| d5-m3-c000037 | 2 | 10 | 2.77089 | completed/correct | exact_single_candidate |
| d5-m3-c000038 | 3 | 2 | 1.16072 | completed/correct | exact_single_candidate |
| d5-m3-c000039 | 3 | 8 | 2.32745 | completed/correct | exact_single_candidate |
| d5-m3-c000040 | 3 | 4 | 1.61806 | completed/correct | exact_single_candidate |
| d5-m3-c000041 | 3 | 11 | 2.97395 | completed/correct | exact_single_candidate |
| d5-m3-c000042 | 3 | 3 | 1.37196 | completed/correct | exact_single_candidate |
| d5-m3-c000043 | 3 | 8 | 3.1365 | completed/correct | exact_single_candidate |
| d5-m3-c000044 | 3 | 3 | 1.28113 | completed/correct | exact_single_candidate |
| d5-m3-c000045 | 2 | 9 | 2.66136 | completed/correct | exact_single_candidate |
| d5-m3-c000046 | 2 | 3 | 1.03829 | completed/correct | exact_single_candidate |
| d5-m3-c000047 | 3 | 5 | 1.64697 | completed/correct | exact_single_candidate |
| d5-m3-c000048 | 2 | 3 | 1.08162 | completed/correct | exact_single_candidate |
| d5-m3-c000049 | 3 | 7 | 2.24692 | completed/correct | exact_single_candidate |
| d5-m3-c000050 | 2 | 5 | 1.38518 | completed/correct | exact_single_candidate |
| d5-m3-c000051 | 3 | 3 | 1.33132 | completed/correct | exact_single_candidate |
| d5-m3-c000052 | 3 | 2 | 1.16491 | completed/correct | exact_single_candidate |
| d5-m3-c000053 | 2 | 18 | 5.37743 | completed/correct | exact_single_candidate |
| d5-m3-c000054 | 2 | 9 | 2.67277 | completed/correct | exact_single_candidate |
| d5-m3-c000055 | 2 | 1 | 0.935227 | completed/correct | exact_single_candidate |
| d5-m3-c000056 | 3 | 10 | 3.1129 | completed/correct | exact_single_candidate |
| d5-m3-c000057 | 3 | 2 | 1.2121 | completed/correct | exact_single_candidate |
| d5-m3-c000058 | 2 | 1 | 0.894892 | completed/correct | exact_single_candidate |
| d5-m3-c000059 | 3 | 10 | 2.98455 | completed/correct | exact_single_candidate |
| d5-m3-c000060 | 3 | 1 | 1.00862 | completed/correct | exact_single_candidate |
| d5-m3-c000061 | 3 | 11 | 3.38526 | completed/correct | exact_single_candidate |
| d5-m3-c000062 | 2 | 1 | 0.920882 | completed/correct | exact_single_candidate |
| d5-m3-c000063 | 3 | 27 | 9.23058 | completed/correct | exact_single_candidate |
| d5-m3-c000064 | 3 | 12 | 3.83057 | completed/correct | exact_single_candidate |
| d5-m3-c000065 | 2 | 7 | 2.1946 | completed/correct | exact_single_candidate |
| d5-m3-c000066 | 3 | 3 | 1.37187 | completed/correct | exact_single_candidate |
| d5-m3-c000067 | 3 | 5 | 1.93028 | completed/correct | exact_single_candidate |
| d5-m3-c000068 | 3 | 3 | 1.34703 | completed/correct | exact_single_candidate |
| d5-m3-c000069 | 3 | 9 | 2.81394 | completed/correct | exact_single_candidate |
| d5-m3-c000070 | 3 | 25 | 7.48253 | completed/correct | exact_single_candidate |
| d5-m3-c000071 | 3 | 15 | 5.04417 | completed/correct | exact_single_candidate |
| d5-m3-c000072 | 3 | 2 | 1.11888 | completed/correct | exact_single_candidate |
| d5-m3-c000073 | 2 | 2 | 0.906447 | completed/correct | exact_single_candidate |
| d5-m3-c000074 | 3 | 3 | 1.35529 | completed/correct | exact_single_candidate |
| d5-m3-c000075 | 2 | 1 | 0.931954 | completed/correct | exact_single_candidate |
| d5-m3-c000076 | 3 | 3 | 1.36911 | completed/correct | exact_single_candidate |
| d5-m3-c000077 | 3 | 12 | 3.83778 | completed/correct | exact_single_candidate |
| d5-m3-c000078 | 3 | 11 | 3.93169 | completed/correct | exact_single_candidate |
| d5-m3-c000079 | 3 | 6 | 2.4013 | completed/correct | exact_single_candidate |
| d5-m3-c000080 | 2 | 2 | 0.943072 | completed/correct | exact_single_candidate |
| d5-m3-c000081 | 3 | 4 | 1.65984 | completed/correct | exact_single_candidate |
| d5-m3-c000082 | 3 | 2 | 1.20366 | completed/correct | exact_single_candidate |
| d5-m3-c000083 | 3 | 19 | 6.39763 | completed/correct | exact_single_candidate |
| d5-m3-c000084 | 3 | 3 | 1.36672 | completed/correct | exact_single_candidate |
| d5-m3-c000085 | 3 | 9 | 3.58345 | completed/correct | exact_single_candidate |
| d5-m3-c000086 | 3 | 16 | 5.20733 | completed/correct | exact_single_candidate |
| d5-m3-c000087 | 3 | 4 | 1.53608 | completed/correct | exact_single_candidate |
| d5-m3-c000088 | 3 | 21 | 7.63829 | completed/correct | exact_single_candidate |
| d5-m3-c000089 | 3 | 2 | 1.36295 | completed/correct | exact_single_candidate |
| d5-m3-c000090 | 3 | 21 | 8.49859 | completed/correct | exact_single_candidate |
| d5-m3-c000091 | 3 | 3 | 1.44289 | completed/correct | exact_single_candidate |
| d5-m3-c000092 | 3 | 5 | 1.79291 | completed/correct | exact_single_candidate |
| d5-m3-c000093 | 3 | 4 | 1.58358 | completed/correct | exact_single_candidate |
| d5-m3-c000094 | 3 | 16 | 5.17782 | completed/correct | exact_single_candidate |
| d5-m3-c000095 | 3 | 7 | 2.57912 | completed/correct | exact_single_candidate |
| d5-m3-c000096 | 2 | 6 | 1.81856 | completed/correct | exact_single_candidate |
| d5-m3-c000097 | 3 | 20 | 7.01005 | completed/correct | exact_single_candidate |
| d5-m3-c000098 | 2 | 2 | 0.941114 | completed/correct | exact_single_candidate |
| d5-m3-c000099 | 3 | 5 | 1.6674 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `0f2fdb0e103c04ace62bd1cb9b2942d5ca23ca0929588e5e3b8176cbe02f4567`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
