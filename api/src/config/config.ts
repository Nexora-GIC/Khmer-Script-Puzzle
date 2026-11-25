// All configuration comes from env (see .env.example). .env is loaded here so both
// the Nest app and the TypeORM CLI see it.
import 'dotenv/config';

function required(name: string): string {
  const v = process.env[name];
  if (!v) throw new Error(`${name} is required`);
  return v;
}

export const config = {
  port: Number(process.env.PORT ?? 3100),
  databaseUrl: required('DATABASE_URL'),
  engineUrl: process.env.ENGINE_URL ?? 'http://localhost:8080',
  engineKey: required('ENGINE_KEY'),
  engineTimeoutMs: 2000,
  production: process.env.NODE_ENV === 'production',
};
