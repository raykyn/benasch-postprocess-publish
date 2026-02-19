"""
Conversion script to transform standard XML (may 2025) to a column format with training data.
column 1 is always the text, the other columns can be defined.
"""

from lxml import etree as et


DEFAULT_NAMESPACE = "https://dhbern.github.io/BeNASch/ns"


def delve_into_children(node, valid_set, collector):
    for child in node:
        for valid_node, instr in valid_set:
            if child is valid_node:
                if child not in collector:
                    collector.append((child, instr))
                break
        else:
            delve_into_children(child, valid_set, collector)


def apply_tag_conversion(node, conversion_instructions):
    out = []
    for elem in conversion_instructions:
        if elem.startswith("^"):
            node = node.getparent()
            elem = elem[1:]
        if elem.startswith("@"):
            attr = node.get(elem[1:])
            attr = PROCESSING_CONFIG.get("rename_labels", {}).get(attr, attr)
            if attr is None:
                out.append("")
            else:
                out.append(attr)
        else:
            out.append(elem)
    return "".join(out)


def create_idx_dict(node_list):
    idx_dict = {}
    tagset = set()
    for node, instr in node_list:
        start = int(node.get("start"))
        end = int(node.get("end")) + 1
        for i in range(start, end):
            prefix = "B-" if i == start else "I-"
            tag = prefix + apply_tag_conversion(node, instr)
            tagset.add(tag)
            idx_dict[i] = tag
    return idx_dict, tagset


def add_base_labels(rows: list, elem, label_setting):
    """
    This puts a label at start and end
    of the text and fills all other columns
    with O.
    The label is given in the definition of the base.
    label_setting can be a list or a single string
    """
    if type(label_setting) is str:
        label_setting = [label_setting]
    label = []
    for ls in label_setting:
        if ls.startswith("^"):
            elem = elem.getparent()
            ls = ls[1:]
        if ls.startswith("@"):
            ls = elem.get(ls[1:])
        label.append(ls)
    label = "-".join(label)
    col_count = len(rows[0]) - 1
    rows.insert(0, ["[B-" + label.upper() + "]"] + ["O"]*col_count)
    rows.append(["[E-" + label.upper() + "]"] + ["O"]*col_count)


def process_document(docpath, config=None):
    if config is None:
        config = PROCESSING_CONFIG

    root = et.parse(docpath).getroot()
    spans = root.find("./b:spans", namespaces={"b": DEFAULT_NAMESPACE})
    tokens = root.findall("./b:text//b:token", namespaces={"b": DEFAULT_NAMESPACE})  # TODO: Enable processing of line elements and implement them as linebreaks

    out_text = []

    tagset = set()

    for base in config["base"]:
        nodes = spans.xpath(base["xpath"], namespaces={"b": DEFAULT_NAMESPACE})
        for node in nodes:
            if base["xpath"] == ".":
                start = 0
                end = len(tokens)
                incl_tokens = [t.text for t in tokens]
            else:
                start = int(node.get("start"))
                end = int(node.get("end"))+1
                incl_tokens = [t.text for t in tokens[start:end]]
            new_columns = []
            for column in config["columns"]:
                valid_nodes = []
                for c in column:
                    valid_nodes.extend([(x, c["tag"]) for x in node.xpath(c["xpath"], namespaces={"b": DEFAULT_NAMESPACE})])
                chosen_nodes = []
                delve_into_children(node, valid_nodes, chosen_nodes)
                chosen_nodes_dict, tags = create_idx_dict(chosen_nodes)
                tagset.update(tags)
                new_column = [chosen_nodes_dict[i] if i in chosen_nodes_dict else "O" for i in range(start, end)]
                new_columns.append(new_column)
            columns = [incl_tokens] + new_columns
            rows = list(zip(*columns))

            if "label" in base:
                add_base_labels(rows, node, base["label"])
            
            for row in rows:
                out_text.append("\t".join(row))
            out_text.append("")
    return "\n".join(out_text), tagset


# PREFIX ALL ELEMENTS WITH B: FOR THE NAMESPACE
PROCESSING_CONFIG = {
    # in the first part, we define which elements the texts are based on
    # "." indicates the whole text
    "base": [
        {"xpath": ".", "label": "DOC"},
        {"xpath": ".//b:span[not(@element='head' or @element='value' or @element='trigger' or @element='mod')]", "label": ["@element", "@class"]},
        {"xpath": ".//b:span[@element='mod'][count(*) > 0]", "label": ["@element", "@class"]}
    ],
    # in the second part, we define which annotations are written for training
    # if multiple layers would fit the xpath, only the most immediate one is used
    "columns": [
        [
            # multiple xpaths can be defined with different tag conversion instructions
            # mind you, if a node fits multiple xpaths, only the first one is used
            {"xpath": ".//b:span", "tag": ["@element", ".", "@class"]}
            #{"xpath": ".//span[@element='head']", "tag": ["@element", ".", "@class"]}
            #{"xpath": ".//b:span[@element='reference']", "tag": ["@class"]}
        ]
    ],
    "rename_labels": {
        #"fac": "loc",
        #"gpe-org": "org",
        #"gpe-loc": "loc",
        #"gpe": "loc",
        #"other": "misc",
        #"nam": "loc"
    }
}

if __name__ == "__main__":
    columns, tagset = process_document("./data/example_hgb/processed/test_evt_ids.benasch.xml")
    print(columns)
    print(tagset)
    #write_document("text.tsv", textnode)