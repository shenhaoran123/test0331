#include "visual.hpp"

void visual::printPtxGraph2Dot(const Graph& graph, string outFile) {
    Set<Int> nodeIDs;
    for(Int i = 0; i < graph.getNodeCnt(); i++) nodeIDs.insert(i);

    printPtxGraph2Dot(graph, outFile, nodeIDs); 
}

 void visual::printPtxGraph2Dot(const Graph& graph, string outFile, const Set<Int>& nodeIDs) {
    std::ofstream ofs(outFile);
    if(!ofs.is_open()) {
        util::showError("Can not open " + outFile);
        return ;
    }

    ofs << "# ShadowGhostH & Bunny" << std::endl;

    ofs << "digraph ptxGraph{" << std::endl;

    printNodeInfo(ofs, graph, nodeIDs);
    printEdgeInfo(ofs, graph, nodeIDs);

    ofs << "}" << endl;
    ofs.close();
 }


void visual::printNodeInfo(std::ofstream& ofs, const Graph& graph, const Set<Int>& nodeIDs) {
    // const vector<bool>& usedInstrs = graph.getUsedInstrs();
    const vector<Node*>& instrNodes = graph.getInstrNodes();

    for(Int i = 0; i < instrNodes.size(); i++) {
        if(nodeIDs.find(i) == nodeIDs.end()) continue;
        const Node* curNode = instrNodes.at(i);
        Int    instrID   = curNode->getInstrID();
        string desReg    = curNode->getDesReg();
        string instrType = curNode->getInstrType();
        InstrClass instrClass = curNode->getInstrClass();

        if(!graph.haveNeighborInstrID(instrID)) continue;
        if(instrClass == InstrClass::LABEL || instrClass == InstrClass::NJUMP) continue;

        if(instrType.find(".") != string::npos) instrType = instrType.substr(0, instrType.find("."));

        ofs << "\t\"" << i << "\"[label=\"" << instrID << "." << instrType << "\"]";
        
        if(instrClass == InstrClass::ST || instrClass == InstrClass::LD)
            ofs << "[color=\"red\"]";
        else if(instrClass == InstrClass::JUMP)
            ofs << "[color=\"blue\"]";
        ofs << endl;
    }
}


void visual::printEdgeInfo(std::ofstream& ofs, const Graph& graph, const Set<Int>& nodeIDs) {
    const vector<Node*>&             instrNodes = graph.getInstrNodes();
    const vector<vector<Int> >&      graphTable = graph.getGraphTable();
    const vector<vector<Int> >&      edgeTimes  = graph.getEdgeTimes();
    const vector<vector<EdgeType> >& edgeTypes  = graph.getEdgeTypes();

    for(Int i = 0; i < instrNodes.size(); i++) {
        if(nodeIDs.find(i) == nodeIDs.end()) continue;
        for(Int j = 0; j < instrNodes.size(); j++) {
            if(nodeIDs.find(j) == nodeIDs.end()) continue;
            if(graphTable.at(i).at(j) == 1) {
                ofs << "\t\"" << i << "\"->\"" << j << "\"";
                if(edgeTypes.at(i).at(j) == EdgeType::ADD) ofs << "[color=\"red\"]";
                else if(edgeTypes.at(i).at(j) == EdgeType::JUMP) {
                    ofs << "[color=\"blue\"]";
                    // ofs << "[label=\"" << edgeTimes.at(i).at(j) << "\"]";
                }
                ofs << "[label=\"" << edgeTimes.at(i).at(j) << "\"]";
                ofs << endl;
            }
        }
    }
}