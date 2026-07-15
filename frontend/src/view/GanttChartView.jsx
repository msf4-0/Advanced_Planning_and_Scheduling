import React, { useState } from 'react';
import { styles } from '../styles';

export function GanttChartView({ schedule, loading, onRefresh }) {
  const [tooltipDelay, setTooltipDelay] = useState(0); // Milliseconds - change this!

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

  // 2. Sort tasks within each resource by start time (for gap detection)
  Object.keys(resourcesGroup).forEach(resId => {
    resourcesGroup[resId].sort((a, b) => (a.start_minute || 0) - (b.start_minute || 0));
  });

  // 3. Find the max timespan to calculate layout scales
  const globalMaxMinutes = schedule.reduce((max, task) => Math.max(max, task.end_minute || 0), 0);
  const chartWidthMinutes = Math.max(globalMaxMinutes + 30, 180);
  const scale = 4; // 4px per production minute

  return (
    <div style={styles.tableCard}>
      <div style={styles.tableHeader}>
        <h2>Operational Gantt Timeline (Resource Allocation)</h2>
        <button onClick={onRefresh} style={styles.refreshButton}>Refresh Schedule</button>
      </div>

      {/* Legend */}
      <div style={{ padding: '12px 16px', backgroundColor: '#f9fafb', borderRadius: '6px', marginBottom: '16px', fontSize: '12px', color: '#6b7280' }}>
        <div><span style={{ display: 'inline-block', width: '12px', height: '12px', backgroundColor: '#3b82f6', borderRadius: '2px', marginRight: '6px' }}></span>Scheduled Task</div>
        <div><span style={{ display: 'inline-block', width: '12px', height: '12px', backgroundColor: '#10b981', borderRadius: '2px', marginRight: '6px' }}></span>Completed Task</div>
        <div style={{ marginTop: '6px', fontStyle: 'italic' }}>Hover over tasks and gaps to see details.</div>
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
            <div key={resourceId}>
              {/* Resource Header Row */}
              <div style={{ display: 'flex', alignItems: 'center', height: '55px', borderBottom: '1px dashed #f3f4f6' }}>
                
                {/* Row Label */}
                <div style={{ width: '150px', fontWeight: '600', color: '#1f2937', fontSize: '14px' }}>
                  📟 {resourceId}
                </div>

                {/* Tracks View Window */}
                <div style={{ position: 'relative', flex: 1, height: '100%' }}>
                  {/* Render tasks */}
                  {tasks.map((task, index) => (
                    <TaskBlock
                      key={index}
                      task={task}
                      index={index}
                      scale={scale}
                      tooltipDelay={tooltipDelay}
                    />
                  ))}

                  {/* Gap indicators - show idle periods */}
                  {tasks.map((task, index) => {
                    if (index === tasks.length - 1) return null; // No gap after last task
                    
                    const currentEnd = task.end_minute || 0;
                    const nextStart = tasks[index + 1].start_minute || 0;
                    const gap = nextStart - currentEnd;

                    if (gap <= 0) return null; // No gap

                    const gapLeftPos = currentEnd * scale;
                    const gapWidth = gap * scale;

                    return (
                      <GapIndicator
                        key={`gap-${index}`}
                        gapLeftPos={gapLeftPos}
                        gapWidth={gapWidth}
                        gap={gap}
                        currentTask={task}
                        nextTask={tasks[index + 1]}
                        tooltipDelay={tooltipDelay}
                      />
                    );
                  })}
                </div>
              </div>
            </div>
          ))}

        </div>
      </div>

      {/* Gap Analysis Summary */}
      <GapAnalysisSummary schedule={schedule} />
    </div>
  );
}

/**
 * Task Block Component - with configurable hover delay
 */
