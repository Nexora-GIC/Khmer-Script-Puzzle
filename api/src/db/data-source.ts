import { join } from 'node:path';
import { DataSource, DataSourceOptions } from 'typeorm';
import { config } from '../config/config';

// One set of options, used by both the Nest app (DbModule) and the TypeORM CLI (migrations).
// Tables to come: users, classes, children, consent, sessions, attempts, strokes,
// mastery state, versions. Each entity lives next to its feature module as *.entity.ts.
export const dataSourceOptions: DataSourceOptions = {
  type: 'postgres',
  url: config.databaseUrl,
  entities: [join(__dirname, '..', '**', '*.entity.{ts,js}')],
  migrations: [join(__dirname, 'migrations', '*.{ts,js}')],
  synchronize: false, // schema changes only through migrations (trial data must stay intact)
};

export default new DataSource(dataSourceOptions);
