export default {
    updateTable () {
        let tableName = tbl_names.selectedRow.name;
        if (tableName) {
            const encodedTableName = encodeURIComponent(tableName);
            // Example API call (replace with your actual API logic)
            const url = `/admin/columns/${encodedTableName}`;
            // fetch(url, { ... }) or use your preferred method to call the API
            console.log("API URL:", url);
            // You can add your API call logic here
        } else {
            console.error("No table name selected.");
        }
    }
}