CONFIG = {
    # this sets possible values for additional classes. 
    # the first value is always the default value for that class.
    "schema_info": {
        "other_fields": {
            "numerus": ["sgl", "grp", "neg"],
            "specificity": ["spc", "uspc"],
            "tense": ["pres", "past", "fut", "unspec"],
            "polarity": ["pos", "neg"],
            "modality": [
                "ass", 
                "claim", 
                "hypo",
                "requ",
                "prop",
                "desi",
                "prom",
                "other",
                ],
        },
        "event_fields": {
            "tense": ["pres", "past", "fut", "unspec"],
            "polarity": ["pos", "neg"],
            "modality": [
                "ass", 
                "claim", 
                "hypo",
                "requ",
                "prop",
                "desi",
                "prom",
                "other",
                ],
        }
    },
    "head_defaults": {
        "per": "nam",
        "loc": "type",
        "org": "type",
        "gpe": "nam",
        "fac": "type",
        "default": "unk"  # fallback
    }
}

CONFIG["schema_info"]["other_fields_values"] = [
    x
    for xs in CONFIG["schema_info"]["other_fields"].values()
    for x in xs
]