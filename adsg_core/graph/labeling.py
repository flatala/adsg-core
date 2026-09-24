"""Generic node labelings for design-space graphs."""

from adsg_core.graph.adsg_nodes import (
    ChoiceNode,
    CollectorNode,
    ConnectionChoiceNode,
    ConnectorDegreeGroupingNode,
    ConnectorNode,
    DesignVariableNode,
    MetricNode,
    NamedNode,
    NonSelectionNode,
    SelectionChoiceNode,
)


__all__ = ["constant_label", "dsg_type_label", "node_type_label"]


def constant_label(_node):
    return "node"


def dsg_type_label(node):
    """Label a node by its most specific generic DSG role."""
    if isinstance(node, SelectionChoiceNode):
        return "selection_choice"
    if isinstance(node, ConnectionChoiceNode):
        return "connection_choice"
    if isinstance(node, ChoiceNode):
        return "choice"
    if isinstance(node, DesignVariableNode):
        return "design_variable"
    if isinstance(node, MetricNode):
        return "metric"
    if isinstance(node, ConnectorDegreeGroupingNode):
        return "connector_group"
    if isinstance(node, ConnectorNode):
        return "connector"
    if isinstance(node, CollectorNode):
        return "collector"
    if isinstance(node, NonSelectionNode):
        return "non_selection"
    if isinstance(node, NamedNode):
        return "named_node"
    return "node"


def node_type_label(node):
    """Label a node by its concrete class without exporting the class object."""
    node_type = type(node)
    return node_type.__module__, node_type.__qualname__
