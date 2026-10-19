# D5 / A5 / H2 — stop_aware-volume-confidence-095 / b04

20 ursprüngliche gepaarte Fälle, 20 einzige Primärversuche: 19 korrekt, 1 falsche Konfidenzentscheidungen, 0 Solverfehler; 123 Antworten. Alle20 bleiben im Nenner.

Volumen-Konfidenzschwelle 0.95, planning_evaluation stop_aware; Grid5/both, adaptive bisTiefe2, receding, minimum expected progress0.001. Modell-Konfidenz ist keine Garantie eines korrekten Gewinners. Auch ein als solved gespeicherter Konfidenzabbruch kann falsch sein. Keine Umwertung als NumericalError, kein Retry.

Diese20 Fälle sind genau eine von fünf disjunkten Partitionen derselben unveränderten100 Matrizen/Gewichte. Alle vier Bedingungen verwenden dieselben ursprünglichen Fall-IDs; der historische Baseline100-Lauf wurde nicht wiederholt. Die20 Batches bilden400 neue Messungen; das Vergleichsdokument ergänzt100 historische Referenzen, keine500 neuen Messungen.

| Fall | Qualität | Antworten | K | Modell-Konfidenz | API s | Fall s | Controller s |
|---|---|---:|---:|---:|---:|---:|---:|
| d5-m5-c000060 | correct | 8 | 2 | 0.9813159425180057 | 14.054528542998014 | 14.42023816400615 | 14.667966873006662 |
| d5-m5-c000061 | correct | 1 | 5 | 0.9558585489974679 | 2.2251541020086734 | 2.52557183400495 | 2.732475674987654 |
| d5-m5-c000062 | correct | 1 | 4 | 0.9502156745785719 | 1.6252824080002028 | 1.9245720689941663 | 2.0999013309919974 |
| d5-m5-c000063 | correct | 3 | 2 | 0.965674698247156 | 2.961447766996571 | 3.2776787930051796 | 3.4680240710004 |
| d5-m5-c000064 | correct | 6 | 2 | 0.9880712483095337 | 3.6103123880020576 | 3.9527311440033372 | 4.183085743992706 |
| d5-m5-c000065 | correct | 7 | 2 | 0.9521630786182986 | 3.7423357390071033 | 4.090344461001223 | 4.320004780005547 |
| d5-m5-c000066 | correct | 4 | 2 | 0.9823510011632887 | 5.809859774002689 | 6.140892653987976 | 6.390567254013149 |
| d5-m5-c000067 | correct | 14 | 2 | 0.9572494251148544 | 9.442108547998942 | 9.852173302002484 | 10.165437407005811 |
| d5-m5-c000068 | correct | 4 | 2 | 0.9784926720233985 | 5.911598452003091 | 6.240535517004901 | 6.450329870000132 |
| d5-m5-c000069 | correct | 2 | 2 | 0.9569840540534948 | 1.4876635179971345 | 1.7992544519947842 | 1.962922748993151 |
| d5-m5-c000070 | incorrect | 22 | 2 | 0.9694005561140332 | 25.539648014004342 | 26.046998974998132 | 26.478984036002657 |
| d5-m5-c000071 | correct | 5 | 2 | 0.9773312257284416 | 7.307843845002935 | 7.653839409991633 | 7.870619937995798 |
| d5-m5-c000072 | correct | 2 | 5 | 0.9635201461880603 | 6.042501210002229 | 6.360230028003571 | 6.536874529992929 |
| d5-m5-c000073 | correct | 8 | 1 | 1.0 | 5.405313994997414 | 5.806731367003522 | 6.054950217003352 |
| d5-m5-c000074 | correct | 0 | 3 | 0.9600146783697263 | 0.024816608987748623 | 0.33017046200984623 | 0.46495608300028834 |
| d5-m5-c000075 | correct | 7 | 2 | 0.9665138011938258 | 4.43892997399962 | 4.802173464995576 | 5.039501673003542 |
| d5-m5-c000076 | correct | 0 | 3 | 0.9985713128532077 | 0.024309657004778273 | 0.32910744499531575 | 0.4670882649952546 |
| d5-m5-c000077 | correct | 11 | 1 | 1.0 | 11.450532661998295 | 11.846090637991438 | 12.14052221699967 |
| d5-m5-c000078 | correct | 14 | 2 | 0.9560811735957307 | 25.251287424005568 | 25.681653772000573 | 26.03432660200633 |
| d5-m5-c000079 | correct | 4 | 2 | 0.986570930963632 | 2.6020125840004766 | 2.940459531004308 | 3.1315473889990244 |

API-, Fall- und Controllerzeiten sind getrennte gespeicherte Messgrößen; unbekannte Werte bleiben unbekannt. Sie werden weder addiert noch als CPU-Zeit, Kalenderdauer oder ETA bezeichnet.

Originalresultate, Journale, Eingaben und Source/Wheel bleiben unverändert. Die öffentliche Plan-/State-/Manifest-/SCI-Ansicht enthält nur ausdrücklich ausgewählte wissenschaftliche Felder mit Originalhashes; private Betriebs-, Prozess-, Claim-, Auth-, Guard-, Release- und Spiegelakten bleiben private Prüfgates. Die gespeicherte Offlineprüfung kontrolliert Hashes, Bindungen und reproduziert Tabellen; sie berechnet keine Gewinner, Fraction-Antworten, Geometrie oder neue wissenschaftliche Abnahme. Messsource62d1…/720726…/Wheel24e4…; Publikationscommit separat.
