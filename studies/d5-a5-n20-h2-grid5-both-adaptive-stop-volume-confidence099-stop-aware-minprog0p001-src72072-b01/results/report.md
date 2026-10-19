# D5 / A5 / H2 — stop_aware-volume-confidence-099 / b01

20 ursprüngliche gepaarte Fälle, 20 einzige Primärversuche: 20 korrekt, 0 falsche Konfidenzentscheidungen, 0 Solverfehler; 101 Antworten. Alle20 bleiben im Nenner.

Volumen-Konfidenzschwelle 0.99, planning_evaluation stop_aware; Grid5/both, adaptive bisTiefe2, receding, minimum expected progress0.001. Modell-Konfidenz ist keine Garantie eines korrekten Gewinners. Auch ein als solved gespeicherter Konfidenzabbruch kann falsch sein. Keine Umwertung als NumericalError, kein Retry.

Diese20 Fälle sind genau eine von fünf disjunkten Partitionen derselben unveränderten100 Matrizen/Gewichte. Alle vier Bedingungen verwenden dieselben ursprünglichen Fall-IDs; der historische Baseline100-Lauf wurde nicht wiederholt. Die20 Batches bilden400 neue Messungen; das Vergleichsdokument ergänzt100 historische Referenzen, keine500 neuen Messungen.

| Fall | Qualität | Antworten | K | Modell-Konfidenz | API s | Fall s | Controller s |
|---|---|---:|---:|---:|---:|---:|---:|
| d5-m5-c000000 | correct | 7 | 1 | 1.0 | 3.6315767819760367 | 3.9765459219925106 | 4.217606390011497 |
| d5-m5-c000001 | correct | 6 | 2 | 0.9943956165907575 | 11.562343128985958 | 11.91810916599934 | 12.166851401998429 |
| d5-m5-c000002 | correct | 4 | 1 | 1.0 | 5.2478293210151605 | 5.594358945993008 | 5.8001752980053425 |
| d5-m5-c000003 | correct | 3 | 1 | 1.0 | 2.4909271379874554 | 2.8535471519862767 | 3.0619990440027323 |
| d5-m5-c000004 | correct | 8 | 2 | 0.9961557727613718 | 25.28991241400945 | 25.70150867701159 | 25.959122512984322 |
| d5-m5-c000005 | correct | 11 | 3 | 0.9912347985246077 | 25.226020582020283 | 25.63813173599192 | 25.938733123999555 |
| d5-m5-c000006 | correct | 5 | 2 | 0.995269628293244 | 4.0461920899979305 | 4.386984270007815 | 4.600529023009585 |
| d5-m5-c000007 | correct | 1 | 4 | 0.9911366368180495 | 3.4500355949858204 | 3.75465630099643 | 3.9376953370228875 |
| d5-m5-c000008 | correct | 1 | 3 | 0.9995600528042815 | 2.4009525619912893 | 2.7133779499854427 | 2.9299405030033085 |
| d5-m5-c000009 | correct | 1 | 4 | 0.9936538093965965 | 4.413206347991945 | 4.721126709016971 | 4.893318693008041 |
| d5-m5-c000010 | correct | 1 | 2 | 0.9923992910740772 | 1.5895285820006393 | 1.911083609011257 | 2.072798187000444 |
| d5-m5-c000011 | correct | 7 | 2 | 0.9994979823675105 | 17.326902341999812 | 17.697965230006957 | 17.94116103698616 |
| d5-m5-c000012 | correct | 5 | 2 | 0.9909845771778463 | 6.533395503007341 | 6.880227260990068 | 7.101856627006782 |
| d5-m5-c000013 | correct | 6 | 2 | 0.9909702840953715 | 4.288956201984547 | 4.659123579011066 | 4.889797037001699 |
| d5-m5-c000014 | correct | 19 | 2 | 0.9918604825232507 | 28.858070092013804 | 29.323413164005615 | 29.729548121977132 |
| d5-m5-c000015 | correct | 3 | 1 | 1.0 | 5.949719987984281 | 6.285766896995483 | 6.476282507996075 |
| d5-m5-c000016 | correct | 1 | 3 | 0.990011109037622 | 1.3285858970193658 | 1.642771585000446 | 1.8169206109887455 |
| d5-m5-c000017 | correct | 3 | 1 | 1.0 | 3.6197863429842982 | 3.950887012993917 | 4.172875015006866 |
| d5-m5-c000018 | correct | 5 | 1 | 1.0 | 5.065111442003399 | 5.41305661998922 | 5.647939790011151 |
| d5-m5-c000019 | correct | 4 | 2 | 0.999461183612662 | 5.9289843600126915 | 6.287574261019472 | 6.503470409021247 |

API-, Fall- und Controllerzeiten sind getrennte gespeicherte Messgrößen; unbekannte Werte bleiben unbekannt. Sie werden weder addiert noch als CPU-Zeit, Kalenderdauer oder ETA bezeichnet.

Originalresultate, Journale, Eingaben und Source/Wheel bleiben unverändert. Die öffentliche Plan-/State-/Manifest-/SCI-Ansicht enthält nur ausdrücklich ausgewählte wissenschaftliche Felder mit Originalhashes; private Betriebs-, Prozess-, Claim-, Auth-, Guard-, Release- und Spiegelakten bleiben private Prüfgates. Die gespeicherte Offlineprüfung kontrolliert Hashes, Bindungen und reproduziert Tabellen; sie berechnet keine Gewinner, Fraction-Antworten, Geometrie oder neue wissenschaftliche Abnahme. Messsource62d1…/720726…/Wheel24e4…; Publikationscommit separat.
