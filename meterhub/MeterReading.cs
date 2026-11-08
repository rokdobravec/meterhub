// One 15-minute reading. Timestamp is the end of the interval.
public record MeterReading(string MeterId, DateTimeOffset Timestamp, double Kwh);
