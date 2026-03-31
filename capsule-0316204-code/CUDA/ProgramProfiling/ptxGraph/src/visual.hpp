#pragma once

#include "graph.hpp"

namespace visual {
    void printPtxGraph2Dot(const Graph& graph, string outFile);
    void printPtxGraph2Dot(const Graph& graph, string outFile, const Set<Int>& nodeIDs);

    void printNodeInfo(std::ofstream& ofs, const Graph& graph, const Set<Int>& nodeIDs);
    void printEdgeInfo(std::ofstream& ofs, const Graph& graph, const Set<Int>& nodeIDs);
}