// api/README.md - API Module Documentation

# API Module Structure

This module provides a well-organized, separation-of-concerns approach to API communication.

## Directory Structure

```
api/
├── index.js              # Main entry point - exports all services
├── config.js             # Centralized configuration (base URLs, endpoints)
├── services/
│   ├── schedule.js       # Schedule and optimization endpoints
│   ├── jobs.js           # Jobs/tasks management endpoints
│   └── machines.js       # Machines/resources endpoints
└── utils/
    ├── mappers.js        # Data transformation functions
    └── errorHandler.js   # Error handling utilities
```

## Usage

### Basic Import (in App.jsx or any component)

```javascript
// Option 1: Import entire api object
import { api } from './api';

// Access services as namespaces
api.schedule.fetchSchedule();
api.jobs.addTask(taskData);
api.machines.fetchMachines();
```

### Grouped Access

```javascript
// Option 2: Import specific service
import { scheduleApi } from './api/services/schedule.js';

// Use directly
scheduleApi.fetchSchedule();
scheduleApi.triggerOptimization();
```

### All Available Methods

#### Schedule Service (`api.schedule`)
- `fetchSchedule()` - Get current optimized schedule (excludes 'Done' status)
- `triggerOptimization()` - Execute the optimization solver engine

#### Jobs Service (`api.jobs`)
- `fetchBacklog()` - Get all operations including completed tasks
- `addTask(task)` - Create new task with optional dependencies
- `deleteTask(operationId)` - Delete task and its dependencies

#### Machines Service (`api.machines`)
- `fetchMachines()` - Fetch all available resources
- `addMachine(machine)` - Create new machine/resource

## Benefits

✅ **Separation of Concerns** - Each service handles one domain
✅ **Scalability** - Easy to add new services without touching existing code
✅ **Maintainability** - Shared utilities reduce code duplication
✅ **Testability** - Individual services can be tested in isolation
✅ **Configuration Management** - Centralized API config in one place
✅ **Error Handling** - Consistent error handling across all services
✅ **Documentation** - JSDoc comments for IDE intellisense

## Configuration

Update `config.js` to change API base URL or endpoints:

```javascript
// api/config.js
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || '/api/v1',
  SCHEDULER_ENDPOINT: '/run_scheduler'
};
```

## Migration Guide (From Old Structure)

### Before
```javascript
import { api } from './api.js';
api.fetchSchedule();
api.addTask(task);
api.fetchMachines();
```

### After
```javascript
import { api } from './api';
api.schedule.fetchSchedule();
api.jobs.addTask(task);
api.machines.fetchMachines();
```

Just update the method calls to use the service namespace!