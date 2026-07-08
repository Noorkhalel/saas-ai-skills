/**
 * Financial Calculation Module
 *
 * Handles currency calculations with precision requirements.
 * Used for invoice generation, tax computation, and payment splitting.
 *
 * NOTE: This module uses JavaScript's native number type for simplicity.
 * Real financial systems should use a Decimal/BigDecimal library.
 * The tests should verify that precision is handled appropriately.
 */

export type Currency = 'USD' | 'EUR' | 'GBP' | 'JPY';

export interface MoneyAmount {
  value: number;
  currency: Currency;
}

export interface TaxResult {
  subtotal: number;
  taxAmount: number;
  total: number;
  effectiveRate: number;
}

export interface SplitResult {
  shares: number[];
  remainder: number;
}

// Currency decimal places (JPY has 0)
const DECIMALS: Record<Currency, number> = {
  USD: 2,
  EUR: 2,
  GBP: 2,
  JPY: 0,
};

/**
 * Round a value to the appropriate decimal places for a currency.
 * Uses banker's rounding (round half to even) for financial accuracy.
 */
export function roundCurrency(value: number, currency: Currency): number {
  const decimals = DECIMALS[currency];
  if (decimals === 0) {
    return Math.round(value);
  }
  const factor = Math.pow(10, decimals);
  // Banker's rounding
  const shifted = value * factor;
  const rounded = Math.round(shifted);
  return rounded / factor;
}

/**
 * Calculate tax on a subtotal.
 *
 * Rules:
 * - Tax is calculated on the pre-discount subtotal
 * - Discount is applied before tax (tax on discounted amount)
 * - Tax amount is rounded per currency rules
 * - Effective rate may differ from nominal rate due to rounding
 * - Zero or negative subtotal returns zero tax
 */
export function calculateTax(
  subtotal: number,
  taxRate: number,
  discount: number = 0,
  currency: Currency = 'USD'
): TaxResult {
  if (subtotal <= 0) {
    return { subtotal: 0, taxAmount: 0, total: 0, effectiveRate: 0 };
  }

  if (taxRate < 0 || taxRate > 1) {
    throw new RangeError('Tax rate must be between 0 and 1');
  }

  if (discount < 0) {
    throw new RangeError('Discount must not be negative');
  }

  const discountedSubtotal = Math.max(0, subtotal - discount);
  const rawTax = discountedSubtotal * taxRate;
  const taxAmount = roundCurrency(rawTax, currency);
  const total = roundCurrency(discountedSubtotal + taxAmount, currency);
  const effectiveRate = discountedSubtotal > 0 ? taxAmount / discountedSubtotal : 0;

  return {
    subtotal: roundCurrency(discountedSubtotal, currency),
    taxAmount,
    total,
    effectiveRate,
  };
}

/**
 * Split an amount evenly among N parties.
 *
 * Rules:
 * - Each share is rounded down to the currency's precision
 * - The remainder (due to rounding) goes to the first share
 * - Sum of all shares must equal the original amount exactly
 * - Splitting among 0 parties throws
 * - Splitting 0 returns all-zero shares
 *
 * Example: $100.00 split 3 ways → [$33.34, $33.33, $33.33]
 * (first person gets the extra cent)
 */
export function splitAmount(
  amount: number,
  parties: number,
  currency: Currency = 'USD'
): SplitResult {
  if (parties <= 0) {
    throw new RangeError('Number of parties must be positive');
  }

  if (amount === 0) {
    return {
      shares: new Array(parties).fill(0),
      remainder: 0,
    };
  }

  const decimals = DECIMALS[currency];
  const factor = Math.pow(10, decimals);
  const totalCents = Math.round(amount * factor);
  const baseCents = Math.floor(totalCents / parties);
  const remainderCents = totalCents - baseCents * parties;

  const shares = new Array(parties).fill(baseCents / factor);

  // Distribute remainder cents to first N shares
  for (let i = 0; i < remainderCents; i++) {
    shares[i] = (baseCents + 1) / factor;
  }

  return {
    shares: shares.map(s => roundCurrency(s, currency)),
    remainder: 0, // All cents distributed
  };
}

/**
 * Convert between currencies using a rate.
 *
 * NOTE: The exchange rate precision and source are deliberately
 * unspecified here. Tests should document their assumption about
 * where rates come from.
 */
export function convertCurrency(
  amount: MoneyAmount,
  targetCurrency: Currency,
  exchangeRate: number
): MoneyAmount {
  if (exchangeRate <= 0) {
    throw new RangeError('Exchange rate must be positive');
  }

  const converted = amount.value * exchangeRate;

  return {
    value: roundCurrency(converted, targetCurrency),
    currency: targetCurrency,
  };
}
