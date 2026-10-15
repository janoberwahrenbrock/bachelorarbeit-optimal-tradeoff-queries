# Konfigurationsbeispiele

Die drei vollständigen Konfigurationen zeigen feste Tiefe zwei, adaptive Tiefe
zwei und adaptive Tiefe drei mit 99%-Abbruch einschließlich Stopbewertung in der
Planung. Sie verwenden fünf Gridwerte plus Ratios, acht Solverworker und einen
nativen Thread je Prozess. Die letzte Planungsebene verwendet immer Ratios.

Kopiere eine passende Konfiguration nach `inputs/configurations/` und ändere
Kennung und Parameter ausdrücklich. `depth=3` kann viel Rechenzeit benötigen.
Die Beispiele sind keine gemessenen Benchmarkresultate und keine qualifizierten
Ausführungsprofile. Matrix und Oracle werden separat übergeben oder mit
`otqa dataset generate` neu erzeugt.

Alle Parameter erklärt [die Konfigurationsdokumentation](../docs/configuration.md).
Das vollständige Verfahren steht unter [Benchmarks](../docs/benchmarks.md).
