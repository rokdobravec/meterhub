# MeterHub

Smart-meter readings service in C#/.NET. Imports 15-minute energy data, calculates daily consumption and peak demand, and detects gaps and duplicates.

This is a learning project that grows step by step: console app → EF Core + SQL Server → ASP.NET Core API → xUnit tests → Angular frontend.

## Run

Requires the [.NET 10 SDK](https://dotnet.microsoft.com/download).

```bash
cd meterhub
dotnet run
```

## Structure

| Path | What |
| --- | --- |
| `meterhub/` | Console app (C#) |
| `data/` | Synthetic sample readings for 5 meters, Jan–Feb 2026 — see [data/README.md](data/README.md) |

## Roadmap

- [ ] Parse CSV readings into records
- [ ] Domain model and interfaces
- [ ] Daily consumption and peak demand with LINQ
- [ ] Async import, gap and duplicate detection
- [ ] Multi-project solution with DI, configuration and logging
- [ ] SQL Server storage with EF Core
- [ ] REST API with ASP.NET Core
- [ ] Unit and integration tests with xUnit
- [ ] Angular frontend
- [ ] Background gap checker

All meter data in `data/` is generated and fictional.
