// api/config.js - Centralized configuration for API endpoints
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || '/api/v1',
  SCHEDULER_ENDPOINT: '/run_scheduler'
};