# this contains the rules for all events which are created by references, appositions and attributes where roles are only "source" and "target"
# define here which annotation classes should be automatically assigned to which role name. 
# source is always from a parental span to a child span.
# you may use regex expressions in these
# by default, if a source is mixed with explicit role assignments, if a role of name "source" is already present, the source will be ignored!
# Multiple targets are possible, but only one source is allowed (only one parent span is possible).
CONFIG = {
    "implicit_event_processing": {  
        ("loc", "occ", r".*?"): {  # key can either be a tuple (event, source, target)
            "rename": "workplace",
            "roles": {
                "source": {
                    r".*?": "worker"
                },
                "target": {
                    r".*?": "location"
                }
            }
        },
        ("loc", "title", r".*?"): {  # key can either be a tuple (event, source, target)
            "rename": "holds_landed_title",
            "roles": {
                "source": {
                    r".*?": "holder"
                },
                "target": {
                    r".*?": "title"
                }
            }
        },
        r"comp|includes": {
            "rename": "part_whole",
            "roles": {
                "source": {
                    r".*?": "whole"
                },
                "target": {
                    r".*?": "part"
                }
            }
        },
        "creditor": {
            "rename": "debt",
            "roles": {
                "source": {
                    r".*?": "creditor"
                },
                "target": {
                    r".*?": "debitor"
                }
            }
        },
        "fam": {
            "rename": "family",
            "roles": {
                "source": {
                    r".*?": "family_a"
                },
                "target": {
                    r".*?": "family_b"
                }
            }
        },
        "heir": {
            "rename": "inheritance",
            "roles": {
                "source": {
                    r".*?": "heir"
                },
                "target": {
                    r".*?": "decedent"
                }
            }
        },
        "inherited-from": {
            "rename": "inheritance",
            "roles": {
                "source": {
                    r".*?": "heir"
                },
                "target": {
                    r".*?": "decedent"
                }
            }
        },
        "inheritance": {
            "roles": {
                "source": {
                    "fac": "property"
                },
                "target": {
                }
            }
        },
        "transfer": {
            "roles": {
                "source": {
                    "fac": "property",
                    "per": "issuer"
                },
                "target": {
                    "per": "recipient"
                }
            }
        },
        r"loc|loc_inhabitant|loc_to|topo": {
            "rename": "topological",
            "roles": {
                "source": {
                    "per": "person_a",
                    r".*?": "location_a"
                },
                "target": {
                    "per": "person_b",
                    r".*?": "location_b"
                }
            }
        },
        r"nam|unk|type|other": { "no_event": True },
        "occ": {
            "rename": "employment",
            "roles": {
                "source": {
                    "per": "employee",
                },
                "target": {
                    r".*?": "employer"
                }
            }
        },
        "org_repr": {
            "rename": "representation",
            "roles": {
                "source": {
                    "per": "representative",
                },
                "target": {
                    "org": "represented"
                }
            }
        },
        (r"org-aff.*?", "per", "gpe-org"): {
            "rename": "civic-affiliation",
            "roles": {
                "source": {
                    "per": "resident",
                },
                "target": {
                    "gpe-org": "geopolitical_entity"
                }
            }
        },
        (r"org-aff.*?", "per", "org"): {
            "rename": "membership",
            "roles": {
                "source": {
                    "per": "member",
                },
                "target": {
                    "org": "organization"
                }
            }
        },
        "has-member": {
            "rename": "membership",
            "roles": {
                "source": {
                    "org": "organization",
                },
                "target": {
                    r".*": "member"
                }
            }
        },
        (r"org-aff.*?", "org", r"org|gpe-org"): {
            "rename": "part_whole",
            "roles": {
                "source": {
                    "org": "part",
                },
                "target": {
                    r"org|gpe-org": "whole"
                }
            }
        },
        "org-job": {
            "rename": "employment",
            "roles": {
                "source": {
                    "per": "employee",
                },
                "target": {
                    r".*?": "employer"
                }
            }
        },
        "org-repr": {
            "rename": "representation",
            "roles": {
                "source": {
                    r".*?": "representative",
                },
                "target": {
                    r".*?": "represented"
                }
            }
        },
        "owner": {
            "rename": "ownership",
            "roles": {
                "source": {
                    r"fac|other|loc": "property",
                    r"per|org|unk|gpe-org": "owner"
                },
                "target": {
                    r"fac|other|loc": "property",
                    r"per|org|unk|gpe-org": "owner"
                }
            }
        },
        "part-of": {
            "rename": "part_whole",
            "roles": {
                "source": {
                    r".*?": "part"
                },
                "target": {
                    r".*?": "whole"
                }
            }
        },
        r"per-repr|repr": {
            "rename": "representation",
            "roles": {
                "source": {
                    r".*?": "representative",
                },
                "target": {
                    r".*?": "represented"
                }
            }
        },
        "rel": {
            "rename": "other_interpersonal_relation",
            "roles": {
                "source": {
                    r".*?": "person_a"
                },
                "target": {
                    r".*?": "person_b"
                }
            }
        },
        "same": {
            "rename": "is_of_type",
            "roles": {
                "source": {
                    r".*?": "describee"
                },
                "target": {
                    r".*?": "descriptor"
                }
            }
        },
        r"tax|due|dues": {
            "rename": "due",
            "roles": {
                "source": {
                    "fac|loc": "property"
                },
                "target": {
                    "money": "interest",
                    r"org|per": "beneficiary",
                    "fac|loc": "property",
                    "date": "date",
                    "time": "interval",
                    "cause": "cause"
                }
            }
        },
        "title": {
            "rename": "holds_landed_title",
            "roles": {
                "source": {
                    "per": "holder"
                },
                "target": {
                    r"gpe-org|gpe-loc|gpe-gpe": "title"
                }
            }
        },
        "sale": {
            "roles": {
                "source": {
                    "fac": "property"
                },
                "target": {
                }
            }
        },
        r"consent|redemption": {
            "delete_source": True,
            "roles": {
                "target": {
                }
            }
        },
        "alias": {
            "rename": "name_variant",
            "roles": {
                "source": {
                    r".*?": "entity"
                },
                "target": {
                    r".*?": "name"
                }
            }
        }
    },
}
