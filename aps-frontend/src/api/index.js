// api/index.js - Main entry point that exports all API services
import { scheduleApi } from './services/schedule.js';
import { jobsApi } from './services/jobs.js';
import { resourcesApi } from './services/resources.js';
import { workordersApi } from './services/workorder.js';
import { itemsApi } from './services/items.js';
import { materialsApi } from './services/materials.js';

export const api = {
  schedule: scheduleApi,
  jobs: jobsApi,
  resources: resourcesApi,
  workorder: workordersApi,
  items: itemsApi,
  materials: materialsApi,
};