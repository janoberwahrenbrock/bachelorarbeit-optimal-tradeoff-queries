# d5-a5-n100-h2-grid3-grid-adaptive-stop-single-candidate-minprog0p001-src72072

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

100 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 100 tatsächliche Versuche.
adaptive, H2, Grid 3, Queryquelle grid, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 100/100; regulär ungelöst: 0/100; fehlgeschlagen: 0/100; falsche Auswahl: 0/100; Auswahlqualität unbestätigt: 0/100.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 100 | 8.23 | 823 |
| Queries, korrekte Lösungen | 100 | 8.23 | 823 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 100 | 8.23 | 823 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 100 | 2.41122 | 241.122 |
| API-Sekunden, korrekte Lösungen | 100 | 2.41122 | 241.122 |
| Controller-Sekunden, sämtliche Versuche | 100 | 3.0847 | 308.47 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d5-m5-c000025, d5-m5-c000036, d5-m5-c000046, d5-m5-c000058, d5-m5-c000061, d5-m5-c000070, d5-m5-c000071, d5-m5-c000098

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d5-m5-c000000 | 2 | 6 | 1.37603 | completed/correct | exact_single_candidate |
| d5-m5-c000001 | 5 | 11 | 3.55608 | completed/correct | exact_single_candidate |
| d5-m5-c000002 | 5 | 4 | 1.38563 | completed/correct | exact_single_candidate |
| d5-m5-c000003 | 3 | 3 | 1.05996 | completed/correct | exact_single_candidate |
| d5-m5-c000004 | 5 | 9 | 4.17732 | completed/correct | exact_single_candidate |
| d5-m5-c000005 | 5 | 14 | 4.21025 | completed/correct | exact_single_candidate |
| d5-m5-c000006 | 3 | 6 | 1.63461 | completed/correct | exact_single_candidate |
| d5-m5-c000007 | 5 | 2 | 1.18454 | completed/correct | exact_single_candidate |
| d5-m5-c000008 | 4 | 11 | 3.56717 | completed/correct | exact_single_candidate |
| d5-m5-c000009 | 5 | 3 | 1.38166 | completed/correct | exact_single_candidate |
| d5-m5-c000010 | 3 | 2 | 0.942279 | completed/correct | exact_single_candidate |
| d5-m5-c000011 | 5 | 6 | 2.29168 | completed/correct | exact_single_candidate |
| d5-m5-c000012 | 4 | 5 | 1.64693 | completed/correct | exact_single_candidate |
| d5-m5-c000013 | 3 | 9 | 1.99937 | completed/correct | exact_single_candidate |
| d5-m5-c000014 | 5 | 19 | 4.77694 | completed/correct | exact_single_candidate |
| d5-m5-c000015 | 5 | 3 | 1.32923 | completed/correct | exact_single_candidate |
| d5-m5-c000016 | 3 | 2 | 1.00467 | completed/correct | exact_single_candidate |
| d5-m5-c000017 | 4 | 3 | 1.18656 | completed/correct | exact_single_candidate |
| d5-m5-c000018 | 4 | 5 | 1.70448 | completed/correct | exact_single_candidate |
| d5-m5-c000019 | 4 | 9 | 3.29659 | completed/correct | exact_single_candidate |
| d5-m5-c000020 | 5 | 11 | 3.57845 | completed/correct | exact_single_candidate |
| d5-m5-c000021 | 5 | 9 | 2.45477 | completed/correct | exact_single_candidate |
| d5-m5-c000022 | 5 | 8 | 2.83968 | completed/correct | exact_single_candidate |
| d5-m5-c000023 | 5 | 4 | 1.7608 | completed/correct | exact_single_candidate |
| d5-m5-c000024 | 5 | 10 | 2.26126 | completed/correct | exact_single_candidate |
| d5-m5-c000025 | 5 | 24 | 6.41747 | completed/correct | exact_single_candidate |
| d5-m5-c000026 | 3 | 5 | 1.4045 | completed/correct | exact_single_candidate |
| d5-m5-c000027 | 4 | 5 | 1.48573 | completed/correct | exact_single_candidate |
| d5-m5-c000028 | 4 | 4 | 1.48989 | completed/correct | exact_single_candidate |
| d5-m5-c000029 | 4 | 8 | 1.78984 | completed/correct | exact_single_candidate |
| d5-m5-c000030 | 4 | 3 | 1.12647 | completed/correct | exact_single_candidate |
| d5-m5-c000031 | 4 | 6 | 1.55748 | completed/correct | exact_single_candidate |
| d5-m5-c000032 | 4 | 2 | 1.00035 | completed/correct | exact_single_candidate |
| d5-m5-c000033 | 3 | 2 | 0.929033 | completed/correct | exact_single_candidate |
| d5-m5-c000034 | 5 | 9 | 2.53859 | completed/correct | exact_single_candidate |
| d5-m5-c000035 | 4 | 6 | 1.53923 | completed/correct | exact_single_candidate |
| d5-m5-c000036 | 5 | 19 | 5.09932 | completed/correct | exact_single_candidate |
| d5-m5-c000037 | 4 | 11 | 2.55059 | completed/correct | exact_single_candidate |
| d5-m5-c000038 | 3 | 8 | 2.58553 | completed/correct | exact_single_candidate |
| d5-m5-c000039 | 5 | 9 | 2.90729 | completed/correct | exact_single_candidate |
| d5-m5-c000040 | 4 | 13 | 3.01041 | completed/correct | exact_single_candidate |
| d5-m5-c000041 | 4 | 3 | 1.17262 | completed/correct | exact_single_candidate |
| d5-m5-c000042 | 5 | 4 | 1.39205 | completed/correct | exact_single_candidate |
| d5-m5-c000043 | 5 | 4 | 1.32202 | completed/correct | exact_single_candidate |
| d5-m5-c000044 | 4 | 5 | 1.62714 | completed/correct | exact_single_candidate |
| d5-m5-c000045 | 4 | 2 | 0.966195 | completed/correct | exact_single_candidate |
| d5-m5-c000046 | 4 | 36 | 10.3055 | completed/correct | exact_single_candidate |
| d5-m5-c000047 | 4 | 6 | 2.07351 | completed/correct | exact_single_candidate |
| d5-m5-c000048 | 5 | 10 | 2.95887 | completed/correct | exact_single_candidate |
| d5-m5-c000049 | 3 | 6 | 1.58144 | completed/correct | exact_single_candidate |
| d5-m5-c000050 | 5 | 6 | 1.91033 | completed/correct | exact_single_candidate |
| d5-m5-c000051 | 5 | 11 | 3.49662 | completed/correct | exact_single_candidate |
| d5-m5-c000052 | 4 | 7 | 2.12577 | completed/correct | exact_single_candidate |
| d5-m5-c000053 | 5 | 7 | 1.9047 | completed/correct | exact_single_candidate |
| d5-m5-c000054 | 5 | 6 | 2.03718 | completed/correct | exact_single_candidate |
| d5-m5-c000055 | 5 | 5 | 1.47111 | completed/correct | exact_single_candidate |
| d5-m5-c000056 | 3 | 5 | 1.22452 | completed/correct | exact_single_candidate |
| d5-m5-c000057 | 4 | 3 | 1.28631 | completed/correct | exact_single_candidate |
| d5-m5-c000058 | 5 | 24 | 7.33547 | completed/correct | exact_single_candidate |
| d5-m5-c000059 | 4 | 4 | 1.34095 | completed/correct | exact_single_candidate |
| d5-m5-c000060 | 5 | 9 | 2.60609 | completed/correct | exact_single_candidate |
| d5-m5-c000061 | 5 | 19 | 4.95509 | completed/correct | exact_single_candidate |
| d5-m5-c000062 | 4 | 5 | 1.52954 | completed/correct | exact_single_candidate |
| d5-m5-c000063 | 4 | 4 | 1.23722 | completed/correct | exact_single_candidate |
| d5-m5-c000064 | 3 | 7 | 1.55742 | completed/correct | exact_single_candidate |
| d5-m5-c000065 | 3 | 6 | 1.68679 | completed/correct | exact_single_candidate |
| d5-m5-c000066 | 5 | 4 | 1.37673 | completed/correct | exact_single_candidate |
| d5-m5-c000067 | 3 | 23 | 4.57674 | completed/correct | exact_single_candidate |
| d5-m5-c000068 | 4 | 4 | 1.50187 | completed/correct | exact_single_candidate |
| d5-m5-c000069 | 3 | 4 | 1.18784 | completed/correct | exact_single_candidate |
| d5-m5-c000070 | 4 | 49 | 12.8522 | completed/correct | exact_single_candidate |
| d5-m5-c000071 | 5 | 18 | 4.99116 | completed/correct | exact_single_candidate |
| d5-m5-c000072 | 5 | 5 | 1.6077 | completed/correct | exact_single_candidate |
| d5-m5-c000073 | 3 | 5 | 1.453 | completed/correct | exact_single_candidate |
| d5-m5-c000074 | 3 | 5 | 1.32592 | completed/correct | exact_single_candidate |
| d5-m5-c000075 | 3 | 8 | 1.85634 | completed/correct | exact_single_candidate |
| d5-m5-c000076 | 3 | 2 | 0.898279 | completed/correct | exact_single_candidate |
| d5-m5-c000077 | 4 | 5 | 1.62206 | completed/correct | exact_single_candidate |
| d5-m5-c000078 | 3 | 17 | 4.78538 | completed/correct | exact_single_candidate |
| d5-m5-c000079 | 3 | 4 | 1.17911 | completed/correct | exact_single_candidate |
| d5-m5-c000080 | 4 | 8 | 1.90812 | completed/correct | exact_single_candidate |
| d5-m5-c000081 | 4 | 6 | 1.68845 | completed/correct | exact_single_candidate |
| d5-m5-c000082 | 4 | 6 | 2.04197 | completed/correct | exact_single_candidate |
| d5-m5-c000083 | 5 | 5 | 1.61652 | completed/correct | exact_single_candidate |
| d5-m5-c000084 | 4 | 14 | 3.46189 | completed/correct | exact_single_candidate |
| d5-m5-c000085 | 4 | 2 | 1.00408 | completed/correct | exact_single_candidate |
| d5-m5-c000086 | 3 | 2 | 0.956832 | completed/correct | exact_single_candidate |
| d5-m5-c000087 | 3 | 1 | 0.847735 | completed/correct | exact_single_candidate |
| d5-m5-c000088 | 3 | 8 | 2.1711 | completed/correct | exact_single_candidate |
| d5-m5-c000089 | 5 | 3 | 1.30725 | completed/correct | exact_single_candidate |
| d5-m5-c000090 | 5 | 22 | 4.70398 | completed/correct | exact_single_candidate |
| d5-m5-c000091 | 5 | 12 | 2.75171 | completed/correct | exact_single_candidate |
| d5-m5-c000092 | 5 | 12 | 3.39226 | completed/correct | exact_single_candidate |
| d5-m5-c000093 | 3 | 3 | 1.14111 | completed/correct | exact_single_candidate |
| d5-m5-c000094 | 4 | 5 | 1.46069 | completed/correct | exact_single_candidate |
| d5-m5-c000095 | 5 | 6 | 2.49792 | completed/correct | exact_single_candidate |
| d5-m5-c000096 | 3 | 3 | 1.12497 | completed/correct | exact_single_candidate |
| d5-m5-c000097 | 4 | 4 | 1.59563 | completed/correct | exact_single_candidate |
| d5-m5-c000098 | 4 | 25 | 6.38325 | completed/correct | exact_single_candidate |
| d5-m5-c000099 | 4 | 11 | 2.70929 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `133061ab663f37931e551d101335a3f2ca668e458ad3b41e8d5cb1d72022c519`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
