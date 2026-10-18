# d7-a5-n10-h2-grid5-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072-group08

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
receding, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 16.4 | 164 |
| Queries, korrekte Lösungen | 10 | 16.4 | 164 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 16.4 | 164 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 37.2983 | 372.983 |
| API-Sekunden, korrekte Lösungen | 10 | 37.2983 | 372.983 |
| Controller-Sekunden, sämtliche Versuche | 10 | 37.9886 | 379.886 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: keine

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d7-m5-c000070 | 5 | 17 | 28.3427 | completed/correct | exact_single_candidate |
| d7-m5-c000071 | 5 | 18 | 31.0831 | completed/correct | exact_single_candidate |
| d7-m5-c000072 | 4 | 13 | 22.4246 | completed/correct | exact_single_candidate |
| d7-m5-c000073 | 5 | 29 | 58.7344 | completed/correct | exact_single_candidate |
| d7-m5-c000074 | 4 | 31 | 98.8805 | completed/correct | exact_single_candidate |
| d7-m5-c000075 | 5 | 12 | 20.6324 | completed/correct | exact_single_candidate |
| d7-m5-c000076 | 5 | 11 | 10.8964 | completed/correct | exact_single_candidate |
| d7-m5-c000077 | 4 | 21 | 90.2593 | completed/correct | exact_single_candidate |
| d7-m5-c000078 | 5 | 7 | 6.37932 | completed/correct | exact_single_candidate |
| d7-m5-c000079 | 5 | 5 | 5.34984 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `2fcdbf1443cec7b711d0cf6c49c70aa5de8a40e095f77c7b71560afa7094e6ee`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
