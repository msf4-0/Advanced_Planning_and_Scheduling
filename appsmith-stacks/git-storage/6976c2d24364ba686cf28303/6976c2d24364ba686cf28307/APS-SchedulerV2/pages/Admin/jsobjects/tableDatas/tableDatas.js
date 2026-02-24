export default {
	tableData: get_table_content.data,
	tableSchema: get_table_cols.data,
	importFromERP: appsmith.store.tableNames_ERP,
	
	mapData() {
		var selTable = this.importFromERP.map(item => ({
			"item" : item
		}))
		
		return selTable
	},
	
	createJsonForm() {
    const fields = {}

    this.tableSchema.forEach(item => {

      // Skip PRIMARY KEY columns
      if (item.is_primary_key) return

      // Skip SERIAL / auto-increment columns
      if (item.column_default && item.column_default.includes("nextval")) return

      const fieldType = item.data_type
      const field = this.getDefaultValueForPostgresType(fieldType)

      fields[item.column_name] = field
    })

    return fields
  },
	
	getDefaultValueForPostgresType(fieldType) {
		switch (fieldType.toLowerCase()) {
			// Numeric types
			case "integer":
			case "bigint":
			case "smallint":
			case "numeric":
			case "real":
			case "double precision":
				return 0

			// Boolean
			case "boolean":
				return false

			// Date and time
			case "date":
				return null
			case "time without time zone":
				return null
			case "timestamp without time zone":
			case "timestamp with time zone":
				return null

			// UUID
			case "uuid":
				return ""  // Could generate a UUID if needed

			// Text types
			case "character varying":
			case "text":
				return ""

			// JSON type
			case "json":
				return {}

			// Arrays (Postgres shows 'ARRAY')
			case "ARRAY":
				return []  // Could enhance to handle integer[], text[], etc.

			// Default fallback
			default:
				return ""
		}
	},

	async getAPIData () {
		await get_all_tables.run()
		await get_table_content.run()
		await get_table_cols.run()
		this.createJsonForm()
	},
	
	getContent() {
    if (this.tableData.length === 0) {
        const data = {};
        this.tableSchema.forEach(item => {
            data[item.column_name] = this.getDefaultValueForPostgresType(item.data_type);
        });
        // If you want an array with a single object:
        return [data];
    } else {
			return this.tableData
		}
	},
	
	updateDatabase() {
    let conditions = {};
		let data = {};
    this.tableSchema.forEach(item => {
        if (item.is_primary_key) {
            const name = item.column_name;
            // Get the value from the form data for the primary key
            conditions[name] = JSONForm3.formData[name];
        } else {
					const name = item.column_name;
					data[name] = JSONForm3.formData[name]
				}
    });
		
		let apiBody = {
			condition : conditions,
			update_values : data
		}
		
		return apiBody
}
}	