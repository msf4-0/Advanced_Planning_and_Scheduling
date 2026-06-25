// api/utils/mappers.js - Shared data transformation functions
/**
 * Maps a database operation row to a universally compatible frontend object
 * Supports both BacklogView and ScheduleView requirements
 */
export const mapOperationToUniversalTask = (op) => ({
  // Shared properties
  job_id: op.id,
  work_order_id: op.work_order_id,
  status: op.status,
  
  // BacklogView specific requirements
  duration: op.duration_minutes,
  predecessor: op.predecessor,
  allowed_resources: op.assigned_resource_id ? [op.assigned_resource_id] : [],
  
  // ScheduleView specific requirements
  resources: op.assigned_resource_id || 'Any Machine',
  start: op.scheduled_start_time || `${op.optimized_start_minute || 0} mins`,
  end: op.scheduled_end_time || `${op.optimized_end_minute || 0} mins`,
  
  // Keep original numeric offsets for timeline calculations if needed by charts
  start_minute: op.optimized_start_minute,
  end_minute: op.optimized_end_minute
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