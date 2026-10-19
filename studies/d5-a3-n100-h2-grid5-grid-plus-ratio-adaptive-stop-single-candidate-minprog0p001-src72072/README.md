# d5-a3-n100-h2-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072

100 unabhängige Primärfälle, 100 tatsächliche Versuche. Ergebnis: **100 korrekt gelöst, 0 regulär ungelöst**, keine Solverfehler oder falschen Gewinner. 727 beantwortete Queries (Mittel 7.27, Nenner alle100 einschließlich ungelöster Fälle).

D5 mit3 Alternativen, adaptiver reduction_per_query-Planung bis Tiefe2, receding,16 Worker/CPU0..15. Grid5 und Ratioqueries; letzte Ebene immer Ratio. Min_expected_progress0.001, stopping single_candidate, ein Versuch pro Fall, keine Query-/Fallzeitlimits, native_threads1, forkserver, bounded_v1, per_answer, standard Trace, profile false. Host177:16GB RAM,8 physische Kerne/16 logische CPUs; Hardware- und Softwarebelege liegen im Paket.

Gespeicherte APIzeit gesamt259.400251977s; Fallzeit298.832849624s; Controller-Versuchszeit325.304120296s. Diese unterschiedlichen Messgrößen sind weder Kalenderdauer noch kausale Hardwarevergleiche.

H1 verwendet dieselben100 ursprünglichen D3-Matrizen und Gewichte wie die historischen H2-Referenzen. Die Kohorten A3/A5/A10/A20 verwenden unterschiedliche Matrizen UND Gewichte und sind ungepaart. Die historische A5/H2-Referenz wurde nicht neu berechnet und zählt nicht zu den400 neuen Fällen. Weniger H1-Queries enthalten30 ungelöste Fälle und belegen keine qualitätsgleiche Verbesserung.

Alle Originalfälle, Antworten, Versuche, gespeicherten Kosten, nativen Audit-/Export-/Releasebelege und Originalberichte sind unverändert enthalten. Provisorische historische Statusfelder bleiben erhalten; getrennte endgültige SCI-Nachweise sind unter provenance verknüpft. Das originale A3-Raw bleibt provisional_failed: zwei Exportprüffelder waren fälschlich auf5 statt3 Alternativen festgelegt; daraus entstand ein tatsächlicher Exportbefund. Die gesonderte einmalige Export-Reconciliation und finale SCI-Annahme sind enthalten; kein vollständiger A3-Raw-Retry.

Keine neue Algorithmusausführung oder geometrische Neuzertifizierung. Die gespeicherte Messquelle ist Commit62d1d01339f91802e2916b63660a4e640d99c9cc/Source720726…/Wheel24e4a5…; Publikationscommit separat.

Downloads: [GitHub Release](https://github.com/janoberwahrenbrock/bachelorarbeit-optimal-tradeoff-queries/releases/tag/study%2Fd5-a3-n100-h2-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072%2Fv1). Rohdaten befinden sich im zusätzlichen d5-a3-n100-h2-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072-v1.zip, nicht allein in GitHubs Quellcodearchiven. Prüfhinweise: reproduction/README.md.
