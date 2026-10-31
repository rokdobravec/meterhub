// MeterHub — week 1: console app that reads smart-meter readings.

var path = Path.Combine(AppContext.BaseDirectory, "data", "readings.csv");

if (!File.Exists(path))
{
    Console.WriteLine($"Data file not found: {path}");
    return;
}

Console.WriteLine($"MeterHub — reading {path}");
Console.WriteLine($"Lines (incl. header): {File.ReadLines(path).Count()}");

// TODO week 1:
// 1. Define: public record MeterReading(string MeterId, DateTimeOffset Timestamp, double Kwh);
// 2. Parse each line (skip the header) with CultureInfo.InvariantCulture.
// 3. Print the reading count, total kWh, and the first and last timestamp.
