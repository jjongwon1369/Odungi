# Refrigerator

The Refrigerator device type models a cold storage appliance.

## Required Clusters

A Refrigerator endpoint SHALL implement the following clusters.

| Cluster | ID |
| --- | --- |
| Temperature Control | 0x0056 |
| Refrigerator Alarm | 0x0057 |

### Temperature Control

The TemperatureSetpoint attribute holds the target temperature.
Writing to MinTemperature outside the supported range returns an error.

```cpp
chip::app::Clusters::TemperatureControl::Attributes::TemperatureSetpoint::Set(endpoint, value);
```

## Notes

See also the LaundryWasherMode cluster for a comparable pattern.
