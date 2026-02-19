# Capacity Module

Functions for capacity planning, utilization, and resource allocation in operations and manufacturing.

## Key Functions

### Core Capacity Calculations
- `calculate_utilization()` - Used capacity / total capacity
- `capacity_gap()` - Demand - available capacity
- `required_capacity()` - Capacity needed for target throughput
- `effective_capacity()` - Capacity accounting for efficiency losses

### Resource Allocation
- `allocate_capacity()` - Distribute capacity across product lines
- `capacity_constraint()` - Maximum possible output
- `bottleneck_capacity()` - Identify limiting resource
- `parallel_capacity()` - Combined capacity of parallel resources

### Scaling & Expansion
- `scale_capacity()` - Add capacity based on growth
- `capacity_increment()` - Minimum unit of capacity addition
- `capacity_lead_time()` - Time to provision new capacity
- `capacity_cost()` - Cost per unit of capacity

### Utilization Metrics
- `peak_utilization()` - Maximum utilization over period
- `average_utilization()` - Mean utilization over period
- `utilization_variability()` - Standard deviation of utilization
- `overutilization_penalty()` - Cost/quality impact of exceeding capacity

## Use Cases
- Manufacturing capacity planning
- Server/infrastructure capacity
- Service delivery capacity (call centers, support teams)
- Warehouse and logistics capacity
- Healthcare facility capacity

## Production-Ready Enhancements (PR-22)

This module has been enhanced with Microsoft-production-grade quality standards:

### Robustness & Validation
- **Division-by-zero protection**: All 16 functions include guards against division by zero
- **Empty array handling**: Functions return safe defaults when passed empty arrays
- **Negative value validation**: Negative inputs are either clamped or trigger safe default returns
- **Boundary condition handling**: Efficiency values clamped to [0,1], proper handling of edge cases

### Documentation
- **Structured @param tags**: Every parameter documented with constraints and valid ranges
- **@return tags**: Expected output ranges and units clearly specified
- **@errors tags**: Error handling behavior explicitly documented
- **Example usage**: Real-world examples for all core functions

### Performance & Numerical Stability
- **Welford's algorithm**: `utilization_variability()` uses numerically stable single-pass variance calculation
- **O(n) complexity**: All functions have linear or better time complexity
- **High test coverage**: 20 edge case tests + 9 integration tests

### Test Coverage
- **16 unit tests**: All core functionality validated
- **20 edge case tests**: Division-by-zero, zero-element arrays, negative values, boundary conditions
- **9 integration tests**: End-to-end workflows for real-world scenarios
- **6 performance tests**: Compilation time benchmarks for scale scenarios (100+ products)

## Related Modules

- **[Hiring Module](../hiring/README.md)** — workforce planning functions that consume capacity metrics. Use `capacity_gap()` to feed into `required_headcount()` and `hiring_plan()`. See integration tests for end-to-end examples.

## Example
```pel
import std.capacity.*

model DataCenterCapacity {
  param total_servers: Count<Server> = 1000 {
    source: "infrastructure_team",
    method: "observed",
    confidence: 1.0
  }
  
  param server_capacity: Rate per Month = 100000 / 1mo {
    source: "vendor_specs",
    method: "observed",
    confidence: 0.95
  }
  
  param target_utilization: Fraction = 0.80 {
    source: "ops_policy",
    method: "assumption",
    confidence: 1.0
  }
  
  rate max_throughput: Rate per Month
    = total_servers * server_capacity
  
  rate available_capacity: Rate per Month
    = max_throughput * target_utilization
  
  param current_demand: Rate per Month = 90000 / 1mo {
    source: "monitoring",
    method: "observed",
    confidence: 0.98
  }
  
  rate utilization: Fraction
    = std.capacity.calculate_utilization(current_demand, max_throughput)
  
  rate capacity_gap: Rate per Month
    = std.capacity.capacity_gap(current_demand, available_capacity)
  
  rate additional_servers: Fraction
    = std.capacity.required_capacity(
        capacity_gap,
        server_capacity,
        1.0  // efficiency
      )
  
  export utilization, capacity_gap, additional_servers
}
```
