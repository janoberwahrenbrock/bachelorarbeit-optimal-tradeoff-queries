# D5 / A5 / H2 — stop_aware-volume-confidence-099 / b02

20 ursprüngliche gepaarte Fälle, 20 einzige Primärversuche: 20 korrekt, 0 falsche Konfidenzentscheidungen, 0 Solverfehler; 139 Antworten. Alle20 bleiben im Nenner.

Volumen-Konfidenzschwelle 0.99, planning_evaluation stop_aware; Grid5/both, adaptive bisTiefe2, receding, minimum expected progress0.001. Modell-Konfidenz ist keine Garantie eines korrekten Gewinners. Auch ein als solved gespeicherter Konfidenzabbruch kann falsch sein. Keine Umwertung als NumericalError, kein Retry.

Diese20 Fälle sind genau eine von fünf disjunkten Partitionen derselben unveränderten100 Matrizen/Gewichte. Alle vier Bedingungen verwenden dieselben ursprünglichen Fall-IDs; der historische Baseline100-Lauf wurde nicht wiederholt. Die20 Batches bilden400 neue Messungen; das Vergleichsdokument ergänzt100 historische Referenzen, keine500 neuen Messungen.

| Fall | Qualität | Antworten | K | Modell-Konfidenz | API s | Fall s | Controller s |
|---|---|---:|---:|---:|---:|---:|---:|
| d5-m5-c000020 | correct | 11 | 2 | 0.9972172004824303 | 25.6814557419857 | 26.072410816996126 | 26.36532090199762 |
| d5-m5-c000021 | correct | 10 | 2 | 0.9937452131230653 | 15.236945306998678 | 15.639277620997746 | 15.938181471981807 |
| d5-m5-c000022 | correct | 11 | 1 | 1.0 | 20.381858012988232 | 20.819967691000784 | 21.131964626983972 |
| d5-m5-c000023 | correct | 5 | 1 | 1.0 | 11.220811395993223 | 11.562681712006452 | 11.779671023017727 |
| d5-m5-c000024 | correct | 1 | 4 | 0.9924836071804282 | 3.238914258981822 | 3.544002400012687 | 3.7024320170166902 |
| d5-m5-c000025 | correct | 22 | 2 | 0.9970788614073705 | 29.474142906983616 | 29.95676547999028 | 30.39603942501708 |
| d5-m5-c000026 | correct | 4 | 1 | 1.0 | 2.692292132007424 | 3.023901073000161 | 3.234361909009749 |
| d5-m5-c000027 | correct | 4 | 3 | 0.9923764338034792 | 5.333522931003245 | 5.669539723021444 | 5.87449025499518 |
| d5-m5-c000028 | correct | 2 | 2 | 0.9939256478631332 | 3.5404706789995544 | 3.85926501697395 | 4.051518077991204 |
| d5-m5-c000029 | correct | 2 | 2 | 0.9946140846014961 | 2.5737252210092265 | 2.8886228560004383 | 3.0744787040166557 |
| d5-m5-c000030 | correct | 2 | 2 | 0.9932176983394333 | 2.7450249069952406 | 3.0970240530150477 | 3.2830019949760754 |
| d5-m5-c000031 | correct | 5 | 1 | 1.0 | 4.760386843991 | 5.119398198003182 | 5.352266229019733 |
| d5-m5-c000032 | correct | 1 | 2 | 0.9909399502228463 | 2.7108696100185625 | 3.0379432839981746 | 3.2012899630062748 |
| d5-m5-c000033 | correct | 2 | 2 | 0.9902095904730874 | 2.5652780850068666 | 2.8882720099936705 | 3.0815403839806095 |
| d5-m5-c000034 | correct | 6 | 2 | 0.9909470131924573 | 9.454366427991772 | 9.828888569987612 | 10.068270849995315 |
| d5-m5-c000035 | correct | 2 | 4 | 0.9902911164231321 | 3.5695106890052557 | 3.9087728429876734 | 4.087749324011384 |
| d5-m5-c000036 | correct | 23 | 2 | 0.9910668490606546 | 39.88753860499128 | 40.40487784802099 | 40.900207694008714 |
| d5-m5-c000037 | correct | 9 | 2 | 0.9946424527752619 | 8.659896619996289 | 9.053677916002925 | 9.33536061301129 |
| d5-m5-c000038 | correct | 7 | 2 | 0.9974773569357245 | 8.824560402979841 | 9.194978716986952 | 9.449289315001806 |
| d5-m5-c000039 | correct | 10 | 2 | 0.9973522141714976 | 16.012672496028244 | 16.410098987980746 | 16.748662753001554 |

API-, Fall- und Controllerzeiten sind getrennte gespeicherte Messgrößen; unbekannte Werte bleiben unbekannt. Sie werden weder addiert noch als CPU-Zeit, Kalenderdauer oder ETA bezeichnet.

Originalresultate, Journale, Eingaben und Source/Wheel bleiben unverändert. Die öffentliche Plan-/State-/Manifest-/SCI-Ansicht enthält nur ausdrücklich ausgewählte wissenschaftliche Felder mit Originalhashes; private Betriebs-, Prozess-, Claim-, Auth-, Guard-, Release- und Spiegelakten bleiben private Prüfgates. Die gespeicherte Offlineprüfung kontrolliert Hashes, Bindungen und reproduziert Tabellen; sie berechnet keine Gewinner, Fraction-Antworten, Geometrie oder neue wissenschaftliche Abnahme. Messsource62d1…/720726…/Wheel24e4…; Publikationscommit separat.
