# Read CAS XMI 1.1 files and enrich them with postprocessing. Output beNASch-XML.

from lxml import etree as et
import os
import re
import pathlib
from postprocess_config import implied_interactions, layer_processing, renaming, defaults, all_interactions

CONFIG = layer_processing.CONFIG
CONFIG.update(renaming.CONFIG)
CONFIG.update(defaults.CONFIG)
CONFIG.update(implied_interactions.CONFIG)
CONFIG.update(all_interactions.CONFIG)

OUTFOLDER = ""

SPAN_LAYER = CONFIG["span_layer"]  # the name of the span layer in the XMI file
RELATION_LAYER = CONFIG["relation_layer"]  # the name of the relation layer in the XMI file

DEBUG = True  # True writes the work trees to files
DEBUGFOLDER = "./data/debug/"

def write_text(text_elem, text, in_root):
    """
    text string is transformed into single token elements.
    We use line elements to keep some of the original document structure intact.
    We also return start and end dictionaries to make matching the tokens
    to the annotations easier in the next steps.

    NOTE: THIS DOES NOT PERFORM ANY "PROPER" PREPROCESSING!

    TODO: How to represent sentences and line breaks in this new system? should we even keep doing it like this?
    """
    current_index = 0
    start_index_dict = {}
    end_index_dict = {}

    tokens = in_root.findall(".//type5:Token", namespaces={"type5":"http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore"})
    for token in sorted(tokens, key=lambda x: int(x.get("begin"))):
        start = int(token.get("begin"))
        end = int(token.get("end"))
        token_elem = et.SubElement(text_elem, "token", token_id=str(current_index))
        token_elem.text = text[start:end]
        start_index_dict[start] = current_index
        end_index_dict[end] = current_index
        current_index += 1

    return start_index_dict, end_index_dict


def get_node_priority(node):
    """
    This makes sure that when sorting the spans, desc-spans will be processed BEFORE 
    mentions, values, etc. 
    This is relevant especially for desc-spans that completely overlap with an
    entity mention or value, such as is often the case for desc.owner.

    This function may need expansion later on if more such cases exist.
    """
    try:
        l = node.get(CONFIG["priority_layer"]).lower().split(".")[0]
    except:
        return CONFIG["priorities"]["default"]
    if l in CONFIG["priorities"]:
        return CONFIG["priorities"][l]
    else:
        return CONFIG["priorities"]["default"]
    

def convert_char_to_token_idx(start_index_dict, end_index_dict, start, end, entity):
    # transform character index to token index
    token_start = start_index_dict[start]
    #try:
    token_end = end_index_dict[end]
    """
    except KeyError:
        # Inception performs an implicit tokenization, which allows annotations
        # to be set outside our own preprocessing. This can lead to annotations
        # ending inside tokens as defined by our preprocessing/system
        # to circumvent this problem, we simply stretch the tag to the end of the token
        guard = 10000
        while end not in end_index_dict and guard > 0:
            end += 1
            guard -= 1
        token_end = end_index_dict[end]
        
        print(f"WARNING: An annotation ended inside a token. Check this error manually for annotation with id {entity.get('{http://www.omg.org/XMI}id')}!")
    """
    return token_start, token_end


def check_overlaps(spans):
    """
    overlaps are not allowed in this system as they will lead to unexpected behavious 
    when building the tree. 
    We check for overlaps and:
    - if overlap is length 1, fix it and print a warning.
    - if overlap is longer, print an error.
    """
    for i, span in enumerate(spans):
        begin = int(span.get("begin"))
        end = int(span.get("end"))
        for other_span in spans[i+1:]:
            if span == other_span:
                continue
            other_begin = int(other_span.get("begin"))
            other_end = int(other_span.get("end"))
            # check if spans overlap
            #print(begin, other_begin, end, other_end)
            if begin > other_begin and begin <= other_end:
                if end > other_end:
                    # overlap detected, check length
                    if begin - other_begin == 1:
                        span.set("begin", str(other_begin))
                        print(f"WARNING: Overlap detected between spans {span.get('{http://www.omg.org/XMI}id')} and {other_span.get('{http://www.omg.org/XMI}id')}. Overlap is only length 1, trying to fix it.")
                    elif end - other_end == 1:
                        span.set("end", str(other_end))
                        print(f"WARNING: Overlap detected between spans {span.get('{http://www.omg.org/XMI}id')} and {other_span.get('{http://www.omg.org/XMI}id')}. Overlap is only length 1, trying to fix it.")
                    else:
                        print(f"ERROR: Overlap detected between spans {span.get('{http://www.omg.org/XMI}id')} and {other_span.get('{http://www.omg.org/XMI}id')}. This will likely lead to unexpected behaviour down the line.")
            elif other_begin > begin and other_begin <= end:
                if other_end > end:
                    # overlap detected, check length
                    if other_begin - begin == 1:
                        other_span.set("begin", str(begin))
                        print(f"WARNING: Overlap detected between spans {span.get('{http://www.omg.org/XMI}id')} and {other_span.get('{http://www.omg.org/XMI}id')}. Overlap is only length 1, trying to fix it.")
                    elif other_end - end == 1:
                        other_span.set("end", str(end))
                        print(f"WARNING: Overlap detected between spans {span.get('{http://www.omg.org/XMI}id')} and {other_span.get('{http://www.omg.org/XMI}id')}. Overlap is only length 1, trying to fix it.")
                    else:
                        print(f"ERROR: Overlap detected between spans {span.get('{http://www.omg.org/XMI}id')} and {other_span.get('{http://www.omg.org/XMI}id')}. This will likely lead to unexpected behaviour down the line.")