function TaskBlock({ task, index, scale, tooltipDelay }) {
  const [showTooltip, setShowTooltip] = useState(false);
  const tooltipTimeoutRef = React.useRef(null);

  const leftPos = (task.start_minute || 0) * scale;
  const blockWidth = ((task.end_minute || 0) - (task.start_minute || 0)) * scale;

  const handleMouseEnter = (e) => {
    e.currentTarget.style.transform = 'scaleY(1.08)';
    e.currentTarget.style.zIndex = '10';
    e.currentTarget.style.borderColor = '#1e3a8a';

    // Set timeout for tooltip
    tooltipTimeoutRef.current = setTimeout(() => {
      setShowTooltip(true);
    }, tooltipDelay);
  };

  const handleMouseLeave = (e) => {
    e.currentTarget.style.transform = 'scaleY(1)';
    e.currentTarget.style.zIndex = '2';
    e.currentTarget.style.borderColor = '#ffffff';

    // Clear timeout and hide tooltip
    if (tooltipTimeoutRef.current) {
      clearTimeout(tooltipTimeoutRef.current);
    }
    setShowTooltip(false);
  };

  return (
    <div
      style={{
        position: 'absolute',
        left: `${leftPos}px`,
        width: `${Math.max(blockWidth - 2, 8)}px`, 
        top: '8px',
        height: '36px',
        backgroundColor: task.status === 'Completed' ? '#10b981' : '#3b82f6',
        color: '#ffffff',
        fontSize: '11px',
        fontWeight: 'bold',
        borderRadius: '4px',
        padding: '4px 6px',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
        border: '1.5px solid #ffffff', 
        boxShadow: '0 1px 3px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.2)',
        cursor: 'pointer',
        boxSizing: 'border-box',
        zIndex: 2,
        transition: 'all 0.1s ease'
      }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      title={buildTooltip(task)}
    >
      {/* Tooltip */}
      {showTooltip && (
        <div
          style={{
            position: 'fixed',
            backgroundColor: '#1f2937',
            color: '#ffffff',
            padding: '8px 12px',
            borderRadius: '6px',
            fontSize: '12px',
            zIndex: 1000,
            pointerEvents: 'none',
            whiteSpace: 'nowrap',
            boxShadow: '0 4px 6px rgba(0,0,0,0.3)',
            bottom: '100%',
            left: `${leftPos}px`,
            transform: 'translateY(-8px)',
            border: '1px solid #374151'
          }}
        >
          {buildTooltip(task).split('\n').map((line, i) => (
            <div key={i}>{line}</div>
          ))}
        </div>
      )}

      <div style={{ textShadow: '1px 1px 1px rgba(0,0,0,0.15)' }}>{task.job_id}</div>
      <div style={{ fontSize: '9px', opacity: 0.9, fontWeight: 'normal' }}>
        WO: {task.work_order_id || '-'}
      </div>
    </div>
  );
}

/**
 * Gap Indicator Component - with configurable hover delay
 */
function GapIndicator({ gapLeftPos, gapWidth, gap, currentTask, nextTask, tooltipDelay }) {
  const [showTooltip, setShowTooltip] = useState(false);
  const tooltipTimeoutRef = React.useRef(null);

  const handleMouseEnter = () => {
    tooltipTimeoutRef.current = setTimeout(() => {
      setShowTooltip(true);
    }, tooltipDelay);
  };

  const handleMouseLeave = () => {
    if (tooltipTimeoutRef.current) {
      clearTimeout(tooltipTimeoutRef.current);
    }
    setShowTooltip(false);
  };

  const tooltipText = `Gap: ${gap}m between ${currentTask.job_id} and ${nextTask.job_id}${
    nextTask.predecessor ? `\nNext task waiting for: ${nextTask.predecessor}` : ''
  }`;

  return (
    <div
      style={{
        position: 'absolute',
        left: `${gapLeftPos}px`,
        width: `${gapWidth}px`,
        top: '8px',
        height: '36px',
        backgroundColor: 'rgba(239, 68, 68, 0.05)',
        border: '1px dashed rgba(239, 68, 68, 0.3)',
        borderRadius: '2px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '9px',
        color: 'rgba(239, 68, 68, 0.6)',
        fontWeight: '500',
        zIndex: 1,
        cursor: 'help',
        position: 'relative'
      }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      title={tooltipText}
    >
      {/* Tooltip */}
      {showTooltip && (
        <div
          style={{
            position: 'fixed',
            backgroundColor: '#dc2626',
            color: '#ffffff',
            padding: '8px 12px',
            borderRadius: '6px',
            fontSize: '12px',
            zIndex: 1000,
            pointerEvents: 'none',
            whiteSpace: 'nowrap',
            boxShadow: '0 4px 6px rgba(0,0,0,0.3)',
            bottom: '100%',
            left: `${gapLeftPos + gapWidth / 2}px`,
            transform: 'translate(-50%, -8px)',
            border: '1px solid #991b1b'
          }}
        >
          {tooltipText.split('\n').map((line, i) => (
            <div key={i}>{line}</div>
          ))}
        </div>
      )}

      {gap > 20 ? `${gap}m gap` : gap > 10 ? '⏸' : ''}
    </div>
  );
}

/**
 * Build enhanced tooltip with dependency information
 */
function buildTooltip(task) {
  let tooltip = `Job: ${task.job_id}\nOrder: ${task.work_order_id || 'N/A'}\nSpan: ${task.start_minute}m - ${task.end_minute}m\nStatus: ${task.status || 'Scheduled'}`;
  
  if (task.predecessor && task.predecessor !== '-') {
    tooltip += `\n\nWaiting for: ${task.predecessor}`;
  }
  
  if (task.duration) {
    tooltip += `\nDuration: ${Math.round(task.duration / 60)} hours`;
  }
  
  return tooltip;
}

/**
 * Show summary statistics about resource utilization and gaps
 */
function GapAnalysisSummary({ schedule }) {
  if (!schedule || schedule.length === 0) return null;

  // Group by resource
  const byResource = {};
  schedule.forEach(task => {
    const res = task.resources || 'Unassigned';
    if (!byResource[res]) byResource[res] = [];
    byResource[res].push(task);
  });

  // Calculate metrics
  const metrics = {};
  Object.entries(byResource).forEach(([resId, tasks]) => {
    const sorted = [...tasks].sort((a, b) => (a.start_minute || 0) - (b.start_minute || 0));
    
    let totalWorking = 0;
    let totalGaps = 0;
    
    sorted.forEach((task, idx) => {
      const duration = (task.end_minute || 0) - (task.start_minute || 0);
      totalWorking += duration;
      
      if (idx < sorted.length - 1) {
        const nextStart = sorted[idx + 1].start_minute || 0;
        const gap = nextStart - (task.end_minute || 0);
        if (gap > 0) totalGaps += gap;
      }
    });
    
    const totalTime = sorted[sorted.length - 1]?.end_minute || 0;
    const utilization = totalTime > 0 ? ((totalWorking / totalTime) * 100).toFixed(1) : 0;
    
    metrics[resId] = { utilization, totalGaps, totalTime, totalWorking };
  });

  return (
    <div style={{ marginTop: '24px', padding: '12px 16px', backgroundColor: '#f0fdf4', borderRadius: '6px', fontSize: '12px', color: '#15803d' }}>
      <div style={{ fontWeight: '600', marginBottom: '8px' }}>📊 Resource Utilization</div>
      {Object.entries(metrics).map(([resId, metric]) => (
        <div key={resId} style={{ marginBottom: '6px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>{resId}</span>
          <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
            <div style={{ width: '100px', height: '6px', backgroundColor: '#d1fae5', borderRadius: '3px', overflow: 'hidden' }}>
              <div style={{ width: `${metric.utilization}%`, height: '100%', backgroundColor: '#10b981' }} />
            </div>
            <span style={{ minWidth: '50px', textAlign: 'right' }}>{metric.utilization}%</span>
            {metric.totalGaps > 0 && <span style={{ color: '#ea580c', fontWeight: '500' }}>+{metric.totalGaps}m idle</span>}
          </div>
        </div>
      ))}
      <div style={{ marginTop: '8px', fontSize: '11px', opacity: 0.7 }}>
        💡 <strong>Gaps may indicate:</strong> waiting for predecessors, materials, or due date constraints
      </div>
    </div>
  );
}