import React from 'react';
import { styles } from '../styles';

export function GanttChartView({ schedule, loading, onRefresh }) {
  if (loading) return <p style={styles.message}>Loading execution timeline...</p>;
  if (!schedule || schedule.length === 0) {
    return <p style={styles.message}>No active production plan to map. Run optimization first!</p>;
  }

  // 1. Group tasks by assigned resource
  const resourcesGroup = schedule.reduce((acc, task) => {
    const resId = task.resources || 'Unassigned';
    if (!acc[resId]) acc[resId] = [];
    acc[resId].push(task);
    return acc;
  }, {});

  // 2. Find the max timespan to calculate layout scales
  const globalMaxMinutes = schedule.reduce((max, task) => Math.max(max, task.end_minute || 0), 0);
  const chartWidthMinutes = Math.max(globalMaxMinutes + 30, 180); // Pad workspace area
  const scale = 4; // 4px per production minute

  return (
    <div style={styles.tableCard}>
      <div style={styles.tableHeader}>
        <h2>Operational Gantt Timeline (Resource Allocation)</h2>
        <button onClick={onRefresh} style={styles.refreshButton}>Refresh Schedule</button>
      </div>

      {/* Gantt Container Scroll Wrapper */}
      <div style={{ overflowX: 'auto', padding: '16px 0', width: '100%' }}>
        <div style={{ position: 'relative', width: `${chartWidthMinutes * scale + 150}px`, minHeight: '200px' }}>
          
          {/* Timeline Rule Header */}
          <div style={{ display: 'flex', borderBottom: '2px solid #e5e7eb', paddingBottom: '8px', marginBottom: '8px' }}>
            <div style={{ width: '150px', fontWeight: 'bold', color: '#4b5563' }}>Resource ID</div>
            <div style={{ position: 'relative', flex: 1, height: '20px' }}>
              {Array.from({ length: Math.ceil(chartWidthMinutes / 30) }).map((_, i) => (
                <div key={i} style={{ position: 'absolute', left: `${i * 30 * scale}px`, fontSize: '12px', color: '#9ca3af' }}>
                  | {i * 30} m
                </div>
              ))}
            </div>
          </div>

          {/* Machine Rows */}
          {Object.entries(resourcesGroup).map(([resourceId, tasks]) => (
            <div key={resourceId} style={{ display: 'flex', alignItems: 'center', height: '55px', borderBottom: '1px dashed #f3f4f6' }}>
              
              {/* Row Label */}
              <div style={{ width: '150px', fontWeight: '600', color: '#1f2937', fontSize: '14px' }}>
                📟 {resourceId}
              </div>

              {/* Tracks View Window */}
              <div style={{ position: 'relative', flex: 1, height: '100%' }}>
                {tasks.map((task, index) => {
                  const leftPos = (task.start_minute || 0) * scale;
                  const blockWidth = ((task.end_minute || 0) - (task.start_minute || 0)) * scale;
                
                  return (
                    <div
                      key={index}
                      style={{
                        position: 'absolute',
                        left: `${leftPos}px`,
                        // CHANGED: Subtracting 2px from the width provides a natural visual gap between back-to-back tasks
                        width: `${Math.max(blockWidth - 2, 8)}px`, 
                        top: '8px',
                        height: '36px',
                        backgroundColor: task.status === 'Completed' ? '#10b981' : '#3b82f6', // Richer Tailwind colors
                        color: '#ffffff',
                        fontSize: '11px',
                        fontWeight: 'bold',
                        borderRadius: '4px',
                        padding: '4px 6px',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        
                        // ADDED: High-contrast crisp border outline to separate blocks
                        border: '1.5px solid #ffffff', 
                        
                        // ADDED: Enhanced shadows to give individual depth
                        boxShadow: '0 1px 3px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.2)',
                        cursor: 'pointer',
                        boxSizing: 'border-box', // Ensures border stays inside calculated width
                        zIndex: 2,
                        transition: 'all 0.1s ease'
                      }}
                      // Interactive scale highlight on hover
                      onMouseEnter={(e) => {
                        e.currentTarget.style.transform = 'scaleY(1.08)';
                        e.currentTarget.style.zIndex = '10';
                        e.currentTarget.style.borderColor = '#1e3a8a'; // Dark blue outline emphasis on hover
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.transform = 'scaleY(1)';
                        e.currentTarget.style.zIndex = '2';
                        e.currentTarget.style.borderColor = '#ffffff';
                      }}
                      title={`Job: ${task.job_id}\nOrder: ${task.work_order_id || 'N/A'}\nSpan: ${task.start_minute}m - ${task.end_minute}m`}
                    >
                      <div style={{ textShadow: '1px 1px 1px rgba(0,0,0,0.15)' }}>{task.job_id}</div>
                      <div style={{ fontSize: '9px', opacity: 0.9, fontWeight: 'normal' }}>
                        WO: {task.work_order_id || '-'}
                      </div>
                    </div>
                  );
                })}
              </div>

            </div>
          ))}

        </div>
      </div>
    </div>
  );
}