def create_work_tree(in_root, out_root, document_text, start_index_dict, end_index_dict):
    """
    Build a hierarchical tree from all spans in the XMI.
    """
    spans = in_root.findall(f"./custom:{SPAN_LAYER}", namespaces={"custom":"http:///custom.ecore"})

    # check for and fix overlapping tags
    check_overlaps(spans)

    sorted_spans = []
    for ent in spans:
        sorted_spans.append((ent, int(ent.get("begin")), int(ent.get("end")), get_node_priority(ent)))
    sorted_spans.sort(key=lambda x: (x[1], -x[2], x[3]))
    work_root = out_root

    spans_node = et.SubElement(work_root, "spans")
    parent_node = spans_node

    for entity, start, end, _ in sorted_spans:
        text_content = document_text[start:end]
        start, end = convert_char_to_token_idx(start_index_dict, end_index_dict, start, end, entity)

        while(parent_node != spans_node):
            if end <= int(parent_node.get("end")):
                current_node = et.SubElement(parent_node, "span", id=entity.get("{http://www.omg.org/XMI}id"), start=str(start), end=str(end), text=text_content)
                for fo, fn in CONFIG["span_features"].items():
                    field, required = fn["field"], fn["required"]
                    if isinstance(field, list):
                        field = ".".join([entity.get(x) for x in field if entity.get(x) is not None])  # in inception, it's more practical to split them, but not here
                    else:
                        field = entity.get(field)
                    if not field and required:
                        print(f"WARNING: Missing required fields {fn['field']} for entity {entity.get('{http://www.omg.org/XMI}id')}!")
                        current_node.set(fo, "other")
                    elif field:
                        current_node.set(fo, field.lower())
                break
            else:
                parent_node = parent_node.getparent()
        else:
            current_node = et.SubElement(parent_node, "span", id=entity.get("{http://www.omg.org/XMI}id"), start=str(start), end=str(end), text=text_content)
            for fo, fn in CONFIG["span_features"].items():
                field, required = fn["field"], fn["required"]
                if isinstance(field, list):
                    field = ".".join([entity.get(x) for x in field if entity.get(x) is not None])  # in inception, it's more practical to split them, but not here
                else:
                    field = entity.get(field)
                if not field and required:
                    print(f"WARNING: Missing required fields {fn['field']} for entity {entity.get('{http://www.omg.org/XMI}id')}!")
                    current_node.set(fo, "other")
                elif field:
                    current_node.set(fo, field.lower())
        parent_node = current_node

    relations = in_root.findall(f".//custom:{RELATION_LAYER}", namespaces={"custom":"http:///custom.ecore"})
    relation_node = et.SubElement(work_root, "relations")
    for relation in relations:
        current_node = et.SubElement(
            relation_node, 
            "relation", 
            {
            "id":relation.get("{http://www.omg.org/XMI}id"), 
            "from":relation.get("Governor"),
            "to":relation.get("Dependent"),
            }
            )
        for fo, fn in CONFIG["relation_features"].items():
            field, required = fn["field"], fn["required"]
            if relation.get(field) is None:
                if required:
                    print(f"WARNING: Missing required field {field} for relation {relation.get('{http://www.omg.org/XMI}id')}!")
                    current_node.set(fo, relation.get("other"))
            else:
                current_node.set(fo, relation.get(field).lower())


def process_remaining_fields(fields, remaining_fields, debug_id):
    other_info = CONFIG["schema_info"][fields]
    out_dict = {}
    for feature, possible_values in other_info.items():
        for rf in remaining_fields:
            if rf in possible_values:
                out_dict[feature] = rf
                remaining_fields.remove(rf)
                break
        else:
            out_dict[feature] = possible_values[0]  # default value
    if remaining_fields and not (len(remaining_fields) == 1 and remaining_fields[0] == ""):
        print(f"ERROR: Unrecognized information {remaining_fields} in span {debug_id}. Ignoring it.")
    return out_dict


