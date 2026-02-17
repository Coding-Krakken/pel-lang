# PEL-100 Expressiveness Benchmark

The PEL-100 Benchmark Suite measures PEL's expressiveness across 100 canonical business archetypes.

## Objective

Prove that PEL can model diverse business scenarios concisely, correctly, and consistently.

## Metrics

1. **Lines of Code (LOC)** - Fewer lines = more expressive
2. **Compilation Time** - Fast compilation = good developer experience  
3. **Execution Time** - Fast execution = practical for real use
4. **Success Rate** - All models compile and run correctly

## Benchmark Categories

### 1. SaaS Models (20 models)
- Subscription (Basic, Tiered, Usage-based)
- Enterprise SaaS
- Freemium Conversion
- Product-Led Growth (PLG)
- Multi-product SaaS
- SMB vs Enterprise
- Vertical SaaS

### 2. E-Commerce (20 models)
- B2C Direct-to-Consumer
- B2B Wholesale
- Marketplace (2-sided, 3-sided)
- Dropshipping
- Subscription Box
- Grocery/Meal Kit
- Luxury/High-AOV

### 3. Services (20 models)
- Consulting
- Agency (Creative, Digital)
- Productized Services
- Coaching/Training
- SaaS + Services Hybrid
- Professional Services (Legal, Accounting)
- Freelance Platform

### 4. Marketplaces (20 models)
- Ride-sharing
- Home Services
- Gig Economy
- Rental (Equipment, Vehicles, Homes)
- Lead Generation
- Subscription Marketplace
- Commission-based

### 5. Other Business Models (20 models)
- Advertising/Media
- Hardware + Subscription
- Fintech (Lending, Payments)
- Real Estate
- Manufacturing
- Franchise
- Non-profit

## Running the Benchmark

```bash
# Score all models
python3 benchmarks/score_benchmark.py

# View results
cat benchmarks/PEL_100_RESULTS.md
```

## Current Status

**Implemented:** 12/100 models (12%)

- ✅ saas/saas_subscription.pel
- ✅ saas/saas_tiered_pricing.pel
- ✅ saas/saas_freemium_conversion.pel
- ✅ ecommerce/ecommerce_b2c.pel
- ✅ ecommerce/subscription_box.pel
- ✅ ecommerce/marketplace_dropshipping.pel
- ✅ services/services_consulting.pel
- ✅ services/agency_retainers.pel
- ✅ services/freelance_platform.pel
- ✅ marketplace/marketplace_two_sided.pel
- ✅ marketplace/gig_economy.pel
- ✅ other/advertising_media.pel

**Next batch (Q2 2026):** 8–16 more models across all categories

## Success Criteria

- **Pass Rate:** 100% of models compile and run successfully
- **Average LOC:** < 150 lines per model (target: 10× smaller than spreadsheet equivalent)
- **Compile Time:** < 500ms per model
- **Run Time (deterministic):** < 200ms per model

## How to Contribute

See [CONTRIBUTING.md](../CONTRIBUTING.md) for:
- How to propose new archetypes
- Model quality requirements
- Testing and validation
- Peer review process

## Comparison Baseline

For each archetype, we estimate equivalent spreadsheet implementation:
- Typical spreadsheet: 20-50 tabs, 5,000-10,000 cells
- PEL model: 50-200 lines of code
- **Compression ratio:** 10-20×

## Related Benchmarks

- **PEL-SAFE**: Silent error prevention
- **PEL-TRUST**: Auditability and provenance
- **PEL-RISK**: Tail risk accuracy
- **PEL-UX**: Developer experience
