/**
 * Centralized HTTP Client for Varidhi Backend API
 * Connects to the running FastAPI backend (P5 + LangGraph Agents).
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8105';

export interface RequestOptions extends RequestInit {
  timeoutMs?: number;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    message: string,
    public data?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchWithTimeout(url: string, options: RequestOptions = {}): Promise<Response> {
  const { timeoutMs = 15000, ...fetchOptions } = options;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(url, {
      ...fetchOptions,
      signal: controller.signal,
    });
    return res;
  } finally {
    clearTimeout(timeoutId);
  }
}

export const apiClient = {
  getBaseUrl(): string {
    return API_BASE_URL.replace(/\/+$/, '');
  },

  async get<T>(path: string, options?: RequestOptions): Promise<T> {
    const url = `${this.getBaseUrl()}${path.startsWith('/') ? path : `/${path}`}`;
    try {
      const response = await fetchWithTimeout(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          ...(options?.headers || {}),
        },
        ...options,
      });

      if (!response.ok) {
        let errorData: unknown;
        try {
          errorData = await response.json();
        } catch {
          errorData = await response.text();
        }
        throw new ApiError(response.status, response.statusText, `GET ${path} failed with ${response.status}`, errorData);
      }

      return (await response.json()) as T;
    } catch (err: unknown) {
      if (err instanceof ApiError) throw err;
      const message = err instanceof Error ? err.message : String(err);
      throw new ApiError(0, 'NETWORK_ERROR', `Failed to fetch ${url}: ${message}`);
    }
  },

  async post<T>(path: string, body: unknown, options?: RequestOptions): Promise<T> {
    const url = `${this.getBaseUrl()}${path.startsWith('/') ? path : `/${path}`}`;
    try {
      const response = await fetchWithTimeout(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          ...(options?.headers || {}),
        },
        body: JSON.stringify(body),
        ...options,
      });

      if (!response.ok) {
        let errorData: unknown;
        try {
          errorData = await response.json();
        } catch {
          errorData = await response.text();
        }
        throw new ApiError(response.status, response.statusText, `POST ${path} failed with ${response.status}`, errorData);
      }

      return (await response.json()) as T;
    } catch (err: unknown) {
      if (err instanceof ApiError) throw err;
      const message = err instanceof Error ? err.message : String(err);
      throw new ApiError(0, 'NETWORK_ERROR', `Failed to post ${url}: ${message}`);
    }
  },
};
