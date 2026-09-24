"""Optional SBArchOpt graph decoder for DSG optimization problems."""

from __future__ import annotations

from typing import Dict, Protocol, Sequence, Tuple

import networkx as nx
import numpy as np

from adsg_core.graph.adsg import DSGType
from adsg_core.graph.adsg_nodes import DesignVariableNode
from adsg_core.graph.graph_edges import get_edge_type
from adsg_core.graph.labeling import constant_label, dsg_type_label, node_type_label
from adsg_core.optimization.graph_processor import GraphProcessor

try:
    from sb_arch_opt.algo.arch_sbo.graph import (
        GraphRepresentation,
        NodeLabeling,
        SizingFeature,
    )

    HAS_SB_ARCH_OPT_GRAPH = True
except ImportError:
    HAS_SB_ARCH_OPT_GRAPH = False


__all__ = [
    "HAS_SB_ARCH_OPT_GRAPH",
    "DSGSizingEncoder",
    "DesignVariableSizingEncoder",
    "DSGGraphDecoder",
    "get_default_dsg_labelings",
]


def _check_dependency():
    if not HAS_SB_ARCH_OPT_GRAPH:
        raise ImportError("SBArchOpt graph support is not installed")


def get_default_dsg_labelings():
    _check_dependency()
    return (
        NodeLabeling("adsg_core.constant", constant_label),
        NodeLabeling("adsg_core.dsg", dsg_type_label),
        NodeLabeling("adsg_core.type", node_type_label),
    )


class DSGSizingEncoder(Protocol):

    @property
    def features(self) -> Sequence["SizingFeature"]:
        ...

    def encode(self, graph: DSGType, x_imputed: Sequence[float]) -> np.ndarray:
        ...


class DesignVariableSizingEncoder:
    """Export additional DesignVariableNode values as normalized sizing features."""

    def __init__(self, processor: GraphProcessor):
        self._variables = tuple(
            (index, variable)
            for index, variable in enumerate(processor.des_vars)
            if isinstance(variable.node, DesignVariableNode)
        )
        _check_dependency()
        self._features = tuple(
            SizingFeature(
                variable.name,
                "numeric" if not variable.is_discrete or variable.is_ordinal else "categorical",
            )
            for _, variable in self._variables
        )

    @property
    def features(self):
        return self._features

    def encode(self, graph, x_imputed):
        del graph
        return np.asarray(
            [self._normalize(x_imputed[index], variable) for index, variable in self._variables],
            dtype=float,
        )

    @staticmethod
    def _normalize(value, variable):
        if not variable.is_discrete:
            lower, upper = variable.bounds
            return (float(value) - lower) / (upper - lower)
        if variable.is_ordinal:
            return 0.0 if variable.n_opts == 1 else float(value) / (variable.n_opts - 1)
        return float(value)


class DSGGraphDecoder:
    """Decode design vectors into neutral SBArchOpt graph representations."""

    def __init__(
        self,
        processor: GraphProcessor,
        labelings=None,
        sizing_encoders: Sequence[DSGSizingEncoder] = None,
    ):
        _check_dependency()
        self.processor = processor
        self._labelings = tuple(
            labelings if labelings is not None else get_default_dsg_labelings()
        )
        self.sizing_encoders = tuple(
            sizing_encoders
            if sizing_encoders is not None
            else (DesignVariableSizingEncoder(processor),)
        )
        self._raw_to_corrected: Dict[Tuple[float, ...], Tuple[float, ...]] = {}
        self._representations: Dict[Tuple[float, ...], "GraphRepresentation"] = {}

    def __deepcopy__(self, memo):
        copied = self.__class__.__new__(self.__class__)
        memo[id(self)] = copied
        copied.__dict__ = self.__dict__.copy()
        return copied

    @property
    def labelings(self):
        return self._labelings

    @property
    def sizing_features(self):
        return tuple(
            feature
            for encoder in self.sizing_encoders
            for feature in encoder.features
        )

    def decode(self, x: np.ndarray):
        representations = []
        for row in np.asarray(x):
            raw_key = tuple(np.asarray(row, dtype=float))
            corrected_key = self._raw_to_corrected.get(raw_key)
            graph = None
            if corrected_key is None:
                graph, x_imputed, _ = self.processor.get_graph(row, create=False)
                corrected_key = tuple(x_imputed)
                self._raw_to_corrected[raw_key] = corrected_key

            representation = self._representations.get(corrected_key)
            if representation is None:
                if graph is None:
                    graph, _, _ = self.processor.get_graph(corrected_key)
                representation = self._representation(graph, corrected_key)
                self._representations[corrected_key] = representation
            representations.append(representation)
        return representations

    def _representation(self, dsg: DSGType, x_imputed):
        source_graph = dsg.graph
        source_nodes = tuple(source_graph.nodes)
        node_ids = {node: index for index, node in enumerate(source_nodes)}

        graph = nx.MultiDiGraph()
        graph.add_nodes_from(node_ids.values())
        for source, target, key, data in source_graph.edges(keys=True, data=True):
            graph.add_edge(
                node_ids[source],
                node_ids[target],
                kind=get_edge_type((source, target, key, data)).name.lower(),
            )

        node_labels = {
            labeling: {
                node_ids[node]: labeling(node)
                for node in source_nodes
            }
            for labeling in self.labelings
        }
        sizing_values = np.concatenate([
            encoder.encode(dsg, x_imputed)
            for encoder in self.sizing_encoders
        ]) if self.sizing_encoders else np.empty((0,), dtype=float)

        return GraphRepresentation(
            graph=graph,
            node_labels=node_labels,
            sizing_values=sizing_values,
        )
