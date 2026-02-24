export default {
	data : [],
	
	getData() {
		return [...this.data]
	},
	
	saveNewData(inp_col_name_widget, sel_col_type_widget, inp_col_default_widget, inp_col_forKey_widget, switch_xtraProp_widget) {
    var xtra = switch_xtraProp_widget;
    let col = {};

    if (inp_col_name_widget) col["name"] = inp_col_name_widget;
    if (sel_col_type_widget) col["type"] = sel_col_type_widget;
    if (inp_col_default_widget !== undefined && inp_col_default_widget !== "") col["default"] = inp_col_default_widget;
    if (xtra && xtra.includes("nullable")) col["nullable"] = true;
    if (xtra && xtra.includes("primary_key")) col["primary_key"] = true;
    if (xtra && xtra.includes("unique")) col["unique"] = true;
    if (inp_col_forKey_widget) col["foreign_key"] = inp_col_forKey_widget;

    this.data.push(col);
    this.getData();
	},
	
	setToDefault() {
		this.data = []
		resetWidget("tbl_new_col")
		resetWidget("Form1", true)
	},
	
	discardRow() {
		this.data.splice(tbl_new_col.triggeredRowIndex, 1)
	},
}