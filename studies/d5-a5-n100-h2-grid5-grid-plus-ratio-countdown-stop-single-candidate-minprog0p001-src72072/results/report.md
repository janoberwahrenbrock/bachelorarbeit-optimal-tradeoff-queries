# d5-a5-n100-h2-grid5-grid-plus-ratio-countdown-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
countdown, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 8.65 | 865 |
| Queries, korrekte Lösungen | 100 | 8.65 | 865 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 8.65 | 865 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 2.19362 | 219.362 |
| API-Sekunden, korrekte Lösungen | 100 | 2.19362 | 219.362 |
| Controller-Sekunden, sämtliche Versuche | 100 | 2.83522 | 283.522 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000004, d5-m5-c000014, d5-m5-c000025, d5-m5-c000036, d5-m5-c000046, d5-m5-c000058, d5-m5-c000070, d5-m5-c000090

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000000 | 2 | 7 | 1.42196 | completed/correct | exact_single_candidate |
| d5-m5-c000001 | 5 | 8 | 2.34 | completed/correct | exact_single_candidate |
| d5-m5-c000002 | 5 | 4 | 1.40024 | completed/correct | exact_single_candidate |
| d5-m5-c000003 | 3 | 4 | 1.09839 | completed/correct | exact_single_candidate |
| d5-m5-c000004 | 5 | 12 | 4.82791 | completed/correct | exact_single_candidate |
| d5-m5-c000005 | 5 | 12 | 2.57214 | completed/correct | exact_single_candidate |
| d5-m5-c000006 | 3 | 4 | 0.980644 | completed/correct | exact_single_candidate |
| d5-m5-c000007 | 5 | 2 | 1.18252 | completed/correct | exact_single_candidate |
| d5-m5-c000008 | 4 | 12 | 3.03936 | completed/correct | exact_single_candidate |
| d5-m5-c000009 | 5 | 3 | 1.59233 | completed/correct | exact_single_candidate |
| d5-m5-c000010 | 3 | 2 | 0.947676 | completed/correct | exact_single_candidate |
| d5-m5-c000011 | 5 | 8 | 2.53197 | completed/correct | exact_single_candidate |
| d5-m5-c000012 | 4 | 6 | 1.50602 | completed/correct | exact_single_candidate |
| d5-m5-c000013 | 3 | 9 | 1.75768 | completed/correct | exact_single_candidate |
| d5-m5-c000014 | 5 | 26 | 5.22099 | completed/correct | exact_single_candidate |
| d5-m5-c000015 | 5 | 4 | 1.37417 | completed/correct | exact_single_candidate |
| d5-m5-c000016 | 3 | 2 | 0.829674 | completed/correct | exact_single_candidate |
| d5-m5-c000017 | 4 | 4 | 1.16434 | completed/correct | exact_single_candidate |
| d5-m5-c000018 | 4 | 6 | 1.65938 | completed/correct | exact_single_candidate |
| d5-m5-c000019 | 4 | 4 | 1.24586 | completed/correct | exact_single_candidate |
| d5-m5-c000020 | 5 | 14 | 3.61975 | completed/correct | exact_single_candidate |
| d5-m5-c000021 | 5 | 12 | 2.542 | completed/correct | exact_single_candidate |
| d5-m5-c000022 | 5 | 8 | 2.43993 | completed/correct | exact_single_candidate |
| d5-m5-c000023 | 5 | 4 | 1.58882 | completed/correct | exact_single_candidate |
| d5-m5-c000024 | 5 | 12 | 2.51339 | completed/correct | exact_single_candidate |
| d5-m5-c000025 | 5 | 28 | 6.51843 | completed/correct | exact_single_candidate |
| d5-m5-c000026 | 3 | 4 | 0.936642 | completed/correct | exact_single_candidate |
| d5-m5-c000027 | 4 | 4 | 1.15174 | completed/correct | exact_single_candidate |
| d5-m5-c000028 | 4 | 4 | 1.37789 | completed/correct | exact_single_candidate |
| d5-m5-c000029 | 4 | 10 | 1.82242 | completed/correct | exact_single_candidate |
| d5-m5-c000030 | 4 | 2 | 1.01301 | completed/correct | exact_single_candidate |
| d5-m5-c000031 | 4 | 10 | 2.01159 | completed/correct | exact_single_candidate |
| d5-m5-c000032 | 4 | 2 | 1.09506 | completed/correct | exact_single_candidate |
| d5-m5-c000033 | 3 | 2 | 0.865921 | completed/correct | exact_single_candidate |
| d5-m5-c000034 | 5 | 12 | 3.62662 | completed/correct | exact_single_candidate |
| d5-m5-c000035 | 4 | 8 | 1.60145 | completed/correct | exact_single_candidate |
| d5-m5-c000036 | 5 | 24 | 5.30772 | completed/correct | exact_single_candidate |
| d5-m5-c000037 | 4 | 10 | 1.91756 | completed/correct | exact_single_candidate |
| d5-m5-c000038 | 3 | 10 | 2.52606 | completed/correct | exact_single_candidate |
| d5-m5-c000039 | 5 | 8 | 2.66903 | completed/correct | exact_single_candidate |
| d5-m5-c000040 | 4 | 13 | 2.65252 | completed/correct | exact_single_candidate |
| d5-m5-c000041 | 4 | 4 | 1.22699 | completed/correct | exact_single_candidate |
| d5-m5-c000042 | 5 | 4 | 1.31554 | completed/correct | exact_single_candidate |
| d5-m5-c000043 | 5 | 4 | 1.3122 | completed/correct | exact_single_candidate |
| d5-m5-c000044 | 4 | 10 | 2.41822 | completed/correct | exact_single_candidate |
| d5-m5-c000045 | 4 | 2 | 1.08524 | completed/correct | exact_single_candidate |
| d5-m5-c000046 | 4 | 30 | 7.95401 | completed/correct | exact_single_candidate |
| d5-m5-c000047 | 4 | 8 | 2.52551 | completed/correct | exact_single_candidate |
| d5-m5-c000048 | 5 | 10 | 2.69632 | completed/correct | exact_single_candidate |
| d5-m5-c000049 | 3 | 10 | 1.86201 | completed/correct | exact_single_candidate |
| d5-m5-c000050 | 5 | 6 | 1.71056 | completed/correct | exact_single_candidate |
| d5-m5-c000051 | 5 | 6 | 1.9761 | completed/correct | exact_single_candidate |
| d5-m5-c000052 | 4 | 10 | 2.57098 | completed/correct | exact_single_candidate |
| d5-m5-c000053 | 5 | 8 | 2.01691 | completed/correct | exact_single_candidate |
| d5-m5-c000054 | 5 | 6 | 1.65778 | completed/correct | exact_single_candidate |
| d5-m5-c000055 | 5 | 4 | 1.19959 | completed/correct | exact_single_candidate |
| d5-m5-c000056 | 3 | 16 | 2.72526 | completed/correct | exact_single_candidate |
| d5-m5-c000057 | 4 | 3 | 1.09405 | completed/correct | exact_single_candidate |
| d5-m5-c000058 | 5 | 26 | 7.61123 | completed/correct | exact_single_candidate |
| d5-m5-c000059 | 4 | 4 | 1.36668 | completed/correct | exact_single_candidate |
| d5-m5-c000060 | 5 | 10 | 2.36171 | completed/correct | exact_single_candidate |
| d5-m5-c000061 | 5 | 8 | 1.92318 | completed/correct | exact_single_candidate |
| d5-m5-c000062 | 4 | 6 | 1.51012 | completed/correct | exact_single_candidate |
| d5-m5-c000063 | 4 | 4 | 1.2166 | completed/correct | exact_single_candidate |
| d5-m5-c000064 | 3 | 9 | 1.59953 | completed/correct | exact_single_candidate |
| d5-m5-c000065 | 3 | 18 | 3.02769 | completed/correct | exact_single_candidate |
| d5-m5-c000066 | 5 | 8 | 2.0613 | completed/correct | exact_single_candidate |
| d5-m5-c000067 | 3 | 15 | 2.73715 | completed/correct | exact_single_candidate |
| d5-m5-c000068 | 4 | 2 | 1.0253 | completed/correct | exact_single_candidate |
| d5-m5-c000069 | 3 | 2 | 0.797799 | completed/correct | exact_single_candidate |
| d5-m5-c000070 | 4 | 42 | 10.0756 | completed/correct | exact_single_candidate |
| d5-m5-c000071 | 5 | 18 | 4.02631 | completed/correct | exact_single_candidate |
| d5-m5-c000072 | 5 | 4 | 1.43838 | completed/correct | exact_single_candidate |
| d5-m5-c000073 | 3 | 6 | 1.31421 | completed/correct | exact_single_candidate |
| d5-m5-c000074 | 3 | 4 | 0.955943 | completed/correct | exact_single_candidate |
| d5-m5-c000075 | 3 | 10 | 1.6559 | completed/correct | exact_single_candidate |
| d5-m5-c000076 | 3 | 2 | 0.96589 | completed/correct | exact_single_candidate |
| d5-m5-c000077 | 4 | 8 | 1.62941 | completed/correct | exact_single_candidate |
| d5-m5-c000078 | 3 | 18 | 4.41937 | completed/correct | exact_single_candidate |
| d5-m5-c000079 | 3 | 4 | 1.21075 | completed/correct | exact_single_candidate |
| d5-m5-c000080 | 4 | 8 | 1.60737 | completed/correct | exact_single_candidate |
| d5-m5-c000081 | 4 | 4 | 1.11877 | completed/correct | exact_single_candidate |
| d5-m5-c000082 | 4 | 6 | 1.48743 | completed/correct | exact_single_candidate |
| d5-m5-c000083 | 5 | 6 | 1.77748 | completed/correct | exact_single_candidate |
| d5-m5-c000084 | 4 | 10 | 2.37229 | completed/correct | exact_single_candidate |
| d5-m5-c000085 | 4 | 2 | 1.10266 | completed/correct | exact_single_candidate |
| d5-m5-c000086 | 3 | 2 | 0.94314 | completed/correct | exact_single_candidate |
| d5-m5-c000087 | 3 | 2 | 0.908425 | completed/correct | exact_single_candidate |
| d5-m5-c000088 | 3 | 6 | 1.25354 | completed/correct | exact_single_candidate |
| d5-m5-c000089 | 5 | 4 | 1.34048 | completed/correct | exact_single_candidate |
| d5-m5-c000090 | 5 | 22 | 4.58935 | completed/correct | exact_single_candidate |
| d5-m5-c000091 | 5 | 12 | 2.35668 | completed/correct | exact_single_candidate |
| d5-m5-c000092 | 5 | 12 | 2.84893 | completed/correct | exact_single_candidate |
| d5-m5-c000093 | 3 | 2 | 0.839421 | completed/correct | exact_single_candidate |
| d5-m5-c000094 | 4 | 12 | 2.43125 | completed/correct | exact_single_candidate |
| d5-m5-c000095 | 5 | 6 | 2.30285 | completed/correct | exact_single_candidate |
| d5-m5-c000096 | 3 | 2 | 0.792154 | completed/correct | exact_single_candidate |
| d5-m5-c000097 | 4 | 4 | 1.33622 | completed/correct | exact_single_candidate |
| d5-m5-c000098 | 4 | 20 | 4.06383 | completed/correct | exact_single_candidate |
| d5-m5-c000099 | 4 | 14 | 3.12167 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `133061ab663f37931e551d101335a3f2ca668e458ad3b41e8d5cb1d72022c519`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
