# D5 / A5 / H2 — stop_aware-volume-confidence-099 / b04

20 ursprüngliche gepaarte Fälle, 20 einzige Primärversuche: 18 korrekt, 2 falsche Konfidenzentscheidungen, 0 Solverfehler; 141 Antworten. Alle20 bleiben im Nenner.

Volumen-Konfidenzschwelle 0.99, planning_evaluation stop_aware; Grid5/both, adaptive bisTiefe2, receding, minimum expected progress0.001. Modell-Konfidenz ist keine Garantie eines korrekten Gewinners. Auch ein als solved gespeicherter Konfidenzabbruch kann falsch sein. Keine Umwertung als NumericalError, kein Retry.

Diese20 Fälle sind genau eine von fünf disjunkten Partitionen derselben unveränderten100 Matrizen/Gewichte. Alle vier Bedingungen verwenden dieselben ursprünglichen Fall-IDs; der historische Baseline100-Lauf wurde nicht wiederholt. Die20 Batches bilden400 neue Messungen; das Vergleichsdokument ergänzt100 historische Referenzen, keine500 neuen Messungen.

| Fall | Qualität | Antworten | K | Modell-Konfidenz | API s | Fall s | Controller s |
|---|---|---:|---:|---:|---:|---:|---:|
| d5-m5-c000060 | correct | 8 | 2 | 0.9945184140344906 | 13.807865214999765 | 14.187333375011804 | 14.455346724978881 |
| d5-m5-c000061 | correct | 7 | 1 | 1.0 | 6.970043886976782 | 7.321609869977692 | 7.614344220986823 |
| d5-m5-c000062 | correct | 4 | 2 | 0.9965314035763174 | 4.287693609017879 | 4.617220015003113 | 4.817583903000923 |
| d5-m5-c000063 | correct | 2 | 2 | 0.9970493239682338 | 2.4483021379855927 | 2.7605144180124626 | 2.9327150490134954 |
| d5-m5-c000064 | correct | 7 | 2 | 0.9988557077794543 | 4.093412656977307 | 4.4667887020041235 | 4.708840824983781 |
| d5-m5-c000065 | correct | 10 | 2 | 0.9934635479287118 | 5.845860988978529 | 6.242878653021762 | 6.526353791996371 |
| d5-m5-c000066 | correct | 4 | 1 | 1.0 | 5.680110774002969 | 6.0270525599771645 | 6.239619364001555 |
| d5-m5-c000067 | incorrect | 3 | 2 | 0.9905695545134299 | 2.032001654995838 | 2.3555076039920095 | 2.5475268799928017 |
| d5-m5-c000068 | correct | 4 | 1 | 1.0 | 6.365395291009918 | 6.707137812976725 | 6.915212549007265 |
| d5-m5-c000069 | correct | 5 | 1 | 1.0 | 3.0558941419876646 | 3.407488500000909 | 3.6294845059746876 |
| d5-m5-c000070 | incorrect | 28 | 2 | 0.9957346287083922 | 38.19500920799328 | 38.725000356993405 | 39.248617827979615 |
| d5-m5-c000071 | correct | 11 | 1 | 1.0 | 19.411323845008155 | 19.813381198007846 | 20.104502580012195 |
| d5-m5-c000072 | correct | 4 | 2 | 0.9943182191489685 | 5.684680685983039 | 6.023745038022753 | 6.231856097991113 |
| d5-m5-c000073 | correct | 5 | 1 | 1.0 | 3.1235467809892725 | 3.4702910449996125 | 3.6852234250109177 |
| d5-m5-c000074 | correct | 1 | 3 | 0.9976688330162076 | 1.0218583029927686 | 1.3443133270193357 | 1.5357073859777302 |
| d5-m5-c000075 | correct | 10 | 1 | 1.0 | 7.192619317997014 | 7.594364769000094 | 7.914406543015502 |
| d5-m5-c000076 | correct | 0 | 3 | 0.9985713128532077 | 0.024740590015426278 | 0.3317113539960701 | 0.49109762799344026 |
| d5-m5-c000077 | correct | 8 | 1 | 1.0 | 9.197592885000631 | 9.577193163015181 | 9.850007771019591 |
| d5-m5-c000078 | correct | 16 | 2 | 0.9928700288149608 | 28.97886153397849 | 29.490498582017608 | 29.860659380996367 |
| d5-m5-c000079 | correct | 4 | 1 | 1.0 | 2.723094246000983 | 3.0776985619741026 | 3.295893974020146 |

API-, Fall- und Controllerzeiten sind getrennte gespeicherte Messgrößen; unbekannte Werte bleiben unbekannt. Sie werden weder addiert noch als CPU-Zeit, Kalenderdauer oder ETA bezeichnet.

Originalresultate, Journale, Eingaben und Source/Wheel bleiben unverändert. Die öffentliche Plan-/State-/Manifest-/SCI-Ansicht enthält nur ausdrücklich ausgewählte wissenschaftliche Felder mit Originalhashes; private Betriebs-, Prozess-, Claim-, Auth-, Guard-, Release- und Spiegelakten bleiben private Prüfgates. Die gespeicherte Offlineprüfung kontrolliert Hashes, Bindungen und reproduziert Tabellen; sie berechnet keine Gewinner, Fraction-Antworten, Geometrie oder neue wissenschaftliche Abnahme. Messsource62d1…/720726…/Wheel24e4…; Publikationscommit separat.
