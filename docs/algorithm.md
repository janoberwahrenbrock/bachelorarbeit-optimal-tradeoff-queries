# Algorithmus

Der Solver wählt anhand von Tradeoffantworten eine Alternative aus einer unverändert übernommenen Alternativenmatrix. Zeilen sind Alternativen, Spalten Ziele. Werte liegen in `[0,1]`. Anzeigenamen und Simulationsgewichte sind kein Eingang der Planung.

## Gewichtsraum und Fragen

Gewichte liegen im Simplex: nichtnegative Komponenten mit Summe eins. Eine Query `(a,b,value)` fragt nach `w[a] ? value * w[b]`; Antworten sind exakt `<`, `>` oder `=`. Die akzeptierte Historie beschränkt den Gewichtsraum. Gleichheit fügt eine Gleichung hinzu, strikte Antworten verwenden die festgelegten geschlossenen Halbseiten.

Kandidaten stammen aus der festgelegten `ratio_relevant`-Analyse. Die Implementierung ersetzt diese Definition nicht durch eine andere Machbarkeits- oder Dominanzregel. Die letzte Planungsebene erzeugt Ratioqueries; höhere Ebenen verwenden Grid oder Grid plus Ratios. Reihenfolge, Spiegelbereinigung und Antwortfilter sind Bestandteil der Methode.

Antwortwahrscheinlichkeiten werden geometrisch ohne Sampling berechnet. Der reguläre Pfad verwendet Binary64, LP und Polytopegeometrie. Exakte, begrenzte rationale Reparaturen behandeln ausdrücklich unterstützte Fehlerfälle; sie führen keine beliebig genaue Universalrechnung ein.

## Feste Planung

`fixed` verwendet nach jeder tatsächlichen Antwort erneut die festgelegte Tiefe. Ohne Konfidenzplanung wird die erwartete terminale Kandidatenanzahl minimiert. Bei gleichem Wert werden die flacheren Werte nur so weit berechnet, wie der bestehende lexikographische Vergleich sie benötigt. Danach entscheidet die numerische Queryidentität.

Bei aktiver Konfidenzplanung ist der terminale Loss das Ziel. Ein akzeptierter hypothetischer Zustand hat Loss eins. Die tatsächlich erwartete Kandidatenanzahl bleibt separat erhalten. Feste Singletonplanung verwendet ihren festgelegten gewöhnlichen Planungspfad.

## Adaptive Verringerung pro Query

`reduction_per_query` vergleicht Horizonte eins bis `depth`. Für jeden zulässigen Plan gilt:

```text
gain = aktuelle_Kandidatenanzahl - erwarteter_terminaler_Loss
rate = gain / erwartete_Queryanzahl
```

Der Nenner ist die gewichtete erwartete Zahl tatsächlich benötigter Fragen des hypothetischen Plans. Früh endende Pfade zählen entsprechend weniger. Die beste Rate gewinnt; Gleichstände entscheiden erwartete Queryzahl, Horizont und numerische Queryidentität in dieser Reihenfolge.

Bei Horizont drei werden vollständige H2-Kindpläne kombiniert. Die Kinder dürfen bei vorhandener Fortsetzung nicht freiwillig stoppen oder durch eine neue frei wählbare H1-Option ersetzt werden. Loss-/Kostenfrontiers und geordnete globale Kombination erhalten die vollständige zulässige Optionsmenge. Nach einer echten Antwort plant der Solver wieder alle erlaubten Root-Horizonte.

## Tatsächliches Ende und Planungsbewertung

`single_candidate` beendet bei genau einem Kandidaten. `volume_confidence` akzeptiert außerdem einen Kandidaten mit Volumenanteil mindestens `threshold`. Gleiche maximale Anteile entscheidet der ursprüngliche Zeilenindex. Singletonprüfung steht vor Konfidenz- und Budgetprüfung.

`planning_evaluation` bestimmt unabhängig davon, ob die Stopregel bereits hypothetische Zustände absorbiert. Ein Konfidenzstopp kann mehrere tatsächliche Kandidaten zurücklassen; deshalb werden Kandidatenanzahl und bewerteter Loss getrennt ausgegeben.

`no_query` und `max_questions` sind reguläre ungelöste Rückgaben. Numerische Fehler oder inkonsistente Antworten sind Fehler mit Partialkontext. Ein Ziel ist als Matrixform zulässig, besitzt aber im festgelegten Ratioverfahren eine leere Kandidatenanalyse und endet mit dem dokumentierten Fehler statt einer zusätzlichen Spezialmethode.
