from adsg_core.graph.adsg_nodes import (
    ConnectorNode,
    DesignVariableNode,
    NamedNode,
    SelectionChoiceNode,
)
from adsg_core.graph.labeling import constant_label, dsg_type_label, node_type_label


def test_generic_node_labelings():
    nodes_and_roles = [
        (NamedNode("node"), "named_node"),
        (ConnectorNode("port"), "connector"),
        (SelectionChoiceNode("choice"), "selection_choice"),
        (DesignVariableNode("size", bounds=(0.0, 1.0)), "design_variable"),
    ]

    for node, role in nodes_and_roles:
        assert constant_label(node) == "node"
        assert dsg_type_label(node) == role
        assert node_type_label(node) == (type(node).__module__, type(node).__qualname__)
