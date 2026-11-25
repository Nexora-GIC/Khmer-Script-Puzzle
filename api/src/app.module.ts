import { Module } from '@nestjs/common';
import { DbModule } from './db/db.module';
import { EngineModule } from './engine/engine.module';
import { HealthModule } from './health/health.module';
import { AuthModule } from './auth/auth.module';
import { ClassesModule } from './classes/classes.module';
import { ChildrenModule } from './children/children.module';
import { PlayModule } from './play/play.module';
import { DashboardModule } from './dashboard/dashboard.module';
import { ReportsModule } from './reports/reports.module';
import { SamplesModule } from './samples/samples.module';
import { ExportModule } from './export/export.module';

@Module({
  imports: [
    DbModule,
    EngineModule,
    HealthModule,
    AuthModule,
    ClassesModule,
    ChildrenModule,
    PlayModule,
    DashboardModule,
    ReportsModule,
    SamplesModule,
    ExportModule,
  ],
})
export class AppModule {}
