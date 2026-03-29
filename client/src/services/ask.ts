import type { AskResponse } from "@/types/api";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://127.0.0.1:8000";

const DEFAULT_TIMEOUT_MS = 130000;

export class ApiError extends Error {
  status?: number;
  isTimeout: boolean;
  isNetwork: boolean;

  constructor(message: string, options?: { status?: number; isTimeout?: boolean; isNetwork?: boolean }) {
    super(message);
    this.name = "ApiError";
    this.status = options?.status;
    this.isTimeout = options?.isTimeout ?? false;
    this.isNetwork = options?.isNetwork ?? false;
  }
}

function withTimeoutSignal(timeoutMs: number): { signal: AbortSignal; cleanup: () => void } {
  const controller = new AbortController();
  const timer = globalThis.setTimeout(() => controller.abort(), timeoutMs);
  return {
    signal: controller.signal,
    cleanup: () => globalThis.clearTimeout(timer),
  };
}

export async function askQuestion(query: string): Promise<AskResponse> {
  const url = `${API_BASE_URL}/v1/ask?q=${encodeURIComponent(query)}`;
  const { signal, cleanup } = withTimeoutSignal(DEFAULT_TIMEOUT_MS);

  let response: Response;

  try {
    response = await fetch(url, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
      signal,
    });
  } catch (error) {
    cleanup();

    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError("Request timed out", { isTimeout: true });
    }

    throw new ApiError("Network request failed", { isNetwork: true });
  }

  cleanup();

  if (!response.ok) {
    throw new ApiError(`Request failed with status ${response.status}`, { status: response.status });
  }

  return response.json() as Promise<AskResponse>;
}

export async function checkBackendHealth(timeoutMs = 5000): Promise<boolean> {
  const url = `${API_BASE_URL}/v1/health`;
  const { signal, cleanup } = withTimeoutSignal(timeoutMs);

  try {
    const response = await fetch(url, {
      method: "GET",
      cache: "no-store",
      signal,
    });
    cleanup();
    return response.ok;
  } catch {
    cleanup();
    return false;
  }
}

export function isBackendConnectionError(error: unknown): boolean {
  if (error instanceof ApiError) {
    return error.isTimeout || error.isNetwork;
  }
  return false;
}
