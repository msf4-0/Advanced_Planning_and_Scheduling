// api/utils/mappers.js - Shared data transformation functions
/**
 * Maps a database operation row to a universally compatible frontend object
 * Supports both BacklogView and ScheduleView requirements
 */
export const mapOperationToUniversalTask = (op) => ({
  // Shared properties
  // Use operation_id (e.g., "op_wo1_10") so it displays meaningfully in the UI tables
  job_id: op.operation_id || `job-${op.id}`, 
  work_order_id: op.work_order_id || '-', // Fallback if work order tracking shifts
  status: op.status || 'Scheduled', // Use backend status, fallback to default
  
  // BacklogView specific requirements
  duration: op.duration_minutes || 0,
  predecessor: op.predecessor || '-',
  allowed_resources: op.assigned_resource_id ? [op.assigned_resource_id] : ['Any Machine'],
  
  // ScheduleView specific requirements
  // If your backend introduces machine assignment later, this checks it. Otherwise maps to visual blocks.
  resources: op.assigned_resource_id || op.machine_id || 'Any Machine',
  start: op.scheduled_start_time ? new Date(op.scheduled_start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : `${op.optimized_start_minute || 0} mins`,
  end: op.scheduled_end_time ? new Date(op.scheduled_end_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : `${op.optimized_end_minute || 0} mins`,
  
  // Keep original numeric offsets for timeline calculations in Gantt view
  start_minute: op.optimized_start_minute ?? 0,
  end_minute: op.optimized_end_minute ?? 0
});

/**
 * Builds a dependency map from raw dependencies array
 * Groups dependencies by downstream task identifier
 */
export const buildDependencyMap = (rawDependencies) => {
  const dependencyMap = {};
  rawDependencies.forEach(edge => {
    if (!dependencyMap[edge.downstream_op_id]) {
      dependencyMap[edge.downstream_op_id] = [];
    }
    dependencyMap[edge.downstream_op_id].push(edge.upstream_op_id);
  });
  return dependencyMap;
};