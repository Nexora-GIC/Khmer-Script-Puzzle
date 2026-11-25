import 'reflect-metadata';
import { writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { NestFactory } from '@nestjs/core';
import { FastifyAdapter, NestFastifyApplication } from '@nestjs/platform-fastify';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { AppModule } from './app.module';
import { config } from './config/config';

async function bootstrap() {
  const app = await NestFactory.create<NestFastifyApplication>(AppModule, new FastifyAdapter());

  // words.json, audio, pictures (uses @fastify/static under the hood)
  app.useStaticAssets({ root: join(__dirname, '..', 'content'), prefix: '/content/' });

  const doc = SwaggerModule.createDocument(
    app,
    new DocumentBuilder().setTitle('api').setVersion('0.0.0').build(),
  );
  SwaggerModule.setup('docs', app, doc);
  // The web repo generates its typed client from this file (npm run gen:api there).
  if (!config.production) writeFileSync('openapi.json', JSON.stringify(doc, null, 2));

  await app.listen(config.port, '0.0.0.0');
}
bootstrap();
