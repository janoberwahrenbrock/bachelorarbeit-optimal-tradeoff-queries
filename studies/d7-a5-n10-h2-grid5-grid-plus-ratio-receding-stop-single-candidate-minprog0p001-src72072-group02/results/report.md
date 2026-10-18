# d7-a5-n10-h2-grid5-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072-group02

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
receding, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 22.9 | 229 |
| Queries, korrekte Lösungen | 10 | 22.9 | 229 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 22.9 | 229 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 80.8285 | 808.285 |
| API-Sekunden, korrekte Lösungen | 10 | 80.8285 | 808.285 |
| Controller-Sekunden, sämtliche Versuche | 10 | 81.5977 | 815.977 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: keine

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d7-m5-c000010 | 5 | 20 | 35.552 | completed/correct | exact_single_candidate |
| d7-m5-c000011 | 5 | 11 | 13.991 | completed/correct | exact_single_candidate |
| d7-m5-c000012 | 5 | 9 | 9.35492 | completed/correct | exact_single_candidate |
| d7-m5-c000013 | 5 | 19 | 39.5052 | completed/correct | exact_single_candidate |
| d7-m5-c000014 | 5 | 42 | 284.911 | completed/correct | exact_single_candidate |
| d7-m5-c000015 | 5 | 21 | 48.5996 | completed/correct | exact_single_candidate |
| d7-m5-c000016 | 5 | 4 | 4.97994 | completed/correct | exact_single_candidate |
| d7-m5-c000017 | 5 | 47 | 166.276 | completed/correct | exact_single_candidate |
| d7-m5-c000018 | 5 | 11 | 19.7921 | completed/correct | exact_single_candidate |
| d7-m5-c000019 | 5 | 45 | 185.324 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `eaa58a47f473416ff14d8e5751ea22febc36510035dc954fd9b5c44601432acc`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
