export default {
	tableData: get_table_content.data,
	tableSchema: get_table_cols.data,
	createJsonForm() {
    const fields = {}
		console.log(this.tableSchema)
    this.tableSchema.forEach(item => {

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
				return {}  // Could enhance to handle integer[], text[], etc.

			// Default fallback
			default:
				return ""
		}
	},

	async getAPIData () {
		await get_table_content.run()
		await get_table_cols.run()
		return this.createJsonForm()
	}
}