def process_spans(out_root):
    """
    Process the spans and write them to the output XML tree.
    :param work_root: The root element of the work XML tree.
    :param out_root: The root element of the output XML tree.
    """

    def do_parent_head_instructions(parent, child, instructions):
        parent_value = parent.get(feature).split(".")
        if parent_value[0] in instructions:
            parent_instruction = instructions[parent_value[0]]
            if "add_features_to_head" in parent_instruction:
                actions = parent_instruction["add_features_to_head"]
                for new_feature, new_value in actions.items():
                    child.set(new_feature, new_value)
            if "copy_by_index_to_head" in parent_instruction:
                actions = parent_instruction["copy_by_index_to_head"]
                for new_feature, copy_idx in actions.items():
                    # first check it isn't part of any of the other_fields values
                    if copy_idx < len(parent_value) and parent_value[copy_idx] not in CONFIG["schema_info"]["other_fields_values"]:
                        new_value = parent_value[copy_idx]
                    else:
                        new_value = CONFIG["head_defaults"].get(parent.get("class"))
                    try:
                        child.set(new_feature, new_value)
                    except TypeError:
                        print(f"WARNING: Could not assign head type for {child.get('id')}! Check if the head defaults are properly defined for class {parent.get('class')} and if the class of the parent {parent.get('id')} is correctly assigned.")
                        child.set(new_feature, CONFIG["head_defaults"]["default"])
            if "add_feature_to_head" in parent_instruction:
                actions = parent_instruction["add_feature_to_head"]
                for new_feature, new_value in actions.items():
                    child.set(new_feature, new_value)
        else:
            return
        
    def rename_attribute(field, instr):
        if field in CONFIG["conversions"] and CONFIG["conversions"][field]:
            if instr in CONFIG["conversions"][field]:
                return CONFIG["conversions"][field][instr]  # TODO: extend to use regex
        return instr
    
    def get_feature_by_coreference(span):
        """
        For pronouns, we can input some of their classes by looking at the entities that they're linked with.
        """
        guard = 10000
        target = span
        while True and guard > 0:
            coref_relation = out_root.find(f"./relations/relation[@from='{target.get('id')}']")
            if coref_relation is None:
                # no coreference relation found
                # supply a unk class instead
                # print a warning (TODO: put this in the settings as an option)
                span.set("class", "unk")
                span.set("numerus", "unk")
                print(f"WARNING: No coreference relation found for pronoun class in span {span.get('id')}!")
                break
            target = out_root.find(f"./spans//span[@id='{coref_relation.get('to')}']")
            # is the target a pronoun too?
            if target.get("class") != "pro":
                if target.get("element") == "list":
                    span.set("class", target.get("class"))
                    span.set("numerus", "grp")
                elif target.get("element") == "appo":
                    # if the coref targets an apposition
                    # print a warning, but pass class and numerus of the parent
                    print(f"WARNING: Coreference relation targetting apposition in span {span.get('id')}!")
                    span.set("class", target.getparent().get("class"))
                    span.set("numerus", target.getparent().get("numerus"))
                else:
                    span.set("class", target.get("class"))
                    span.set("numerus", target.get("numerus"))
                break
            guard -= 1

    for span in out_root.findall("./spans//span"):
        for feature, instructions in CONFIG["span_features"].items():
            instructions = instructions["process_instructions"]
            if not instructions:  # this signifies to ignore the feature
                continue
            feature_value = span.get(feature).split(".")
            for regex_key in instructions:
                if re.match(regex_key, feature_value[0]):
                    instruction = instructions[regex_key]
                    new_span = span  # TODO: unify variables
                    # process the feature according to the instructions
                    for instr_name, instr_value in instruction.items():
                        if instr_name == "new_features":
                            for new_feature, new_value in instr_value.items():
                                new_span.set(new_feature, new_value)
                        elif instr_name == "copy_features":
                            for copy_feature, copy_value in instr_value.items():
                                if span.get(copy_value) is not None:
                                    new_span.set(copy_feature, span.get(copy_value))
                        elif instr_name == "add_features_to_head":
                            pass  # easier to do this as we process the head
                        elif instr_name == "copy_by_index_to_head":
                            pass  # easier to do this as we process the head
                        elif instr_name == "add_feature_to_head":
                            pass  # easier to do this as we process the head
                        elif instr_name == "add_feature_by_index":
                            for idx, new_feature in instr_value.items():
                                if idx < len(feature_value):
                                    new_span.set(new_feature, rename_attribute(new_feature, feature_value[idx]))
                                else:
                                    new_span.set(new_feature, "")  # NOTE: possibly implement using a default value here (also defined in config)
                        elif instr_name == "add_optional_feature_by_index":
                            for idx, new_feature in instr_value.items():
                                # only adds the feature if the label is long enough to support it
                                # also only adds it if the feature is filled (pro..same would not overwrite class label this way)
                                if len(feature_value) > idx and feature_value[idx]:
                                    new_span.set(new_feature, feature_value[idx])
                        elif instr_name == "add_remaining_fields_by_schema_info":
                            out_dict = process_remaining_fields("other_fields", feature_value[instr_value:], span.get("id"))
                            for f, v in out_dict.items():
                                new_span.set(f, v)
                        elif instr_name == "add_remaining_fields_by_event_info":
                            out_dict = process_remaining_fields("event_fields", feature_value[instr_value:], span.get("id"))
                            for f, v in out_dict.items():
                                new_span.set(f, v)
                        elif instr_name == "add_all_other_fields_as":
                            remaining_class = ".".join(feature_value[1:])
                            new_span.set(instruction["add_all_other_fields_as"], remaining_class)
                        elif instr_name == "get_features_from_parent" and instr_value:
                            if span.get("class"):
                                continue
                            parent = span.getparent()
                            if parent.tag != "spans":
                                do_parent_head_instructions(parent, new_span, instructions)
                            else:
                                print(f"WARNING: Parent of span {span.get('id')} not found!")
                                continue
                        elif instr_name == "requires_head" and instr_value:
                            # if no head is present, try to add one
                            for child in span:
                                child_value = child.get(feature).split(".")
                                if child_value[0] == "head":
                                    break
                            else:
                                # No head is present, handle the case here
                                # easy case: no other children exist, simply make the whole span the head
                                if len(span) == 0:
                                    start = span.get("start")
                                    end = span.get("end")
                                # complex case: other children exist, supplement the head with all text till the first child,
                                # or if that would yield a span of 0, from last child to end. also print a warning when this happens.
                                else:
                                    # print warning message
                                    print(f"WARNING: No head found for span {span.get('id')}, other children present! Trying to supplement a head before first or after last child.")
                                    # get the first child
                                    first_child = span[0]
                                    # get the start and end of the first child
                                    first_child_start = int(first_child.get("start"))
                                    # check if the head would be empty
                                    if first_child_start - int(span.get("start")) > 0:
                                        start = span.get("start")
                                        end = str(first_child_start - 1)
                                    elif int(span.get("end")) - (int(span[-1].get("end"))) > 0:
                                        start = str(int(span[-1].get("end"))+1)
                                        end = span.get("end")
                                    else:
                                        print(f"ERROR: No head found for span {span.get('id')}, other children present! Failed to find space to supplement a head.")
                                        continue
                                new_head_span = et.SubElement(new_span, "span", {
                                    "id": span.get("id") + "_head",
                                    "start": start,
                                    "end": end,
                                    "element": "head",
                                })
                                do_parent_head_instructions(span, new_head_span, instructions)
                                # getting the text is somewhat difficult
                                new_head_span.set("text", " ".join([out_root.find(f"./text//token[@token_id='{x}']").text for x in range(int(start), int(end)+1)]))
                        elif instr_name == "process_eventelement":
                            pass  # depreciated, should be handled by the event processing instructions instead
                        elif instr_name == "print_warning_to_check":
                            print(f"WARNING: span {span.get('id')} is marked as {feature_value[0]}! Please check the annotation.")
                        else:
                            if instr_name in [
                                "get_class_from_child_references",
                                "if_no_class_get_class_from_head"
                            ]:
                                continue
                            print(f"WARNING: Unknown instruction {instr_name} for feature {feature} in span {span.get('id')}!")
                            continue
                    # set the text of the new span
                    new_span.set("text", span.get("text"))
                    break
            else:
                print(f"WARNING: Unknown {feature} value {feature_value[0]} for span {span.get('id')}!")
                continue

    def get_class_from_children(span):
        """
        Hardcoded for now!
        """
        all_classes = set()
        for child in span:
            if child.get("element") == "reference":
                designated_class = child.get("class").split("_")[0]
                if designated_class != "pro":
                    all_classes.add(designated_class)
        return ";".join(sorted(all_classes))

    # NOTE: process certain functions after everything else has been processed, but before pronouns try to find their class
    for span in out_root.findall("./spans//span"):
        for feature, instructions in CONFIG["span_features"].items():
            instructions = instructions["process_instructions"]
            if not instructions or span.get(feature) is None:
                continue
            feature_value = span.get(feature).split(".")
            for regex_key in instructions:
                if re.match(regex_key, feature_value[0]):
                    instruction = instructions[regex_key]
                    for instr_name, instr_value in instruction.items():
                        if instr_name == "get_class_from_child_references":
                            new_class = get_class_from_children(span)
                            span.set("class", new_class)
                        elif instr_name == "if_no_class_get_class_from_head":
                            if span.get("class") is None or span.get("class") == "":
                                heads = span.xpath("./span[@element='head']")
                                classes = set([h.get("class") for h in heads])
                                span.set("class", ";".join(sorted(classes)))

    # NOTE: worth considering if this should be in a separate function AFTER relations and events have been processed
    for span in out_root.findall("./spans//span"):
        if span.get("element") == "reference" and span.get("class") == "pro":
            # some info requires other info to already have been processed, so we add those instructions in a second loop
            get_feature_by_coreference(span)


