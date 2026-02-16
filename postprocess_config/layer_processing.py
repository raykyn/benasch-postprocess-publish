CONFIG = {
    "span_layer": "Span",  # the name of the relation layer in the XMI file
    "relation_layer": "Relation",  # the name of the relation layer in the XMI file
    "priority_layer": "Element",
    "priorities": {  # higher priority means nested deeper (this makes sure that same-boundary annotations are nested in the right order)
        "attr": 0,
        "head": 2,
        "default": 1
    },
    "span_attributes_to_remove": ["Element", "Category", "Role", "label"],  # cleanup
    "relation_attributes_to_remove": ["label"],  # cleanup
    "span_features": {
        "label": {
            "field": ["Element", "Category"],  # the name of the features as defined in INCEPTION,
            "required": True,  # if this feature is required to be present for the annotation to be processed, if not present, the annotation will be skipped
            "process_instructions": {  # instructions on how to process the annotation based on the value of the feature
                "appo": {
                    "new_features": {
                        "element": "appo",
                    },
                    "add_feature_by_index": {
                        1: "class",
                    },
                    "copy_by_index_to_head": {
                        "class": 1
                    },
                    "add_remaining_fields_by_schema_info": 2,
                    "requires_head": True,
                    "if_no_class_get_class_from_head": True,
                },
                "attr": {
                    "new_features": {
                        "element": "attr",
                    },
                    "add_feature_by_index": {
                        1: "class",
                    },
                    "add_remaining_fields_by_schema_info": 2,
                },
                "head": {
                    "new_features": {  # create a new feature with the given value
                        "element": "head",
                    },
                    "add_feature_by_index": {
                        1: "class",
                    },
                    "get_features_from_parent": True,  # meaning: the head-class is defined by the instruction 'add feature to head' of the parent span
                },
                "interaction": {
                    "new_features": {
                        "element": "interaction",  # NOTE: Should we leave interaction annotations in? 
                    },
                    "copy_features": {
                    },
                    "process_eventelement": ("eventinfo", "eventspan"),
                    "add_feature_by_index": {
                        1: "class",
                    },
                    "add_remaining_fields_by_event_info": 2
                },
                "list": {
                    "new_features": {  # create a new feature with the given value
                        "element": "list",
                    },
                    "add_all_other_fields_as": "class",  # NOTE: we do this for the moment, so no information gets lost
                    "get_class_from_child_references": True,
                },
                "mod": {
                    "new_features": {
                        "element": "mod",
                    },
                    "add_feature_by_index": {
                        1: "class",
                    },
                    "add_all_other_fields_as": "subclass",
                },
                "num": {
                    "new_features": {
                        "element": "num",
                    },
                    "add_feature_by_index": {
                        1: "class",
                    },
                    "add_all_other_fields_as": "subclass",
                },
                "other": {
                    "new_features": {
                        "element": "other",
                    },
                    "add_feature_by_index": {
                        1: "class",
                    },
                    "add_all_other_fields_as": "subclass",
                },
                "pro": {
                    "new_features": {
                        "element": "reference",
                        "class": "pro"  # gets overwritten anyways, but required for an in between step
                    },
                    "add_optional_feature_by_index": {
                        1: "class",
                    },
                    "add_remaining_fields_by_schema_info": 2,
                    "requires_head": True
                },
                "ref": {
                    "new_features": {
                        "element": "reference",
                    },
                    "add_feature_by_index": {
                        1: "class",
                    },
                    "copy_by_index_to_head": {
                        "class": 2
                    },
                    "add_remaining_fields_by_schema_info": 2,
                    "requires_head": True
                },
                "trigger": {
                    "new_features": {
                        "element": "trigger",
                    },
                    "process_eventelement": ("eventinfo", "trigger"),  # TODO: WHAT DOES THIS DO?
                    "add_feature_by_index": {
                        1: "class",
                    },
                    "add_remaining_fields_by_event_info": 2
                },
                "unc": {
                    "new_features": {
                        "element": "unclear",
                    },
                    "add_feature_by_index": {
                        1: "class",
                    },
                    "add_all_other_fields_as": "subclass",
                },
                "unk": {
                    "new_features": {
                        "element": "unknown",
                    },
                    "add_feature_by_index": {
                        1: "class",
                    },
                    "add_all_other_fields_as": "subclass",
                },
                "val": {
                    "new_features": {
                        "element": "value",
                    },
                   "add_feature_by_index": {
                        1: "class",
                    },
                    "add_all_other_fields_as": "subclass",
                },
            }
        },
        "role": {
            "field": "Role", 
            "required": False,
            "process_instructions": {
            }
        },
    },
    "relation_features": {
        "label": {
            "field": "label", 
            "required": True,
            "process_instructions": {
                "role": {
                    "new_features": {
                        "class": "role",
                    },
                    "add_all_other_fields_as": "detail",
                    "add_remaining_fields_by_event_info": 2,
                },
                r".*?": {  # all remaining labels are handled like this, so always put this last
                    "add_feature_by_index": {
                        0: "class",
                    },
                    "add_remaining_fields_by_event_info": 1,
                }
            }
        },
    },
}