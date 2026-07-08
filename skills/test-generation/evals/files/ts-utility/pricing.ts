/**
 * Date Range Pricing Utility
 *
 * Calculates pricing for date-range-based bookings with tier-based
 * discounts, weekend surcharges, and seasonal adjustments.
 */

export type PriceTier = 'basic' | 'premium' | 'enterprise';

export interface DateRange {
  start: Date;
  end: Date;
}

export interface PricingResult {
  basePrice: number;
  discount: number;
  surcharges: number;
  total: number;
  nightCount: number;
  breakdown: PriceBreakdownEntry[];
}

export interface PriceBreakdownEntry {
  date: string;
  baseRate: number;
  adjustments: string[];
  dailyTotal: number;
}

const BASE_RATES: Record<PriceTier, number> = {
  basic: 50,
  premium: 100,
  enterprise: 200,
};

const WEEKEND_SURCHARGE_RATE = 0.25;
const LONG_STAY_THRESHOLD = 7;
const LONG_STAY_DISCOUNT_RATE = 0.15;

// Peak season: June through August (months 5-7, zero-indexed)
const PEAK_MONTHS = [5, 6, 7];
const PEAK_SURCHARGE_RATE = 0.30;

/**
 * Calculate the total price for a date range booking.
 *
 * Rules:
 * - Base rate depends on tier
 * - Weekends (Saturday & Sunday) have a 25% surcharge
 * - Peak season (June–August) has a 30% surcharge (stacks with weekend)
 * - Stays of 7+ nights get a 15% discount on the total
 * - The start date is included, end date is excluded (hotel-style)
 *
 * Edge cases:
 * - Same start and end date = 0 nights
 * - End before start = throws RangeError
 * - Fractional days are truncated (time component ignored)
 */
export function calculateBookingPrice(
  range: DateRange,
  tier: PriceTier
): PricingResult {
  const start = stripTime(range.start);
  const end = stripTime(range.end);

  if (end < start) {
    throw new RangeError('End date must not be before start date');
  }

  const nightCount = daysBetween(start, end);
  const baseRate = BASE_RATES[tier];

  if (baseRate === undefined) {
    throw new TypeError(`Unknown price tier: ${tier}`);
  }

  const breakdown: PriceBreakdownEntry[] = [];
  let totalBase = 0;
  let totalSurcharges = 0;

  for (let i = 0; i < nightCount; i++) {
    const current = addDays(start, i);
    const adjustments: string[] = [];
    let dailyRate = baseRate;

    // Weekend surcharge
    const dayOfWeek = current.getDay();
    if (dayOfWeek === 0 || dayOfWeek === 6) {
      const weekendExtra = baseRate * WEEKEND_SURCHARGE_RATE;
      dailyRate += weekendExtra;
      totalSurcharges += weekendExtra;
      adjustments.push(`weekend +${(WEEKEND_SURCHARGE_RATE * 100).toFixed(0)}%`);
    }

    // Peak season surcharge
    if (PEAK_MONTHS.includes(current.getMonth())) {
      const peakExtra = baseRate * PEAK_SURCHARGE_RATE;
      dailyRate += peakExtra;
      totalSurcharges += peakExtra;
      adjustments.push(`peak +${(PEAK_SURCHARGE_RATE * 100).toFixed(0)}%`);
    }

    totalBase += baseRate;

    breakdown.push({
      date: current.toISOString().split('T')[0],
      baseRate,
      adjustments,
      dailyTotal: dailyRate,
    });
  }

  const subtotal = totalBase + totalSurcharges;
  let discount = 0;

  if (nightCount >= LONG_STAY_THRESHOLD) {
    discount = subtotal * LONG_STAY_DISCOUNT_RATE;
  }

  return {
    basePrice: totalBase,
    discount: Math.round(discount * 100) / 100,
    surcharges: Math.round(totalSurcharges * 100) / 100,
    total: Math.round((subtotal - discount) * 100) / 100,
    nightCount,
    breakdown,
  };
}

function stripTime(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

function daysBetween(a: Date, b: Date): number {
  return Math.floor((b.getTime() - a.getTime()) / (1000 * 60 * 60 * 24));
}

function addDays(date: Date, days: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}
