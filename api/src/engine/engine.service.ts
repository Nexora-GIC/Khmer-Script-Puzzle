import { Injectable, Logger } from '@nestjs/common';
import { config } from '../config/config';
// After `npm run gen:engine`, type the methods below with:
// import type { components } from './generated/engine';

/**
 * The only caller of the Go engine. The rest of the api calls engine.judge(...) etc.
 * The engine is a pure function (state in → state out), so a retry never double-counts.
 */
@Injectable()
export class EngineService {
  private readonly log = new Logger(EngineService.name);

  health(): Promise<{ status: string; engineVersion: string }> {
    return this.call('GET', '/healthz');
  }

  // judge(), scoreTrace(), recommend() go here once engine.yaml schemas are filled in.

  private async call<T>(method: string, path: string, body?: unknown, retries = 1): Promise<T> {
    try {
      const res = await fetch(config.engineUrl + path, {
        method,
        headers: {
          Authorization: `Bearer ${config.engineKey}`,
          'Content-Type': 'application/json',
        },
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: AbortSignal.timeout(config.engineTimeoutMs),
      });
      if (!res.ok) throw new Error(`engine ${method} ${path} → ${res.status}`);
      return (await res.json()) as T;
    } catch (err) {
      if (retries > 0) return this.call(method, path, body, retries - 1);
      this.log.error(String(err));
      throw err;
    }
  }
}
