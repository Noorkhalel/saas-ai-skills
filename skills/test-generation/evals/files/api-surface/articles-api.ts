/**
 * REST API for article management.
 *
 * Features:
 * - Pagination (offset-based with configurable page size)
 * - Filtering by status, author, tag, and date range
 * - Sorting by title, created date, or view count
 * - Input validation for all query parameters
 * - Rate limiting (100 requests per minute per API key)
 */

import { Router, Request, Response, NextFunction } from 'express';

export interface Article {
  id: string;
  title: string;
  slug: string;
  content: string;
  status: 'draft' | 'published' | 'archived';
  author: { id: string; name: string };
  tags: string[];
  viewCount: number;
  createdAt: Date;
  updatedAt: Date;
}

interface ListQuery {
  page?: number;
  limit?: number;
  sort?: 'title' | 'createdAt' | 'viewCount';
  order?: 'asc' | 'desc';
  status?: string;
  author?: string;
  tag?: string;
  fromDate?: string;
  toDate?: string;
  search?: string;
}

interface PaginatedResult<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

// Rate limiter state (in-memory for simplicity)
const rateLimitMap = new Map<string, { count: number; resetAt: number }>();
const RATE_LIMIT = 100;
const RATE_WINDOW_MS = 60_000;

function rateLimit(req: Request, res: Response, next: NextFunction) {
  const apiKey = req.headers['x-api-key'] as string;
  if (!apiKey) {
    return res.status(401).json({ error: 'API key required' });
  }

  const now = Date.now();
  const entry = rateLimitMap.get(apiKey);

  if (!entry || now > entry.resetAt) {
    rateLimitMap.set(apiKey, { count: 1, resetAt: now + RATE_WINDOW_MS });
    res.set('X-RateLimit-Remaining', String(RATE_LIMIT - 1));
    return next();
  }

  entry.count++;

  if (entry.count > RATE_LIMIT) {
    const retryAfter = Math.ceil((entry.resetAt - now) / 1000);
    res.set('Retry-After', String(retryAfter));
    return res.status(429).json({
      error: 'Rate limit exceeded',
      retryAfter,
    });
  }

  res.set('X-RateLimit-Remaining', String(RATE_LIMIT - entry.count));
  next();
}

// Simulated article store
let articles: Article[] = [];

const VALID_SORT_FIELDS = ['title', 'createdAt', 'viewCount'];
const VALID_ORDERS = ['asc', 'desc'];
const MAX_LIMIT = 100;
const DEFAULT_LIMIT = 20;

export function createArticleRouter(): Router {
  const router = Router();
  router.use(rateLimit);

  // List articles with pagination, filtering, sorting
  router.get('/articles', (req: Request, res: Response) => {
    const query = req.query as Record<string, string>;

    // Validate pagination
    const page = parseInt(query.page || '1', 10);
    const limit = parseInt(query.limit || String(DEFAULT_LIMIT), 10);

    if (isNaN(page) || page < 1) {
      return res.status(400).json({ error: 'Page must be a positive integer' });
    }
    if (isNaN(limit) || limit < 1) {
      return res.status(400).json({ error: 'Limit must be a positive integer' });
    }
    if (limit > MAX_LIMIT) {
      return res.status(400).json({ error: `Limit must not exceed ${MAX_LIMIT}` });
    }

    // Validate sort
    const sort = (query.sort || 'createdAt') as string;
    const order = (query.order || 'desc') as string;

    if (!VALID_SORT_FIELDS.includes(sort)) {
      return res.status(400).json({
        error: `Invalid sort field. Valid fields: ${VALID_SORT_FIELDS.join(', ')}`,
      });
    }
    if (!VALID_ORDERS.includes(order)) {
      return res.status(400).json({ error: 'Order must be "asc" or "desc"' });
    }

    // Validate date range
    if (query.fromDate && isNaN(Date.parse(query.fromDate))) {
      return res.status(400).json({ error: 'Invalid fromDate format' });
    }
    if (query.toDate && isNaN(Date.parse(query.toDate))) {
      return res.status(400).json({ error: 'Invalid toDate format' });
    }

    // Apply filters
    let filtered = [...articles];

    if (query.status) {
      if (!['draft', 'published', 'archived'].includes(query.status)) {
        return res.status(400).json({ error: 'Invalid status filter' });
      }
      filtered = filtered.filter(a => a.status === query.status);
    }

    if (query.author) {
      filtered = filtered.filter(a => a.author.id === query.author);
    }

    if (query.tag) {
      filtered = filtered.filter(a => a.tags.includes(query.tag as string));
    }

    if (query.fromDate) {
      const from = new Date(query.fromDate);
      filtered = filtered.filter(a => a.createdAt >= from);
    }

    if (query.toDate) {
      const to = new Date(query.toDate);
      filtered = filtered.filter(a => a.createdAt <= to);
    }

    if (query.search) {
      const term = query.search.toLowerCase();
      filtered = filtered.filter(
        a => a.title.toLowerCase().includes(term) || a.content.toLowerCase().includes(term)
      );
    }

    // Sort
    filtered.sort((a, b) => {
      let cmp = 0;
      if (sort === 'title') cmp = a.title.localeCompare(b.title);
      else if (sort === 'createdAt') cmp = a.createdAt.getTime() - b.createdAt.getTime();
      else if (sort === 'viewCount') cmp = a.viewCount - b.viewCount;
      return order === 'desc' ? -cmp : cmp;
    });

    // Paginate
    const total = filtered.length;
    const totalPages = Math.ceil(total / limit);
    const offset = (page - 1) * limit;
    const pageData = filtered.slice(offset, offset + limit);

    const result: PaginatedResult<Article> = {
      data: pageData,
      pagination: {
        page,
        limit,
        total,
        totalPages,
        hasNext: page < totalPages,
        hasPrev: page > 1,
      },
    };

    res.json(result);
  });

  // Get single article
  router.get('/articles/:id', (req: Request, res: Response) => {
    const article = articles.find(a => a.id === req.params.id);
    if (!article) {
      return res.status(404).json({ error: 'Article not found' });
    }
    // Increment view count
    article.viewCount++;
    res.json(article);
  });

  return router;
}

// Test helper to set articles
export function setArticles(data: Article[]) {
  articles = data;
}