def process_relations(out_root):
    relations = out_root.findall("./relations/relation")
    for relation in relations:
        for feature, instructions in CONFIG["relation_features"].items():
            instructions = instructions["process_instructions"]
            if not instructions:  # no special operations
                continue
            feature_value = relation.get(feature).split(".")
            for regex_key in instructions:
                if re.match(regex_key, feature_value[0]):
                    instruction = instructions[regex_key]
                    for instr_name, instr_value in instruction.items():
                        if instr_name == "new_features":
                            for new_feature, new_value in instr_value.items():
                                relation.set(new_feature, new_value)
                        elif instr_name == "add_feature_by_index":
                            for idx, new_feature in instr_value.items():
                                relation.set(new_feature, feature_value[idx])
                        elif instr_name == "add_remaining_fields_by_event_info":
                            out_dict = process_remaining_fields("event_fields", feature_value[instr_value:], relation.get("id"))
                            for f, v in out_dict.items():
                                relation.set(f, v)
                        elif instr_name == "add_all_other_fields_as":
                            remaining_class = ".".join(feature_value[1:])
                            relation.set(instruction["add_all_other_fields_as"], remaining_class)
                    break


def write_events(out_root):
    """
    We write events and situations here.
    - the trigger is not the important part, but instead the event-span
    - if no eventspan is annotated, but a trigger is, the evspan is extrapolated
    - event-spans, trigger and roles do not necessarily need an id if only 1 event with no subevents is in that annotation level
    """

    def get_roles(role_field, is_evt=False):
        if role_field is None:
            if is_evt:
                return [{"role": "evt", "id": [""]}]
            else:
                return {}
        roles = []
        rolefields = role_field.split(";")
        for rf in rolefields:
            rf = rf.split(".")
            if len(rf) == 1 or (len(rf) == 2 and rf[1] == ""):
                if rf[0].isnumeric() and is_evt:  # if the role is just a number, we assume it's an event id (for subevents)
                    roles.append({"role": "evt", "id": list(rf[0])})
                else:
                    roles.append({"role": rf[0], "id": [""]})
            elif len(rf) == 2:
                if ":" in rf[1]:
                    roleid = rf[1].split(":")
                    roles.append({"role": rf[0], "id": roleid})
                else:    
                    roleid = list(rf[1])
                    roles.append({"role": rf[0], "id": roleid})
            else:
                roles.append({"role": rf[0], "id": list(rf[1:])})
        # if it's an event, it should now have an evt role otherwise supply one
        if is_evt and not any([r["role"] == "evt" for r in roles]):
            roles.append({"role": "evt", "id": [""]})
        return roles
    
    def apply_role_name_conversions(entity_type):
        for o, r in CONFIG["conversions"]["role_names"].items():
            entity_type = re.sub(o, r, entity_type)
        return entity_type
    
    def create_event(event, event_node, event_triggers, participants, running_ids):
        running_ids += 1
        for event_trigger in event_triggers:
            trigger_node = et.SubElement(event_node, "trigger", start=event_trigger.get("start"), end=event_trigger.get("end"), text=event_trigger.get("text"), ref=event_trigger.get("id"))
        # write list of Subevents
        # first identify distinct subevent ids
        subevent_ids = set([".".join(roleinfo["id"]) for _, roleinfo in participants])
        dictinct_ids = []
        for si in subevent_ids:
            for si2 in subevent_ids:
                if si == si2:
                    continue
                if si2.startswith(si):
                    break
            else:
                dictinct_ids.append(si)
        # each distinct id spawns its own subevent
        for num, di in enumerate(sorted(dictinct_ids)):
            subevent_node = et.SubElement(event_node, "event", event_id=event_node.get("event_id")+"."+str(num))
            for role_elem, roleinfo in participants:
                roleid = ".".join(roleinfo["id"])
                if di.startswith(roleid):
                    if role_elem.tag == "spans":
                        print(f"ERROR: Describing Element (e.g. Apposition, Attribute) without List or Reference to nest it! See {event.get('id')}")
                        continue
                    # TODO: Implement handling of appositions inside lists (project role to all members of the list instead)
                    #print(str(role_elem.tag), str(role_elem.attrib).encode("utf8"))
                    ref_class = role_elem.get("class") if role_elem.get("class") is not None else role_elem.find("span[@element='head']").get("class")
                    role_node = et.SubElement(subevent_node, "role", role=apply_role_name_conversions(roleinfo["role"].strip()), ref=role_elem.get("id"), ref_class=ref_class)
                    role_node.set("text", role_elem.get("text"))
                    if role_elem in elems_with_roles:
                        # check first if it's in there,
                        # because one role elem can be in multiple subevents
                        elems_with_roles.remove(role_elem)

            # change role names according to config
            if subevent_node.find("role[@role='source']") is not None:
                for term, info in CONFIG["implicit_event_processing"].items():
                    if type(term) == str:
                        m = re.match(term, event_node.get("class"))
                        if m:
                            break
                    elif type(term) == tuple:
                        m = re.match(term[0], event_node.get("class"))
                        if m:
                            m = re.match(term[1], subevent_node.find("role[@role='source']").get("ref_class"))
                            if m:
                                #print(et.tostring(subevent_node.getparent()))
                                m = re.match(term[2], subevent_node.find("role[@role='target']").get("ref_class"))
                                if m:
                                    break
                    else:
                        print(f"ERROR: Unknown term type {type(term)} in implicit event processing!")
                        exit()
                else:
                    print("WARNING: No event definition found for event {0} (while processing Element {1})!".format(subevent_node.get("event_id"), event.get("id")))
                    info = None
                if info is not None:
                    if "no_event" in info and info["no_event"]:
                        event_node.getparent().remove(event_node)
                        break
                    # rename event, source and target
                    # only rename the event if it's the last subevent! (or the ones before won't match)
                    if "rename" in info and num == len(dictinct_ids) - 1:
                        event_node.set("class", info["rename"])
                    for role in subevent_node.findall("./role"):
                        old_role = role.get("role")
                        if "delete_source" in info and old_role == "source":
                            subevent_node.remove(role)
                            continue
                        for r in info["roles"]:
                            if old_role == r:
                                for template, new_role in info["roles"][r].items():
                                    if re.match(template, role.get("ref_class")):
                                        role.set("role", new_role)
                                        break
                                else:
                                    print(f"WARNING: No role definition found for role {role.get('role')} in event {subevent_node.get('event_id')} (while processing Element {event.get('id')})!")
                        if old_role == "source" and len(subevent_node.findall(f"./role[@role='{new_role}']")) > 1:
                            # special case: ignore the source when there is already another role which has the new_role role
                            # print(f"TESTING: Removing a source role because another has been found in event {subevent_node.get('event_id')}")
                            subevent_node.remove(role)

        return running_ids
    
    # update span lengths after other events have been added
    def update_eventspan_length(event, events_node, already_processed):
        already_processed.append(event)
        for subevent in event.findall("./event"):
            for role in subevent.findall("./role"):
                ref = role.get("ref")
                corr = events_node.find("./eventGroup[@event_id='" + ref + "']")
                if corr is not None:
                    if corr not in already_processed:
                        update_eventspan_length(corr, events_node, already_processed)
                    event.set("start", str(min([int(event.get("start")), int(corr.get("start"))])))
                    event.set("end", str(max([int(event.get("end")), int(corr.get("end"))])))

    def solve_list(list_elem, collector, prev_roles, transfer_roles=False):
        """
        spans inside lists may have relevant roles
        so we need to also look through lists and return all their children
        recursively. Also give all roles of a list to all its children
        """
        if list_elem.get("role"):
            prev_roles.append(list_elem.get("role")) 
        for child in list_elem:
            if child.get("element") in ["reference", "trigger", "eventspan", "value"]:
                if transfer_roles and prev_roles:
                    if child.get("role"):
                        child.set("role", child.get("role") + ";" + ";".join(prev_roles))
                    else:
                        child.set("role", ";".join(prev_roles))
                collector.append(child)
            elif child.get("element") == "list":
                solve_list(child, collector, prev_roles=prev_roles.copy(), transfer_roles=transfer_roles)

    def get_participants_from_relations(prefix, event, event_id):
        """
        All relations that have an event-spawning element as a source and a prefix "role" (or any other passed prefix) will cause
        the target element to be added as a participant in the event.
        This is a workaround to enable overlapping events even when the work tree system wouldn't allow it.
        """
        matching_relations = out_root.xpath("./relations/relation[@from='{0}' and starts-with(@label, '{1}')]".format(event.get("id"), prefix + "."))
        for relation in matching_relations:
            # get the target element
            target = out_root.find(f"./spans//span[@id='{relation.get('to')}']")
            role = relation.get("label").split(".")[1]
            yield (target, {"id": event_id, "role": role})

    # move all roles from list elements to their children
    for list_elem in out_root.xpath("./spans//span[@element='list' and not(parent::span[@element='list'])]"):
        solve_list(list_elem, [], [], transfer_roles=True)

    # collect all elements with roles so we can later detect which ones didnt get an event
    elems_with_roles = out_root.xpath("./spans//span[string-length(@role) > 0]")

    events_node = et.SubElement(out_root, "eventGroups")
    
    previously_used_triggers = []

    # eventspan handling
    # TODO: Make this configurable via the config file
    running_ids = 0
    eventspans = out_root.xpath("./spans//span[@element='interaction']")
    for event in eventspans:
        event_id = next(role for role in get_roles(event.get("role"), is_evt=True) if role["role"] == "evt")["id"]  # TODO: as we're not using the role field anymore we can simplify this
        # find a trigger if present
        triggers = event.findall("./span[@element='trigger']")
        event_triggers = []
        for trigger in triggers:
            # only add this trigger if it has no or same event id
            trigger_id = next(role for role in get_roles(trigger.get("role"), is_evt=True) if role["role"] == "evt")["id"]
            if trigger_id == event_id:
                event_triggers.append(trigger)
                # add event type to trigger from eventspan
                trigger.set("class", event.get("class"))
                previously_used_triggers.append(trigger)
        # collect participants
        candidates = []
        for child in event:
            if child in event_triggers:
                continue
            if child.get("element") == "list":
                collector = []
                solve_list(child, collector, [])
                candidates.extend(collector)
            else:
                candidates.append(child)
        # print(event.get("id"), [c.get("id") for c in candidates])
        participants = []
        for candidate in candidates:
            roles = get_roles(candidate.get("role"))
            for role in roles:
                # if no event_id was given, we assume only one event in the span,
                # so all children with roles are part of it.
                if not event_id[0] or role["id"][0] == event_id[0]:
                    participants.append((candidate, role))
        # get participants from role.X relations (this is currently hardcoded)
        participants.extend(get_participants_from_relations("role", event, event_id))

        event_node = et.SubElement(events_node, "eventGroup", 
            {
                "event_id": str(running_ids), 
                "class": event.get("class"),
                "polarity": event.get("polarity"),
                "tense": event.get("tense"),
                "modality": event.get("modality"),
                "start": event.get("start"), 
                "end": event.get("end"), 
                "ref": event.get("id")  # TODO: Consider if this needs to be set to the id of the parent element instead
            })
        running_ids = create_event(event, event_node, event_triggers, participants, running_ids)

    # events based on references
    # self is always participant in the event
    # don't write events if only one entity (self) is present
    reference_spans = out_root.xpath("./spans//span[@element='reference']")
    for event in reference_spans:
        event_id = [""]  # more complex events need to be presented as eventspans in the current system
        head = event.find("./span[@element='head']")
        if head is None:
            continue  # a missing head is an error and needs to be fixed, otherwise the event won't be generated
        # collect participants
        candidates = []
        for child in event:
            if child.get("element") in ["head", "appo", "attr"]:  # TODO: create list in config for all describing spans (or only allow references to be added?)
                continue
            if child.get("element") == "list":
                collector = []
                solve_list(child, collector, [])
                candidates.extend(collector)
            else:
                candidates.append(child)
        participants = [(event, {"id": [""], "role": "source"})]  # TODO: better behaviour needs to be implemented
        for candidate in candidates:
            roles = get_roles(candidate.get("role"))
            for role in roles:
                # if no event_id was given, we assume only one event in the span,
                # so all children with roles are part of it.
                if not event_id[0] or role["id"][0] == event_id[0]:
                    participants.append((candidate, role))
        # get participants from role.X relations (this is currently hardcoded)
        participants.extend(get_participants_from_relations("role", event, event_id))
        if len(participants) == 1:
            # no additional roles found, so look for elements without explicit role assignments
            candidates = []
            for child in event:
                if child.get("element") not in ["list", "reference", "value"]:  # TODO: create list in config which contains all elements like that
                    continue
                if child.get("element") == "list":
                    collector = []
                    solve_list(child, collector, [])
                    candidates.extend(collector)
                else:
                    candidates.append(child)
            participants = [(event, {"id": [""], "role": "source"})]  # TODO: better behaviour needs to be implemented
            for candidate in candidates:
                participants.append((candidate, {"id": [""], "role": "target"}))
            if len(participants) == 1:
                continue
        event_node = et.SubElement(events_node, "eventGroup", 
            {
                "event_id": str(running_ids), 
                "class": head.get("class"), 
                "polarity": event.get("polarity"),
                "tense": event.get("tense"),
                "modality": event.get("modality"),
                "start": event.get("start"), 
                "end": event.get("end"), 
                "ref": event.get("id")
            })
        running_ids = create_event(event, event_node, [head], participants, running_ids)

    
    # events based on appositions
    appo_spans = out_root.xpath("./spans//span[@element='appo']")
    for event in appo_spans:
        event_id = [""]  # more complex events need to be presented as eventspans in the current system
        head = event.find("./span[@element='head']")
        if head is None:
            continue  # a missing head is an error and needs to be fixed, otherwise the event won't be generated
        #print(et.tostring(event))
        parent = event.xpath("ancestor::span[@element='reference' or @element='list'][1]")[0]
        if parent.get("element") == "reference":
            references = [parent]
        else:
            references = parent.findall("span[@element='reference']")

        # collect participants
        candidates = []
        for child in event:
            if child.get("element") in ["head", "appo", "attr"]:  # TODO: create list in config for all describing spans (or only allow references to be added?)
                continue
            if child.get("element") == "list":
                collector = []
                solve_list(child, collector, [])
                candidates.extend(collector)
            else:
                candidates.append(child)
        
        for reference in references:
            participants = [(reference, {"id": [""], "role": "source"})]  # TODO: better behaviour needs to be implemented
            for candidate in candidates:
                roles = get_roles(candidate.get("role"))
                for role in roles:
                    # if no event_id was given, we assume only one event in the span,
                    # so all children with roles are part of it.
                    if not event_id[0] or role["id"][0] == event_id[0]:
                        participants.append((candidate, role))
            # get participants from role.X relations (this is currently hardcoded)
            participants.extend(get_participants_from_relations("role", event, event_id))
            if len(participants) == 1:
                # no additional roles found, so look for elements without explicit role assignments
                candidates = []
                for child in event:
                    if child.get("element") not in ["list", "reference", "value"]:  # TODO: create list in config which contains all elements like that
                        continue
                    if child.get("element") == "list":
                        collector = []
                        solve_list(child, collector, [])
                        candidates.extend(collector)
                    else:
                        candidates.append(child)
                participants = [(reference, {"id": [""], "role": "source"})]  # TODO: better behaviour needs to be implemented
                for candidate in candidates:
                    participants.append((candidate, {"id": [""], "role": "target"}))
                if len(participants) == 1:
                    continue
            event_node = et.SubElement(events_node, "eventGroup", 
                {
                    "event_id": str(running_ids), 
                    "class": head.get("class"), 
                    "polarity": event.get("polarity"),
                    "tense": event.get("tense"),
                    "modality": event.get("modality"),
                    "start": event.get("start"), 
                    "end": event.get("end"), 
                    "ref": event.get("id")
                })
            running_ids = create_event(event, event_node, [head], participants, running_ids)


    # events based on attributes
    # NOTE: parent references of attributes can be explicitly annotated with a role by putting that role info as part of the attribute (e.g. label="attr.sale" role="property")
    attr_spans = out_root.xpath("./spans//span[@element='attr']")
    for event in attr_spans:
        event_id = [""]  # more complex events need to be presented as eventspans in the current system
        triggers = event.findall("./span[@element='trigger']")
        event_triggers = []
        for trigger in triggers:
            # only add this trigger if it has no event id (TODO: this behaviour needs some improvement, e.g. any trigger can be used to be part of the attribute event)
            trigger_id = next(role for role in get_roles(trigger.get("role"), is_evt=True) if role["role"] == "evt")["id"]
            if trigger_id == [""]:
                event_triggers.append(trigger)
                trigger.set("class", event.get("class"))
                previously_used_triggers.append(trigger)
        if triggers != event_triggers:
            # if some triggers were not added, it means they had an event id, and we better let the triggers handle the 
            # event instead of the attribute
            if len(event_triggers) > 0:
                print("ERROR: Multiple triggers, some without ids, were found in a single Attribute span. See ID {0}.".format(event.get("id")))
            continue
        parent = event.xpath("ancestor::span[@element='reference' or @element='list'][1]")[0]
        if parent.get("element") == "reference":
            references = [parent]
        else:
            references = parent.findall("span[@element='reference']")
        # collect participants
        candidates = []
        for child in event:
            if child in event_triggers:
                continue
            if child.get("element") == "list":
                collector = []
                solve_list(child, collector, [])
                candidates.extend(collector)
            else:
                candidates.append(child)
        for reference in references:
            participants = [(reference, {"id": [""], "role": "source"})]
            for candidate in candidates:
                roles = get_roles(candidate.get("role"))
                for role in roles:
                    # if no event_id was given, we assume only one event in the span,
                    # so all children with roles are part of it.
                    if not event_id[0] or role["id"][0] == event_id[0]:
                        participants.append((candidate, role))
            # get participants from role.X relations (this is currently hardcoded)
            participants.extend(get_participants_from_relations("role", event, event_id))
            if len(participants) == 1:
                # no additional roles found, so look for elements without explicit role assignments
                candidates = []
                for child in event:
                    if child in event_triggers:
                        continue
                    if child.get("element") == "list":
                        collector = []
                        solve_list(child, collector, [])
                        candidates.extend(collector)
                    else:
                        candidates.append(child)
                participants = [(reference, {"id": [""], "role": "source"})]
                for candidate in candidates:
                    participants.append((candidate, {"id": [""], "role": "target"}))
                if len(participants) == 1:
                    continue
            event_node = et.SubElement(events_node, "eventGroup", 
                {
                    "event_id": str(running_ids), 
                    "class": event.get("class"), 
                    "polarity": event.get("polarity"),
                    "tense": event.get("tense"),
                    "modality": event.get("modality"),
                    "start": event.get("start"), 
                    "end": event.get("end"), 
                    "ref": event.get("id")
                })
            running_ids = create_event(event, event_node, event_triggers, participants, running_ids)

    # event based on trigger handling
    trigger_spans = out_root.xpath("./spans//span[@element='trigger']")
    for trigger in trigger_spans:
        # make sure that you don't belong to an event span
        if trigger in previously_used_triggers:
            continue
        trigger_id = next(role for role in get_roles(trigger.get("role"), is_evt=True) if role["role"] == "evt")["id"]
        # find parent span
        parent = trigger.getparent()
        # collect participants
        candidates = []
        for child in parent:
            if child == trigger:
                continue
            if child.get("element") == "list":
                collector = []
                solve_list(child, collector, [])
                candidates.extend(collector)
            else:
                candidates.append(child)
        participants = []
        for candidate in candidates:
            roles = get_roles(candidate.get("role"))
            for role in roles:
                # if no event_id was given, we assume only one event in the span,
                # so all children with roles are part of it.
                if not trigger_id[0] or role["id"][0] == trigger_id[0]:
                    participants.append((candidate, role))
        # get participants from role.X relations (this is currently hardcoded)
        participants.extend(get_participants_from_relations("role", trigger, trigger_id))
        event_node = et.SubElement(events_node, "eventGroup", 
            {
                "event_id": str(running_ids), 
                "class": trigger.get("class"), 
                "polarity": trigger.get("polarity"),
                "tense": trigger.get("tense"),
                "modality": trigger.get("modality"),
                "start": min(min(participants, key=lambda x: int(x[0].get("start")))[0].get("start"), trigger.get("start")) if participants else trigger.get("start"), 
                "end": max(max(participants, key=lambda x: int(x[0].get("end")))[0].get("end"), trigger.get("end")) if participants else trigger.get("end"),
                "ref": parent.get("id") if parent.tag == "span" else "" # point to anchor element
            })
        running_ids = create_event(trigger, event_node, [trigger], participants, running_ids)

    # events based on relations
    relations = out_root.findall("./relations/relation")
    for relation in relations:
        # corefs should be processed separately
        if relation.get("label").split(".")[0] in ["coref", "role"]:  # TODO: define this in CONFIG instead of hardcoding
            continue

        # If one of the arrows points to a list, add each child as participant instead of the list
        source = out_root.find(f"./spans//span[@id='{relation.get('from')}']")
        sources = []
        if source.get("element") == "list":
            collector = []
            solve_list(source, collector, [])
            sources.extend(collector)
        else:
            sources.append(source)
        
        target = out_root.find(f"./spans//span[@id='{relation.get('to')}']")
        targets = []
        if target.get("element") == "list":
            collector = []
            solve_list(target, collector, [])
            targets.extend(collector)
        else:
            targets.append(target)

        for source in sources:
            for target in targets:
                participants = [
                    (
                        source,
                        {"id": [""], "role": "source"}
                    ),
                    (
                        target,
                        {"id": [""], "role": "target"}
                    )
                ]
                event_node = et.SubElement(events_node, "eventGroup", 
                    {
                        "event_id": str(running_ids), 
                        "class": relation.get("class"),
                        "polarity": relation.get("polarity"),
                        "tense": relation.get("tense"),
                        "modality": relation.get("modality"),
                    })
                running_ids = create_event(relation, event_node, [], participants, running_ids)

    # fit all event span start and ends
    already_processed = []
    for event in events_node:
        try:
            update_eventspan_length(event, events_node, already_processed)
        except RecursionError:
            print(f"ERROR: During event postprocessing, a recursion error occured while the event with id {event.get('event_id')} was processed. This should not be happening and is indicating an error in the code.")

    # check if all roles were assigned to events. Throw error if they weren't assigned
    for role_elem in elems_with_roles:
        if role_elem.get("element") == "list":
            continue
        if "trigger" in role_elem.get("role"):
            continue
        if role_elem.get('role').isnumeric():  # evt id
            continue
        print(f"ERROR: The span {role_elem.get('id')} with a role annotation {role_elem.get('role')} couldn't be matched to an event.")


