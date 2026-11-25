import { Controller, Get } from '@nestjs/common';
import { EngineService } from '../engine/engine.service';

@Controller()
export class HealthController {
  constructor(private readonly engine: EngineService) {}

  @Get('health')
  async health() {
    const engine = await this.engine.health().then(
      (h) => ({ status: 'ok', engineVersion: h.engineVersion }),
      () => ({ status: 'down' }),
    );
    return { status: 'ok', engine };
  }

  @Get('version')
  version() {
    return { appVersion: process.env.npm_package_version ?? '0.0.0' };
  }
}
