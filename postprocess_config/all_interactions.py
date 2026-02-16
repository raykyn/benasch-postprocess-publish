# this config serves three purposes
# 1) we define for each event and state if it is state or event (based on the event class)
# 2) we use it to validate events and states (check if all assigned roles are allowed for that interaction and have the correct entity classes)
# 3) we perform speficic correction steps (usually project specifc), such as unifying different role names to a common name

# this config is very long and a bit complicated, we hope that the hgb config can serve as an example to understand it.
# NOTE: event here always refers to both events and states
# NOTE: Currently the validation has no 'required'-roles, feature, this is something that we aim to implement in the future.
CONFIG = {
    "event_generic_roles": [  # all roles defined here will be valid for all events
        {
            "name": "date",  # name of the role
            "alternative_names": ["date-range"],  # all names defined as alternative_names will be unified to the name defined above
            "classes": ["date"]  # only annotations of these classes will be seen as valid with this role
        },
        {
            "name": "place",
            "classes": ["place"]
        },
        {
            "name": "cause",
            "classes": ["#other", "#event", "#mod"]
        },
        {
            "name": "consequence",
            "classes": ["#other", "#event", "#mod"]
        },
        {
            "name": "other",
            "alternative_names": ["detail-other"],
        },
    ],
    "event_processing_entity_class_groupings": {  # a little helper to save some space and time in the following definitions
        "agent": ["per", "org", "gpe-org", "gpe-gpe"],
        "place": ["loc", "fac", "gpe-loc", "org", "per", "gpe-gpe"]
    },
    "event_postprocessing": [  # each dictionary in this list is an event or state definition
        {
            "name": "bid",  # name of the event
            "type": "event",  # either "event" or "state"
            "alternative_names": "outbid",  # can either be a single string or a list of strings
            "main_classes": [  # all valid "main" roles are defined here, see 'other_classes' for minor roles.
                {
                    "name": "bid",
                    "classes": ["money"]
                },
                {
                    "name": "bidder",
                    "classes": ["agent"]
                },
                {
                    "name": "property",
                    "classes": ["fac"]
                },
            ],
        },
        {
            "name": "civic-affiliation",
            "type": "state",
            "main_classes": [
                {
                    "name": "geopolitical-entity",
                    "classes": ["gpe-org"]
                },
                {
                    "name": "resident",
                    "classes": ["agent"]
                },
            ],
        },
        {
            "name": "consent",
            "type": "event",
            "main_classes": [
                {
                    "name": "consenting",
                    "classes": ["agent"]
                },
                {
                    "name": "subject",
                    "classes": ["#event", "#other"]
                },
                {
                    "name": "addressee",
                    "classes": ["agent"]
                },
            ],
        },
        {
            "name": "construction",
            "type": "event",
            "main_classes": [
                {
                    "name": "builder",
                    "classes": ["agent"]
                },
                {
                    "name": "property",
                    "classes": ["fac"]
                },
                {
                    "name": "structure",
                    "classes": ["fac", "#other"]
                },
            ],
        },
        {
            "name": "death",
            "type": "event",
            "main_classes": [
                {
                    "name": "deceased",
                    "classes": ["agent"]
                },
            ],
        },
        {
            "name": "debt",
            "type": "state",
            "alternative_names": ["arrear", "credit"],
            "main_classes": [
                {
                    "name": "capital",
                    "alternative_names": ["price"],
                    "classes": ["money"]
                },
                {
                    "name": "creditor",
                    "alternative_names": ["claimant", "beneficiary"],
                    "classes": ["agent"]
                },
                {
                    "name": "debitor",
                    "alternative_names": ["debtor"],
                    "classes": ["agent"]
                },
            ],
            "other_classes": [
                {
                    "name": "related-property",
                    "alternative_names": ["property"]
                },
                {
                    "name": "accumulated-interest",
                },
                {
                    "name": "capital-detail",
                    "alternative_names": ["capital"],  # a detail ABOUT capital
                }
            ]
        },
        {
            "name": "declaration",
            "type": "event",
            "main_classes": [
                {
                    "name": "proclaimer",
                    "classes": ["agent"]
                },
                {
                    "name": "content",
                    "classes": ["#other", "#event"]
                },
                {
                    "name": "addressee",
                    "classes": ["agent"]
                },
            ],
        },
        {
            "name": "due-payment",
            "type": "event",
            "alternative_names": "due",
            "main_classes": [
                {
                    "name": "interest",
                    "alternative_names": ["value", "insterest", "interes"],
                    "classes": ["money", "#event"]
                },
                {
                    "name": "property",
                    "classes": ["fac", "loc"]
                },
                {
                    "name": "payer",
                    "alternative_names": ["co-payer"],
                    "classes": ["agent"]
                },
                {
                    "name": "beneficiary",
                    "classes": ["agent"]
                },
                {
                    "name": "interval",
                    "alternative_names": ["date-interval", "date-intervall"],
                    "classes": ["time", "date"]
                },
                {
                    "name": "date-missing",
                    "classes": ["date"]
                },
                {
                    "name": "due-date",
                    "alternative_names": ["date-due"],
                    "classes": ["date"]
                },
                {
                    "name": "previous-due",
                    "alternative_names": ["due"],
                    "classes": ["#event"]
                },
                {
                    "name": "previous-payer",
                    "alternative_names": ["payer-prev"],
                    "classes": ["agent"]
                },
                {
                    "name": "capital",
                    "alternative_names": ["interest-redeemable_amount", "debt"],
                    "classes": ["money"]
                },
                {
                    "name": "interest-redeemable",
                    "alternative_names": ["detail-interest-redeemed", "detail-redeemed"],
                    "classes": ["#event", "money", "#other"]
                },
            ],
            "other_classes": [  # prefix all of these with "detail"
                {
                    "name": "interest-conv",
                    "alternative_names": ["conv", "conversion"],
                },
                {
                    "name": "interval-conv",
                    "alternative_names": ["date-interval-conv"],
                },
                {
                    "name": "other",
                    "alternative_names": ["due", "unclear"],
                },
                {
                    "name": "payment-mode",
                },
                {
                    "name": "distribution",
                    "alternative_names": ["distrib"],
                },
                {
                    "name": "effective-payer",
                    "alternative_names": ["payer-actual"],
                },
                {
                    "name": "alternative-payer",
                },
                {
                    "name": "proxy",
                },
                {
                    "name": "confirmation",
                },
                {
                    "name": "prev-interest",
                },
                {
                    "name": "quant",
                },
                {
                    "name": "property-detail",
                    "alternative_names": ["property"],
                },
                {
                    "name": "previous-property",
                    "alternative_names": ["property-prev"],
                },
                {
                    "name": "date-due-detail",
                    "alternative_names": ["date-due"],
                },
                {
                    "name": "alternative-interest",
                    "alternative_names": ["interest-alternative"],
                },
            ],
            "special_operations": [
                "check_if_payment_or_obligation",
            ]
        },
        {
            "name": "due-obligation",
            "type": "state",
            "main_classes": [
                {
                    "name": "interest",
                    "alternative_names": ["value", "insterest", "interes"],
                    "classes": ["money", "#event"]
                },
                {
                    "name": "property",
                    "alternative_names": ["collateral"],
                    "classes": ["fac", "loc"]
                },
                {
                    "name": "payer",
                    "alternative_names": ["co-payer"],
                    "classes": ["agent"]
                },
                {
                    "name": "beneficiary",
                    "classes": ["agent"]
                },
                {
                    "name": "interval",
                    "alternative_names": ["date-interval", "date-intervall"],
                    "classes": ["time", "date"]
                },
                {
                    "name": "date-missing",
                    "classes": ["date"]
                },
                {
                    "name": "due-date",
                    "alternative_names": ["date-due"],
                    "classes": ["date"]
                },
                {
                    "name": "previous-due",
                    "alternative_names": ["due"],
                    "classes": ["#event"]
                },
                {
                    "name": "previous-payer",
                    "alternative_names": ["payer-prev"],
                    "classes": ["agent"]
                },
                {
                    "name": "consenting",
                    "classes": ["agent", "#event"]
                },
                {
                    "name": "capital",
                    "alternative_names": ["interest-redeemable-amount", "debt"],
                    "classes": ["money"]
                },
                {
                    "name": "interest-redeemable",
                    "alternative_names": ["detail-interest-redeemed", "detail-redeemed"],
                    "classes": ["#event", "money", "#other"]
                },
            ],
            "other_classes": [
                {
                    "name": "interest-conv",
                    "alternative_names": ["conv", "conversion"],
                },
                {
                    "name": "interest-detail",
                },
                {
                    "name": "interval-conv",
                    "alternative_names": ["date-interval-conv"],
                },
                {
                    "name": "other",
                    "alternative_names": ["due", "unclear"],
                },
                {
                    "name": "payment-mode",
                },
                {
                    "name": "distribution",
                    "alternative_names": ["distrib"],
                },
                {
                    "name": "effective-payer",
                    "alternative_names": ["payer-actual"],
                },
                {
                    "name": "alternative-payer",
                },
                {
                    "name": "proxy",
                },
                {
                    "name": "confirmation",
                },
                {
                    "name": "prev-interest",
                },
                {
                    "name": "quant",
                },
                {
                    "name": "hereditary-owner",
                    "alternative_names": ["owner"],
                },
                {
                    "name": "part-redeemable",
                    "alternative_names": ["redeemable"],
                },
                {
                    "name": "property-detail",
                    "alternative_names": ["property"],
                },
                {
                    "name": "previous-property",
                    "alternative_names": ["property-prev"],
                },
                {
                    "name": "date-due-detail",
                    "alternative_names": ["date-due"],
                },
                {
                    "name": "alternative-interest",
                    "alternative_names": ["interest-alternative"],
                },
            ],
            "special_operations": [
            ]
        },
        {
            "name": "employment",
            "type": "state",  # either event or state
            "main_classes": [
                {
                    "name": "employee",
                    "classes": ["agent"]  # allowed entity classes for that role
                },
                {
                    "name": "employer",
                    "classes": ["agent"]
                },
            ],
        },
        {
            "name": "endowment",
            "type": "event",
            "main_classes": [
                {
                    "name": "property",
                    "classes": ["fac", "#event"] 
                },
                {
                    "name": "benefactor",
                    "classes": ["agent"]
                },
                {
                    "name": "beneficiary",
                    "classes": ["agent"]
                },
                {
                    "name": "consideration",
                    "classes": ["#other"]
                },
                {
                    "name": "consideration-object",
                    "classes": ["fac"]
                },
            ],
        },
        {
            "name": "family",
            "type": "state",  # either event or state
            "main_classes": [
                {
                    "name": "family-a",
                    "classes": ["per"]
                },
                {
                    "name": "family-b",
                    "classes": ["per"]
                },
            ],
        },
        {
            "name": "heritable-lease-grant",
            "type": "event", 
            "alternative_names": ["hereditary"],
            "main_classes": [
                {
                    "name": "lessee",
                    "classes": ["agent"],
                    "alternative_names": ["tenant"],
                },
                {
                    "name": "property",
                    "classes": ["fac"]
                },
                {
                    "name": "grantor",
                    "classes": ["agent"],
                    "alternative_names": ["owner"],
                },
                {
                    "name": "due",
                    "classes": ["#event"],
                },
                {
                    "name": "price",
                    "classes": ["money"],
                },
            ],
            "other_classes": [
                {
                    "name": "grantor-repr",
                    "alternative_names": ["owner-representative"],
                },
                {
                    "name": "other",
                    "alternative_names": [""],
                },
                {
                    "name": "context",
                },
            ],
            "special_operations": [
                "include_due_roles"
            ]
        },
        {
            "name": "heirship",
            "type": "state", 
            "main_classes": [
                {
                    "name": "heir",
                    "classes": ["agent"]
                },
                {
                    "name": "decedent",
                    "classes": ["agent"],
                    "alternative_names": ["bequeather"],
                },
                {
                    "name": "property",
                    "classes": ["fac"]
                },
            ],
            "other_classes": [
                {
                    "name": "property-detail",
                }
            ],
        },
        {
            "name": "holds-landed-title",
            "type": "state",  # either event or state
            "main_classes": [
                {
                    "name": "title",
                    "classes": ["gpe-org", "gpe-gpe", "gpe-loc", "loc", "org"]
                },
                {
                    "name": "holder",
                    "classes": ["agent"]
                },
            ],
        },
        {
            "name": "inheritance",
            "type": "event",
            "main_classes": [
                {
                    "name": "heir",
                    "classes": ["agent"]
                },
                {
                    "name": "decedent",
                    "classes": ["agent"],
                    "alternative_names": ["bequeather"],
                },
                {
                    "name": "property",
                    "classes": ["fac"]
                },
            ],
            "other_classes": [
                {
                    "name": "property-detail",
                }
            ],
        },
        {
            "name": "litigation",
            "type": "event",
            "main_classes": [
                {
                    "name": "party1",
                    "classes": ["agent"]
                },
                {
                    "name": "party2",
                    "classes": ["agent"]
                },
                {
                    "name": "subject",
                    "classes": ["#event", "#other", "fac"]
                },
                {
                    "name": "court",
                    "classes": ["place"]
                },
                {
                    "name": "decision",
                    "alternative_names": ["sanction"],
                    "classes": ["#event", "#other"]
                }
            ],
            "other_classes": [
                {
                    "name": "delay",
                    "alternative_names": ["delayed"]
                }
            ]
        },
        {
            "name": "membership",
            "type": "state",
            "main_classes": [
                {
                    "name": "organization",
                    "classes": ["org", "gpe-org"]
                },
                {
                    "name": "member",
                    "classes": ["agent"]
                },
            ],
        },
        {
            "name": "offer",
            "type": "event",
            "main_classes": [
                {
                    "name": "offeror",
                    "alternative_names": ["buyer"],
                    "classes": ["agent"]
                },
                {
                    "name": "offeree",
                    "classes": ["agent"]
                },
                {
                    "name": "property",
                    "classes": ["fac"]
                },
                {
                    "name": "price",
                    "classes": ["money"]
                },
            ],
            "other_classes": [
                {
                    "name": "event-detail",
                    "alternative_names": ["event"]
                }
            ]
        },
        {
            "name": "other-interpersonal-relation",
            "type": "state",
            "main_classes": [
                {
                    "name": "person-a",
                    "classes": ["agent"]
                },
                {
                    "name": "person-b",
                    "classes": ["agent"]
                }
            ]
        },
        {
            "name": "ownership",
            "type": "state",
            "main_classes": [
                {
                    "name": "owner",
                    "classes": ["agent"]
                },
                {
                    "name": "property",
                    "classes": ["fac"]
                },
                {
                    "name": "tenant",
                    "classes": ["agent"]
                }
            ]
        },
        {
            "name": "part-whole",
            "type": "state",
            "main_classes": [
                {
                    "name": "part"
                },
                {
                    "name": "whole"
                }
            ]
        },
        {
        "name": "payment",
        "type": "event",
        "main_classes": [
                {
                    "name": "sum",
                    "alternative_names": ["amount", "interest", "capital", "due"],
                    "classes": ["money", "#event"]
                },
                {
                    "name": "payer",
                    "classes": ["agent"]
                },
                {
                    "name": "beneficiary",
                    "alternative_names": ["receiver"],
                    "classes": ["agent"]
                },
                {
                    "name": "due-date",
                    "alternative_names": ["date-due"],
                    "classes": ["date"]
                },
                {
                    "name": "cause",
                    "classes": ["fac"]  # can have an additional class in this event
                },
            ],
            "other_classes": [
                {
                    "name": "other",
                    "alternative_names": ["unclear"],
                },
                {
                    "name": "detail_unclear"
                },
                {
                    "name": "alternative-payment",
                    "alternative_names": ["alternative"],
                },
            ]
        },
        {
            "name": "pledge",
            "type": "event",
            "main_classes": [
                {
                    "name": "property",
                    "alternative_names": ["collateral"],
                    "classes": ["fac"]
                },
                {
                    "name": "pledger",
                    "classes": ["agent"]
                },
                {
                    "name": "pledgee",
                    "classes": ["agent"]
                },
                {
                    "name": "capital",
                    "classes": ["money"]
                },
                {
                    "name": "property",
                    "classes": ["fac"]
                }
            ],
            "special_operations": [
                "include_due_roles"
            ]
        },
        {
            "name": "receipt",
            "type": "event",
            "main_classes": [
                {
                    "name": "payer",
                    "classes": ["agent"]
                },
                {
                    "name": "receiver",
                    "classes": ["agent"]
                },
            ]
        },
        {
            "name": "redemption",
            "type": "event",
            "alternative_names": ["assertion"],
            "main_classes": [
                {
                    "name": "beneficiary",
                    "alternative_names": ["claimant", "waiver"],
                    "classes": ["agent"]
                },
                {
                    "name": "redeemer",
                    "classes": ["agent"]
                },
                {
                    "name": "capital",
                    "alternative_names": ["capitel"],
                    "classes": ["money"]
                },
                {
                    "name": "collateral",
                    "alternative_names": ["property"],
                    "classes": ["fac"]
                },
                {
                    "name": "due",
                    "classes": ["#event"]
                },
                {
                    "name": "interest",
                    "alternative_names": ["interest-original"],
                    "classes": ["money"]
                },
            ],
            "other_classes": [  # prefix all of these with "detail"
                {
                    "name": "interest-conv",
                    "alternative_names": ["conv"]
                },
                {
                    "name": "capital-original",
                },
                {
                    "name": "interest-remaining",
                },
                {
                    "name": "other",
                    "alternative_names": ["unclear"]
                }
            ],
            "special_operations": [
                "include_due_roles"
            ]
        },
        {
            "name": "rent-purchase",
            "type": "event",
            "alternative_names": "rent",
            "main_classes": [
                {
                    "name": "seller",
                    "alternative_names": ["debtor"],
                    "classes": ["agent"]
                },
                {
                    "name": "buyer",
                    "alternative_names": ["creditor"],
                    "classes": ["agent"]
                },
                {
                    "name": "collateral",
                    "alternative_names": ["property"],
                    "classes": ["fac", "#event"]
                },
                {
                    "name": "price",
                    "alternative_names": ["capital", "interest-redeemable-amount"],
                    "classes": ["money"]
                },
                {
                    "name": "due",
                    "classes": ["#event"]
                },
                {
                    "name": "consenting",
                    "classes": ["agent", "#event"]
                }
            ],
            "other_classes": [
                {
                    "name": "prev-creditor",
                    "alternative_names": ["creditor-prev"],
                },
                {
                    "name": "time-past"
                },
            ],
            "special_operations": [
                "include_due_roles"
            ]
        },
        {
            "name": "representation",
            "type": "state",
            "main_classes": [
                {
                    "name": "represented",
                    "classes": ["agent"]
                },
                {
                    "name": "representative",
                    "classes": ["agent"]
                }
            ]
        },
        {
            "name": "revocation",
            "type": "event",
            "main_classes": [
                {
                    "name": "proclaimer",
                    "classes": ["agent"]
                },
                {
                    "name": "revoker",
                    "classes": ["agent"]
                },
                {
                    "name": "content",
                    "classes": ["#other"]
                }
            ]
        },
        {
            "name": "property-purchase",
            "type": "event",
            "alternative_names": ["acquisition", "sale"],
            "main_classes": [
                {
                    "name": "buyer",
                    "alternative_names": ["claimant"],
                    "classes": ["agent"]
                },
                {
                    "name": "seller",
                    "classes": ["agent"]
                },
                {
                    "name": "witness",
                    "classes": ["agent"]
                },
                {
                    "name": "consenting",
                    "classes": ["agent", "#event"]
                },
                {
                    "name": "property",
                    "classes": ["fac"]
                },
                {
                    "name": "price",
                    "alternative_names": ["money"],
                    "classes": ["money", "#event"]
                },
            ],
            "other_classes": [
                {
                    "name": "payment-mode",
                },
                {
                    "name": "property-detail",
                    "alternative_names": ["property-part", "part", "property"]
                },
                {
                    "name": "offer"  # ev. zu Bezug umwandeln?
                },
                {
                    "name": "payment-detail",
                    "alternative_names": ["payment"]
                },
                {
                    "name": "price-conv",
                    "alternative_names": ["conv"]
                },
                {
                    "name": "condition"
                },
                {
                    "name": "context"
                },
                {
                    "name": "event"  # ?
                },
                {
                    "name": "rights"
                },
                {
                    "name": "seizure"
                },
                {
                    "name": "support"
                },
                {
                    "name": "temp"
                },
                {
                    "name": "time-past",
                    "alternative_names": ["time-past-kuerzlich"]
                }
            ],
        },
        {
            "name": "sanction",
            "type": "event",
            "main_classes": [
                {
                    "name": "court",
                    "classes": ["place"]
                },
                {
                    "name": "sanctioned",
                    "classes": ["agent"]
                },
                {
                    "name": "party1",
                    "classes": ["agent"]
                },
                {
                    "name": "party2",
                    "classes": ["agent"]
                },
                {
                    "name": "procedure",
                    "classes": ["#event", "#other"]
                },
                {
                    "name": "decision",
                    "alternative_names": ["consequence", "subject"],
                    "classes": ["#event", "#other"]
                },
            ],
            "other_classes": [
                {
                    "name": "decision-alternative"
                },
            ]
        },
        {
            "name": "seizure",
            "type": "event",
            "main_classes": [
                {
                    "name": "property",
                    "classes": ["fac", "#event"]
                },
                {
                    "name": "claimant",
                    "classes": ["agent"]
                },
                {
                    "name": "debitor",
                    "alternative_names": ["debtor"],
                    "classes": ["agent"]
                },
                {
                    "name": "executor",
                    "classes": ["agent"]
                },
                {
                    "name": "capital",
                    "classes": ["money"]
                },
                {
                    "name": "date-affirmed",
                    "alternative_names": ["date-affirm"],
                    "classes": ["date"]
                },
            ],
            "other_classes": [
                {
                    "name": "offer"
                },
                {
                    "name": "other"
                }
            ]
        },
        {
            "name": "settlement",
            "type": "event",
            "main_classes": [
                {
                    "name": "subject",
                    "classes": ["#event", "#other"]
                },
                {
                    "name": "party1",
                    "classes": ["agent"]
                },
                {
                    "name": "party2",
                    "classes": ["agent"]
                }
            ]
        },
        {
            "name": "testament",  # only declares intention, not the actual inheritance
            "type": "event",
            "main_classes": [
                {
                    "name": "bequeather",
                    "classes": ["agent"]
                },
                {
                    "name": "beneficiary",
                    "alternative_names": ["heir", "erbe"],
                    "classes": ["agent"]
                },
                {
                    "name": "property",
                    "classes": ["fac", "money", "#event"]
                },
            ],
            "other_classes": [
                {
                    "name": "considered"
                },
                {
                    "name": "property-detail"
                }
            ]
        },
        {
            "name": "topological",
            "type": "state",
            "main_classes": [
                {
                    "name": "location-a",
                    "alternative_names": ["person-a"],
                    "classes": ["place"]
                },
                {
                    "name": "location-b",
                    "alternative_names": ["person-b"],
                    "classes": ["place"]
                },
            ]
        },
        {
            "name": "transfer",
            "type": "event",
            "main_classes": [
                {
                    "name": "property",
                    "classes": ["fac"]
                },
                {
                    "name": "owner-prev",
                    "alternative_names": ["issuer"],
                    "classes": ["agent"]
                },
                {
                    "name": "owner-new",
                    "alternative_names": ["owner", "recipient"],
                    "classes": ["agent"]
                },
                {
                    "name": "value",
                    "classes": ["money"]
                }
            ],
            "other_classes": [
                {
                    "name": "owner-new-detail",
                    "alternative_names": ["owner-new-support"],
                }
            ]
        },
        {
            "name": "other",
            "type": "event",
            "alternative_names": "unclear",
            "main_classes": [
                # allow all
            ]
        },
        {
            "name": "workplace",
            "type": "state",
            "main_classes": [
                {
                    "name": "worker",
                    "classes": ["agent"]
                },
                {
                    "name": "location",
                    "classes": ["place"]
                }
            ]
        },
        {
            "name": "name-variant",
            "type": "state",
            "main_classes": [
                {
                    "name": "entity",
                },
                {
                    "name": "name",
                    "classes": ["name"],
                }
            ]
        },
        {
            "name": "bequest",
            "desc": "This event describes agents bequeathing some property to each other.",
            "type": "event",
            "alternative_names": [],
            "main_classes": [
                {
                    "name": "bequeather",
                    "desc": "",
                    "alternative_names": [],
                    "classes": ["agent"],
                    # if there is no beneficiary annotated, the agents bequeathe each other
                    # technically a pronoun should be annotated, but sometimes it isnt :-( TODO
                    "special_operations": ["if_no_beneficiary_make_bequeathers_also_beneficiaries"]
                },
                {
                    "name": "beneficiary",
                    "desc": "",
                    "alternative_names": [],
                    "classes": ["agent"]
                },
                {
                    "name": "property",
                    "desc": "",
                    "alternative_names": [],
                    "classes": ["fac"]
                }
            ],
            "other_classes": [  # prefix all of these with "detail"
                {
                    "name": "property-detail",
                }
            ]
        },
    ]
}