def write_coref(out_root):
    """
    Write the coreference information to the output XML tree.
    corefs are usually annotated as relations with the coref-label.
    :param out_root: The root element of the output XML tree.

    NOTE: I'm not sure how we want to handle this currently.
    One way would be to simply write an entity registry where we 
    aggregate all information about each noted entity with all its
    mentions by using the coref information.
    Simply writing corefs again would duplicate the information in
    the relations node without adding much to it.
    """
    pass


def apply_special_operations_before_processing(out_root):
    """
    This can be used to apply special operations of any kind on the xml tree before it gets postprocessed. 
    Operations such as systematic replacement of certain tags or replacement of specific tags can be implemented here.
    Mind you, this is after the work tree has been built, so make sure you're looking for the right attributes.

    :param out_root: The root element of the output XML tree.
    """
    return


def apply_special_operations_between_processing(out_root):
    # NOTE: Probably should move all this to a regular step instead of making a special function
    merge = {
        # put here any classes you want to rename (key=old, value=new)
        # you can also do this in renaming.py so it may be a bit redundant
    }
    for span in out_root.findall("./spans//span"):
        span_class = span.get("class")
        if span_class is None:
            continue
        # merge or rename classes of nodes
        if span_class in merge:
            span_class = merge[span_class]

        # split classes and subclasses
        span_class = span_class.split("_")
        if len(span_class) > 1:
            span.set("class", span_class[0])
            span.set("subclass", span_class[1])
        else:
            span.set("class", span_class[0])
            span.set("subclass", "")


