// Copyright (c) 2019, Aerele Technologies Private Limited and contributors
// For license information, please see license.txt
frappe.ui.form.on(cur_frm.doctype,{
onload: function(frm) {
    frm.set_query("part", function() {
        return {
            filters: {
                "is_combined":0
            }
        };
    });
    frm.set_query("item", function() {
        return {
            "filters":{
                "item_group":["in",["Products","Intermediate Product"]],
                "has_variants": 1
            },
        };
    });
    frm.set_query("color_additional_items", function() {
        return {
            filters: {
                "item_group":"Raw Material",
                "has_variants":1
            }
        };
    });
    frm.set_query("size_additional_items", function() {
        return {
            filters: {
                "item_group":"Raw Material",
                "has_variants":1
            }
        };
    });
    frm.set_query("item", "additional_parts", function(doc, cdt, cdn) {
        var fields = frappe.get_doc(cdt, cdn);
		if(fields.based_on==="None") {
            return {
                filters: {
                    "item_group":"Raw Material",
                    "has_variants":0
                }
            };
        }
        else{
            return {
                filters: {
                    "item_group":"Raw Material",
                    "has_variants":1
                }
            };
        }
    });
    frm.set_query("item", "additional_parts_size", function() {
        return {
            filters: {
                "item_group":"Raw Material",
                "has_variants":1
            }
        };
    });
    frm.set_query("item", "additional_parts_colour", function() {
        return {
            filters: {
                "item_group":"Raw Material",
                "has_variants":1
            }
        };
    });
    if(cur_frm && cur_frm.doctype!=='Cutting'){
    frm.set_query("part", "colour_mappings", function() {
        return {
            filters: {
                "is_combined":0
            }
        };
    });
    frm.set_query("part", "parts_per_piece", function() {
        return {
            filters: {
                "is_combined":0
            }
        };
    });
    frm.set_query("parts", function() {
        return {
            filters: {
                "is_combined":0
            }
        };
    });
    }
}
});
