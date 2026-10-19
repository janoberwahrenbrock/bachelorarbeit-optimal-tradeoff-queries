# D5 / A5 / H2 — stop_aware-volume-confidence-099 / b05

20 ursprüngliche gepaarte Fälle, 20 einzige Primärversuche: 20 korrekt, 0 falsche Konfidenzentscheidungen, 0 Solverfehler; 132 Antworten. Alle20 bleiben im Nenner.

Volumen-Konfidenzschwelle 0.99, planning_evaluation stop_aware; Grid5/both, adaptive bisTiefe2, receding, minimum expected progress0.001. Modell-Konfidenz ist keine Garantie eines korrekten Gewinners. Auch ein als solved gespeicherter Konfidenzabbruch kann falsch sein. Keine Umwertung als NumericalError, kein Retry.

Diese20 Fälle sind genau eine von fünf disjunkten Partitionen derselben unveränderten100 Matrizen/Gewichte. Alle vier Bedingungen verwenden dieselben ursprünglichen Fall-IDs; der historische Baseline100-Lauf wurde nicht wiederholt. Die20 Batches bilden400 neue Messungen; das Vergleichsdokument ergänzt100 historische Referenzen, keine500 neuen Messungen.

| Fall | Qualität | Antworten | K | Modell-Konfidenz | API s | Fall s | Controller s |
|---|---|---:|---:|---:|---:|---:|---:|
| d5-m5-c000080 | correct | 2 | 4 | 0.9945531000771168 | 4.052980737003963 | 4.366529279999668 | 4.560747912997613 |
| d5-m5-c000081 | correct | 3 | 3 | 0.9922064990839665 | 3.65627076398232 | 3.9739594559941906 | 4.17169789300533 |
| d5-m5-c000082 | correct | 5 | 2 | 0.9956770095107041 | 6.598959483002545 | 6.937737054016907 | 7.158545844024047 |
| d5-m5-c000083 | correct | 5 | 1 | 1.0 | 7.251799702993594 | 7.590444501984166 | 7.81885902598151 |
| d5-m5-c000084 | correct | 9 | 2 | 0.9918317137512995 | 12.523474468005588 | 12.90226801999961 | 13.17413301000488 |
| d5-m5-c000085 | correct | 2 | 2 | 0.9911630087859467 | 3.3050238900177646 | 3.619243208988337 | 3.7942306420009118 |
| d5-m5-c000086 | correct | 2 | 1 | 1.0 | 2.22906705798232 | 2.5461427160189487 | 2.7374732780153863 |
| d5-m5-c000087 | correct | 1 | 2 | 0.9992572115167594 | 1.6758760439988691 | 2.0004249380144756 | 2.165265048010042 |
| d5-m5-c000088 | correct | 4 | 2 | 0.9957590047025718 | 3.6311760300013702 | 3.9802578469971195 | 4.209495734015945 |
| d5-m5-c000089 | correct | 3 | 3 | 0.9993305646853228 | 5.9729125809972174 | 6.303087804000825 | 6.491376427991781 |
| d5-m5-c000090 | correct | 19 | 2 | 0.9909065636879723 | 20.879221636016155 | 21.34278626801097 | 21.745767010987038 |
| d5-m5-c000091 | correct | 11 | 1 | 1.0 | 11.075521822000155 | 11.474366974987788 | 11.785322891984833 |
| d5-m5-c000092 | correct | 12 | 1 | 1.0 | 21.4466232220002 | 21.855779726000037 | 22.17245657197782 |
| d5-m5-c000093 | correct | 1 | 2 | 0.9923757252560814 | 1.4876120580011047 | 1.8024035180278588 | 2.007606739003677 |
| d5-m5-c000094 | correct | 5 | 2 | 0.9938566816881416 | 5.214070078014629 | 5.590414584003156 | 5.817217175004771 |
| d5-m5-c000095 | correct | 4 | 3 | 0.9960130553651894 | 17.685919534997083 | 18.039217632991495 | 18.25229841901455 |
| d5-m5-c000096 | correct | 3 | 1 | 1.0 | 2.24826949799899 | 2.595978211989859 | 2.7966757390240673 |
| d5-m5-c000097 | correct | 9 | 2 | 0.9978444477372891 | 20.721143627015408 | 21.109904167999048 | 21.38796856699628 |
| d5-m5-c000098 | correct | 24 | 2 | 0.9915522526845336 | 32.85477956398972 | 33.362067290989216 | 33.82709365998744 |
| d5-m5-c000099 | correct | 8 | 2 | 0.990568268962425 | 7.4081941100012045 | 7.825640280003427 | 8.08038449898595 |

API-, Fall- und Controllerzeiten sind getrennte gespeicherte Messgrößen; unbekannte Werte bleiben unbekannt. Sie werden weder addiert noch als CPU-Zeit, Kalenderdauer oder ETA bezeichnet.

Originalresultate, Journale, Eingaben und Source/Wheel bleiben unverändert. Die öffentliche Plan-/State-/Manifest-/SCI-Ansicht enthält nur ausdrücklich ausgewählte wissenschaftliche Felder mit Originalhashes; private Betriebs-, Prozess-, Claim-, Auth-, Guard-, Release- und Spiegelakten bleiben private Prüfgates. Die gespeicherte Offlineprüfung kontrolliert Hashes, Bindungen und reproduziert Tabellen; sie berechnet keine Gewinner, Fraction-Antworten, Geometrie oder neue wissenschaftliche Abnahme. Messsource62d1…/720726…/Wheel24e4…; Publikationscommit separat.
