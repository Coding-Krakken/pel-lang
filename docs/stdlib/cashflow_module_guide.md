# Cashflow Module Guide

## Overview

The `cashflow` module provides functions for modeling cash flow timing, working capital management, and financial runway calculations. It enables accurate cash-based financial modeling by accounting for payment terms, aging, and burn rates.

## Key Concepts

### Cash vs. Accrual Accounting

PEL models typically use **accrual accounting** for revenue and expenses (when earned/incurred), but **cash flow timing** is critical for:

- **Runway calculations**: How long until cash runs out
- **Working capital management**: Ensuring sufficient liquidity
- **Credit risk**: Managing AR aging and bad debt
- **Supplier relations**: Optimizing AP payment timing

### Payment Terms

Payment terms determine the **timing gap** between revenue recognition and cash collection:

- **Net-30**: Customer pays 30 days after invoice
- **Net-60**: 60 days after invoice
- **Due on receipt**: Immediate payment

This gap creates **Accounts Receivable (AR)** and affects cash availability.

## Module Functions

### Accounts Receivable (AR) Functions

#### `ar_with_payment_terms(revenue, payment_terms)`

Calculate accounts receivable based on payment terms.

**Parameters:**
- `revenue: Currency<USD> per Month` - Monthly revenue
- `payment_terms: Duration<Day>` - Payment terms in days

**Returns:** `Currency<USD>` - AR balance

**Example:**
```pel
// Company has $100k monthly revenue with 30-day terms
param monthly_revenue: Currency<USD> per Month = $100_000/1mo
param terms: Duration<Day> = 30d

var ar = ar_with_payment_terms(monthly_revenue, terms)
// Result: $100,000 (one month of revenue outstanding)
```

**Business Logic:**
```
AR = Revenue × (Payment Terms / 30 days)
```

For 30-day terms, AR equals one month of revenue. For 60-day terms, AR equals two months of revenue.

---

## Best Practices

### 1. Match Terms to Business Model

- **Enterprise SaaS**: Net-30 or Net-60 acceptable
- **SMB SaaS**: Net-15 or faster (credit card preferred)
- **Marketplace**: Fast payment cycles critical

### 2. Monitor DSO Trends

```pel
constraint dso_warning {
  severity: "warning"
  condition: dso > 45d
  message: "DSO exceeds 45 days - review collections"
}
```

### 3. Maintain Runway Buffer

```pel
constraint runway_critical {
  severity: "fatal"
  condition: runway < 6mo
  message: "Runway below 6 months - immediate action required"
}
```

---

**Module:** `stdlib/cashflow/cashflow.pel`  
**Version:** 0.1.0  
**Status:** Complete (17 functions)  
**Dependencies:** None
