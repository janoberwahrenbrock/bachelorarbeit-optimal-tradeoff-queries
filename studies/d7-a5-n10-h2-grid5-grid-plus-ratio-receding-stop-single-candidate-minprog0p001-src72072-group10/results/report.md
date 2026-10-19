# d7-a5-n10-h2-grid5-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072-group10

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
receding, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 22.1 | 221 |
| Queries, korrekte Lösungen | 10 | 22.1 | 221 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 22.1 | 221 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 63.6355 | 636.355 |
| API-Sekunden, korrekte Lösungen | 10 | 63.6355 | 636.355 |
| Controller-Sekunden, sämtliche Versuche | 10 | 64.4162 | 644.162 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: keine

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d7-m5-c000090 | 5 | 16 | 32.3852 | completed/correct | exact_single_candidate |
| d7-m5-c000091 | 4 | 16 | 26.556 | completed/correct | exact_single_candidate |
| d7-m5-c000092 | 5 | 6 | 7.10731 | completed/correct | exact_single_candidate |
| d7-m5-c000093 | 5 | 39 | 166.055 | completed/correct | exact_single_candidate |
| d7-m5-c000094 | 5 | 6 | 4.85069 | completed/correct | exact_single_candidate |
| d7-m5-c000095 | 4 | 20 | 52.5214 | completed/correct | exact_single_candidate |
| d7-m5-c000096 | 5 | 69 | 202.423 | completed/correct | exact_single_candidate |
| d7-m5-c000097 | 4 | 34 | 127.24 | completed/correct | exact_single_candidate |
| d7-m5-c000098 | 4 | 7 | 5.85883 | completed/correct | exact_single_candidate |
| d7-m5-c000099 | 4 | 8 | 11.3589 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `38f87818fe81a1d91142874b2f28c11903c155470c0adc47d0c143af7b9c5976`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