def apply_special_operations_after_processing(out_root):
    """
    event postprocessing goes here as well currently.
    """
    def do_special_operations(event_group, event_config):
        for special_operation in event_config.get("special_operations", []):
            # perform special actions
            if special_operation == "check_if_payment_or_obligation":
                # if a date is present, it's a payment. otherwise, it's an obligation. (payments may contain obligation information!)
                event = event_group.find("event")
                if event is None:
                    continue
                date = event.find("role[@role='date']")
                if date is None:
                    due_oblig_config = next((d for d in CONFIG["event_postprocessing"] if d.get('name') == 'due-obligation'), None)
                    event_group.set("class", "due-obligation")
                    event_config = due_oblig_config
                    do_special_operations(event_group, event_config)
            elif special_operation == "include_due_roles":
                # add all roles from due_obligations to the event config
                due_oblig_config = next((d for d in CONFIG["event_postprocessing"] if d.get('name') == 'due-obligation'), None)
                event_config["main_classes"] += due_oblig_config["main_classes"]
                if "other_classes" in event_config:
                    event_config["other_classes"] += due_oblig_config["other_classes"]
                else:
                    event_config["other_classes"] = due_oblig_config["other_classes"]
            else:
                print(f"EVENT POSTPROCESSING ERROR: No matching instruction found for special operation '{special_operation}' while processing event {event_class}")

        return event_config  # return it in case it changed


    # iterate all event groups and look them up in our event list
    event_groups = out_root.find("eventGroups").findall("eventGroup")
    for event_group in event_groups:
        event_class = event_group.get("class").replace("_", "-")
        for event_config in CONFIG["event_postprocessing"]:
            if event_config["name"] == event_class:
                break
            if event_class in event_config.get("alternative_names", []):
                # rename the event group if it has an alternative name
                event_group.set("class", event_config["name"])
                break
        else:
            print(f"EVENT POSTPROCESSING WARNING: No event config could be found for event {event_class}!")

        event_config = do_special_operations(event_group, event_config)

        # add type if it is an event or a state
        event_group.set("type", event_config["type"])

        if event_config["name"] == "other":
            # end here as other can contain any roles with no checks whatsoever
            continue
    
        for event in event_group.findall("event"):
            # 1. iterate all roles and
            for role in event:
                role_class = role.get("role").replace("_", "-")
                if role_class == "detail":
                    role.set("role", "detail_other")
                    continue
                for role_config in event_config["main_classes"] + CONFIG["event_generic_roles"]:
                    if role_config["name"] == role_class:
                        role.set("role", role_class)
                        break
                    if role_class in role_config.get("alternative_names", []):
                        # a) if they have an alternative name, give it the proper name
                        role.set("role", role_config["name"])
                        break
                else:
                    role_class = role_class.replace("detail-", "")
                    role_class = role_class.replace("detail_", "")
                    for role_config in event_config.get("other_classes", []):
                        if role_config["name"] == role_class:
                            role.set("role", "detail_" + role_config["name"])
                            break
                        if role_class in role_config.get("alternative_names", []):
                            # a) if they have an alternative name, give it the proper name
                            role.set("role", "detail_" + role_config["name"])
                            break
                    else:
                        print(f"EVENT POSTPROCESSING WARNING: No role config could be found for role {role_class} in event {event_class}!")
                # b) check if the entity class is allowed for that role
                cfg_classes = role_config.get("classes", [])
                allowed_classes = []
                for cls in cfg_classes:
                    if cls in CONFIG["event_processing_entity_class_groupings"]:
                        allowed_classes.extend(CONFIG["event_processing_entity_class_groupings"][cls])
                    else:
                        allowed_classes.append(cls)
                if not allowed_classes:
                    continue  # if no allowed classes are specified all are allowed
                role_entity_class = role.get("ref_class")
                ref = role.get("ref")
                ref_elem = out_root.find("spans").find(f".//span[@id='{ref}']").get("element")
                if role_entity_class in ["unc", "unk", "other"]:  # other should be restricted to only actual "other" entities, not for modifiers as well
                    pass
                elif role_entity_class in allowed_classes:
                    pass  # all good
                elif "#mod" in allowed_classes and ref_elem in ["mod"]:
                    pass
                elif "#other" in allowed_classes and ref_elem == "other":
                    pass  # all good
                elif "#event" in allowed_classes and ref_elem in ["trigger", "eventspan"]:
                    pass  # all good
                else:
                    print("EVENT POSTPROCESSING WARNING: role entity class '{}' is not allowed by config for role '{}' in event '{}'.".format(role_entity_class, role_config["name"], event_config["name"]))

                    
