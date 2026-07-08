/**
 * Order Submission Service
 *
 * Handles order placement with payment processing.
 * Previously had a duplicate-order bug (see BUG_REPORT.md).
 */

export interface OrderRequest {
  customerId: string;
  items: Array<{ productId: string; quantity: number; unitPrice: number }>;
  idempotencyKey: string;
  paymentMethodId: string;
}

export interface OrderResult {
  orderId: string;
  status: 'confirmed' | 'failed';
  total: number;
  chargeId?: string;
  error?: string;
}

interface PaymentGateway {
  charge(amount: number, paymentMethodId: string): Promise<{ chargeId: string }>;
}

interface OrderStore {
  findByIdempotencyKey(key: string): Promise<OrderResult | null>;
  save(order: OrderResult & { idempotencyKey: string; customerId: string }): Promise<void>;
}

export class OrderService {
  constructor(
    private readonly payments: PaymentGateway,
    private readonly store: OrderStore
  ) {}

  /**
   * Submit an order. Uses idempotency key to prevent duplicate orders.
   *
   * The idempotency check prevents the duplicate-order bug:
   * if the same idempotencyKey has been used before, return the
   * original result instead of creating a new order.
   */
  async submitOrder(request: OrderRequest): Promise<OrderResult> {
    // Validate input
    if (!request.items || request.items.length === 0) {
      throw new Error('Order must contain at least one item');
    }

    if (!request.idempotencyKey) {
      throw new Error('Idempotency key is required');
    }

    // Check for duplicate submission
    const existing = await this.store.findByIdempotencyKey(request.idempotencyKey);
    if (existing) {
      return existing;
    }

    // Calculate total
    const total = request.items.reduce(
      (sum, item) => sum + item.quantity * item.unitPrice,
      0
    );

    if (total <= 0) {
      throw new Error('Order total must be positive');
    }

    // Process payment
    try {
      const { chargeId } = await this.payments.charge(total, request.paymentMethodId);

      const result: OrderResult = {
        orderId: generateOrderId(),
        status: 'confirmed',
        total,
        chargeId,
      };

      await this.store.save({
        ...result,
        idempotencyKey: request.idempotencyKey,
        customerId: request.customerId,
      });

      return result;

    } catch (error: any) {
      const failedResult: OrderResult = {
        orderId: generateOrderId(),
        status: 'failed',
        total,
        error: error.message,
      };

      await this.store.save({
        ...failedResult,
        idempotencyKey: request.idempotencyKey,
        customerId: request.customerId,
      });

      return failedResult;
    }
  }
}

let _orderCounter = 0;
function generateOrderId(): string {
  _orderCounter++;
  return `ORD-${Date.now()}-${_orderCounter}`;
}
