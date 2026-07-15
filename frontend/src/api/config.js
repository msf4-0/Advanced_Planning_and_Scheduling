// api/config.js - Centralized configuration for API endpoints
export const API_CONFIG = {
  // Base URL for primary REST endpoints (operations, dependencies, resources, workorders)
  BASE_URL: `${window.location.origin}/api/v1`,
  
  // Specialized scheduler endpoints
  RECENT_SCHEDULE: `${window.location.origin}/recent-schedule`,    // GET - returns optimized schedule
  SCHEDULER_RUNNER: `${window.location.origin}/run_scheduler`      // POST - triggers optimization
};