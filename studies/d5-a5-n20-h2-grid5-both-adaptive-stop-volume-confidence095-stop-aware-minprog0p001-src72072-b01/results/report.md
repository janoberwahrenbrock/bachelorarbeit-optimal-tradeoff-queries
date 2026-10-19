# D5 / A5 / H2 — stop_aware-volume-confidence-095 / b01

20 ursprüngliche gepaarte Fälle, 20 einzige Primärversuche: 20 korrekt, 0 falsche Konfidenzentscheidungen, 0 Solverfehler; 74 Antworten. Alle20 bleiben im Nenner.

Volumen-Konfidenzschwelle 0.95, planning_evaluation stop_aware; Grid5/both, adaptive bisTiefe2, receding, minimum expected progress0.001. Modell-Konfidenz ist keine Garantie eines korrekten Gewinners. Auch ein als solved gespeicherter Konfidenzabbruch kann falsch sein. Keine Umwertung als NumericalError, kein Retry.

Diese20 Fälle sind genau eine von fünf disjunkten Partitionen derselben unveränderten100 Matrizen/Gewichte. Alle vier Bedingungen verwenden dieselben ursprünglichen Fall-IDs; der historische Baseline100-Lauf wurde nicht wiederholt. Die20 Batches bilden400 neue Messungen; das Vergleichsdokument ergänzt100 historische Referenzen, keine500 neuen Messungen.

| Fall | Qualität | Antworten | K | Modell-Konfidenz | API s | Fall s | Controller s |
|---|---|---:|---:|---:|---:|---:|---:|
| d5-m5-c000000 | correct | 1 | 2 | 0.9779583566792236 | 0.7749822030018549 | 1.0788311829965096 | 1.3039018769923132 |
| d5-m5-c000001 | correct | 2 | 4 | 0.9752974480110874 | 6.369144812982995 | 6.677963693975471 | 6.885687524016248 |
| d5-m5-c000002 | correct | 5 | 1 | 1.0 | 5.357159386010608 | 5.690034970990382 | 5.905747431999771 |
| d5-m5-c000003 | correct | 4 | 1 | 1.0 | 2.6823125570081174 | 3.008148941997206 | 3.2059453800029587 |
| d5-m5-c000004 | correct | 7 | 2 | 0.9768357303929374 | 17.66784707698389 | 18.021049692004453 | 18.255000178993214 |
| d5-m5-c000005 | correct | 14 | 2 | 0.9715379538289041 | 26.970950416987762 | 27.387017446977552 | 27.73613755599945 |
| d5-m5-c000006 | correct | 2 | 3 | 0.9623246688508552 | 1.5987670680042356 | 1.907666913990397 | 2.083047496009385 |
| d5-m5-c000007 | correct | 1 | 4 | 0.9519970739649928 | 3.007865285006119 | 3.3699469929852057 | 3.524705552001251 |
| d5-m5-c000008 | correct | 1 | 4 | 0.9767451091894506 | 2.1549763359944336 | 2.4606452839798294 | 2.63385833799839 |
| d5-m5-c000009 | correct | 1 | 5 | 0.9546939324290883 | 4.006424579012673 | 4.347365753987106 | 4.521086427994305 |
| d5-m5-c000010 | correct | 1 | 2 | 0.9923992910740772 | 1.4799348690139595 | 1.790494952001609 | 1.9698315289861057 |
| d5-m5-c000011 | correct | 6 | 3 | 0.9558197682421911 | 27.06881936697755 | 27.414949822996277 | 27.641912242979743 |
| d5-m5-c000012 | correct | 2 | 3 | 0.9535873182998232 | 3.0011370000138413 | 3.3709730450063944 | 3.5524176429898944 |
| d5-m5-c000013 | correct | 6 | 2 | 0.956834493915077 | 4.638214066013461 | 4.987852619000478 | 5.227589431015076 |
| d5-m5-c000014 | correct | 7 | 2 | 0.9701307476049026 | 17.534093109017704 | 17.938689076021546 | 18.19392504901043 |
| d5-m5-c000015 | correct | 2 | 4 | 0.9507643202617869 | 4.956131825980265 | 5.274387433979427 | 5.459645559982164 |
| d5-m5-c000016 | correct | 0 | 3 | 0.9819823362390045 | 0.024395276996074244 | 0.32825261299149133 | 0.46855757100274786 |
| d5-m5-c000017 | correct | 2 | 3 | 0.9528531975709366 | 3.901353748020483 | 4.228781773999799 | 4.408353261009324 |
| d5-m5-c000018 | correct | 5 | 3 | 0.9603921009776315 | 6.862540580012137 | 7.199055928009329 | 7.410263960016891 |
| d5-m5-c000019 | correct | 5 | 2 | 0.9651924345124442 | 7.736357268993743 | 8.08656968001742 | 8.317930633987999 |

API-, Fall- und Controllerzeiten sind getrennte gespeicherte Messgrößen; unbekannte Werte bleiben unbekannt. Sie werden weder addiert noch als CPU-Zeit, Kalenderdauer oder ETA bezeichnet.

Originalresultate, Journale, Eingaben und Source/Wheel bleiben unverändert. Die öffentliche Plan-/State-/Manifest-/SCI-Ansicht enthält nur ausdrücklich ausgewählte wissenschaftliche Felder mit Originalhashes; private Betriebs-, Prozess-, Claim-, Auth-, Guard-, Release- und Spiegelakten bleiben private Prüfgates. Die gespeicherte Offlineprüfung kontrolliert Hashes, Bindungen und reproduziert Tabellen; sie berechnet keine Gewinner, Fraction-Antworten, Geometrie oder neue wissenschaftliche Abnahme. Messsource62d1…/720726…/Wheel24e4…; Publikationscommit separat.
