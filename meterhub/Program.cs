// MeterHub — week 1: console app that reads smart-meter readings.
using System.Globalization;

var path = Path.Combine(AppContext.BaseDirectory, "data", "readings.csv");

if (!File.Exists(path))
{
    Console.WriteLine($"Data file not found: {path}");
    return;
}

Console.WriteLine($"MeterHub — reading {path}");

var readings = new List<MeterReading>();
var skipped = 0;

// Skip the header line (meterId,timestamp,kwh).
foreach (var line in File.ReadLines(path).Skip(1))
{
    var parts = line.Split(',');
    if (parts.Length != 3)
    {
        skipped++;
        continue;
    }

    if (!DateTimeOffset.TryParse(parts[1], CultureInfo.InvariantCulture, DateTimeStyles.AssumeUniversal, out var timestamp)
        || !double.TryParse(parts[2], NumberStyles.Float, CultureInfo.InvariantCulture, out var kwh))
    {
        skipped++;
        continue;
    }

    readings.Add(new MeterReading(parts[0], timestamp, kwh));
}

Console.WriteLine($"Readings: {readings.Count:N0} (skipped {skipped})");

if (readings.Count > 0)
{
    Console.WriteLine($"Total kWh: {readings.Sum(r => r.Kwh):F2}");
    Console.WriteLine($"First timestamp: {readings.Min(r => r.Timestamp):O}");
    Console.WriteLine($"Last timestamp:  {readings.Max(r => r.Timestamp):O}");
}
