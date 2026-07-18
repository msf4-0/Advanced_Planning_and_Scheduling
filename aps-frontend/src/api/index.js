// api/index.js - Main entry point that exports all API services
import { scheduleApi } from './services/schedule.js';
import { jobsApi } from './services/jobs.js';
import { machinesApi } from './services/machines.js';
import { workordersApi } from './services/workorder.js';
import { itemsApi } from './services/items.js';

export const api = {
  schedule: scheduleApi,
  jobs: jobsApi,
  machines: machinesApi,
  workorder: workordersApi,
  items: itemsApi
};