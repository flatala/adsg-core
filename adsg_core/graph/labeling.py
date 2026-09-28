"""
MIT License

Copyright: (c) 2026, Deutsches Zentrum fuer Luft- und Raumfahrt e.V.
Contact: jasper.bussemaker@dlr.de

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

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


__all__ = ["constant_label", "dsg_type_label"]


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