def cleanup(out_root):
    """
    Remove unwanted elements, attributes, etc.
    """
    # check all ref-Attributes and make sure elements with those ids exist
    spans = out_root.find("spans")
    for elem in out_root.xpath("./relations//* | ./eventGroups//*"):
        for attr in ["ref", "from", "to"]:
            if elem.get(attr) is not None and elem.get(attr):
                ref_id = elem.get(attr)
                ref_span = spans.find(f".//span[@id='{ref_id}']")
                if ref_span is None:
                    if attr in ["from", "to"]:
                        # this was a manual change where an element was deleted and we forgot to remove the coref as well
                        if elem.getparent() is not None:
                            elem.getparent().remove(elem)
                    else:
                        print(f"WARNING: Element with id '{ref_id}' referenced in {elem.tag} does not exist in the spans section.")
                        print(et.tostring(elem))
    
    # remove span attributes
    for span in spans.findall(".//span"):
        for attr in CONFIG["span_attributes_to_remove"]:
            span.attrib.pop(attr, None)
    
    # remove relation attributes
    for relation in out_root.find("relations").findall("relation"):
        for attr in CONFIG["relation_attributes_to_remove"]:
            relation.attrib.pop(attr, None)

    # remove the ref_class helper attribute
    for role in out_root.xpath("./eventGroups/eventGroup/event/role"):
        role.attrib.pop("ref_class", None)

        
