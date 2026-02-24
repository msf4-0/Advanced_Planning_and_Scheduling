export default {
	allERPTables: [],
	selectedTables: [],
	saveData () {
		storeValue('tableNames_ERP', sel_erp_table_names.selectedOptionValues, true)
		showAlert("Table names have been stored for future import in local browser storage.", "info")
	},
	loadData() {
		if (this.selectedTables.length == 0) {
			this.selectedTables = appsmith.store.tableNames_ERP
		}
	},
	async getDataAPI () {
		await get_full_erp_schema.run()
		this.allERPTables = get_full_erp_schema.data
	}
}