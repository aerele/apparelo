// Copyright (c) 2019, Aerele Technologies Private Limited and contributors
// For license information, please see license.txt
frappe.ui.form.on(cur_frm.doctype,{
onload: function(frm) {
    frm.set_query("item", function() {
        return {
            "filters":{
                "item_group":["in",["Products","Intermediate Product"]],
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
    frm.set_query("item", "additional_parts", function() {
        return {
            filters: {
                "item_group":"Raw Material",
            }
        };
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
}
});