def process(in_root, outname):
    """
    Process the XMI file and write the output to a new file.
    :param in_root: The root element of the input XML tree.
    :param outname: The name of the output file.
    """
    # for debugging
    #print(et.tostring(in_root, encoding='unicode', pretty_print=True))

    text_node = in_root.find("./cas:Sofa", namespaces={"cas":"http:///uima/cas.ecore"})
    document_text = text_node.get("sofaString")

    out_root = et.Element("doc", nsmap={None: "https://dhbern.github.io/BeNASch/ns"})
    out_text = et.SubElement(out_root, "text")
    start_index_dict, end_index_dict = write_text(out_text, document_text, in_root)

    create_work_tree(in_root, out_root, document_text, start_index_dict, end_index_dict)

    apply_special_operations_before_processing(out_root)

    process_spans(out_root)
    process_relations(out_root)

    apply_special_operations_between_processing(out_root)

    write_events(out_root)
    write_coref(out_root)

    apply_special_operations_after_processing(out_root)

    cleanup(out_root)

    # write debug info
    print(f"See processed file at {os.path.abspath(os.path.join(OUTFOLDER, os.path.basename(outname)))}")

    # write xml
    out_tree = et.ElementTree(out_root)
    pathlib.Path(OUTFOLDER).mkdir(parents=True, exist_ok=True) 
    out_tree.write(os.path.join(OUTFOLDER, os.path.basename(outname)), xml_declaration=True, pretty_print=True, encoding="utf8")
    
    #print(et.tostring(out_root, encoding='unicode', pretty_print=True))
    

def process_xmi(infile):
    in_root = et.parse(infile).getroot()

    at_least_one_span = in_root.find(f"./custom:{SPAN_LAYER}", namespaces={"custom":"http:///custom.ecore"})
    if at_least_one_span is None:
        # stop processing if document doesn't contain annotations
        return

    print("="*80)
    print(f"Processing {os.path.abspath(infile)}.")

    outname = os.path.splitext(infile)[0] + ".benasch.xml"

    process(in_root, outname)


if __name__ == "__main__":
    # implement a test case with a single file
    import zipfile
    path = "./data/hgb_2025_04_03/exports/hgb_21113301359897783216/annotation/HGB_Exp_12_199_HGB_1_229_037_015.txt/admin.zip"
    archive = zipfile.ZipFile(path, 'r')
    xmi = archive.read("admin.xmi")
    process_xmi(xmi)
    