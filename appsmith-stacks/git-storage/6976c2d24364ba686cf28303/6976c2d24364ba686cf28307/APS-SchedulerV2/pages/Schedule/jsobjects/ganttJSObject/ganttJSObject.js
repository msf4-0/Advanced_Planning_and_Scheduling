export default {
  // User can set these to match their dataset
  groupField: inp_group.text,      // e.g., 'machine', 'group', 'resource'
  labelField: inp_label.text,     // e.g., 'order_id', 'job', 'label'
  startField: inp_start.text,   // e.g., 'start', 'start_time'
  endField: inp_end.text,       // e.g., 'end', 'end_time'
  durationField: inp_duration.text,  // e.g., 'duration'
	scheduleStartDate: datePick_start.selectedDate,
	data: {},
	
	async toggleAutoChart() {
		if (get_state.data.is_running) {
			await get_gantt_schedule.run()
			this.data = get_gantt_schedule.data.result
		} else {
			await get_recent_saved_schedule.run()
		 	this.data = get_recent_saved_schedule.data.result.result
		}
	},
	
	async schedule_run() {
		await get_gantt_schedule.run()
		this.data = get_gantt_schedule.data.result
		this.mapToMermaidGantt(this.data)
	},

  mapToMermaidGantt: function(steps = this.data) {
		
		// Convert object to array if needed
    if (steps && !Array.isArray(steps) && typeof steps === 'object') {
      steps = Object.entries(steps).map(([job, props]) => ({
        ...props,
        label: job
      }));
    }
		
    if (!steps || !Array.isArray(steps) || steps.length === 0) {
      return 'gantt\nNo data available';
    }

    let ganttChart = 'gantt\n  title Schedule\n  dateFormat  YYYY-MM-DD HH:mm\n';
		const axisFormat = 'axisFormat ' + inp_axisFormat.text + '\n';
		ganttChart += axisFormat
		
    // Use the configured field names
    const groupKey = this.groupField;
    const labelKey = this.labelField;
    const startKey = this.startField;
    const endKey = this.endField;
    const durationKey = this.durationField;

    // Group by the specified group field
    const groups = steps.reduce((acc, step) => {
      const group = step[groupKey] || 'Unknown';
      if (!acc[group]) acc[group] = [];
      acc[group].push(step);
      return acc;
    }, {});

    const baseDate = new Date(this.scheduleStartDate || '2024-01-01T00:00:00');

    Object.entries(groups).forEach(([group, tasks]) => {
      ganttChart += `  section ${group}\n`;

      tasks.forEach((step, idx) => {
        const startOffset = step[startKey] || 0;
        let duration = 1;
        if (step[endKey] !== undefined) {
          duration = step[endKey] - startOffset;
        } else if (step[durationKey] !== undefined) {
          duration = step[durationKey];
        }

        const start = new Date(baseDate);
        start.setHours(start.getHours() + startOffset);

        const startStr = start.toISOString().slice(0, 16).replace('T', ' ');
        const label = step[labelKey] || `Task ${idx + 1}`;

        ganttChart += `    ${label} :${group}_${idx}, ${startStr}, ${duration}h\n`;
      });
    });

    return ganttChart;
  },
};