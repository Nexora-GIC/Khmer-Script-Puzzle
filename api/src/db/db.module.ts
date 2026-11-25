import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { dataSourceOptions } from './data-source';

// The only way into Postgres. The api is the only service that touches the database.
// Feature modules use TypeOrmModule.forFeature([Entity]) to get repositories.
@Module({ imports: [TypeOrmModule.forRoot(dataSourceOptions)] })
export class DbModule {}
