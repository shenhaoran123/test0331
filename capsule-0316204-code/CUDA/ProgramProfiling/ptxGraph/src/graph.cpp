#include "graph.hpp"
//test  by bunny

/* class Node *****************************************************************/
Int Node::getInstrID() const { 
    return instrID;
}

string Node::getInstrType() const {
    return instrType;
}

Float Node::getPrSDC() const {
    return prSDC;
}

// Int Node::getOpType() const {
//     return opType;
// }

string Node::getDesReg() const {
    return desReg;
}

InstrClass Node::getInstrClass() const {
    return instrClass;
}

const vector<string>& Node::getDepRegs() const {
    return depRegs;
}

void Node::setInstrNodeST(const vector<string>& words, string instr, bool havePrSDC) {
    Int curIndex = 2;
    desReg = words.at(curIndex);
    util::formatReg(desReg);

    if(words.size() != curIndex + 2 + (havePrSDC ? 1 : 0)) util::showWarning("Unexpected ST instr: " + instr);
    if(!util::isReg(desReg) || !util::isAdd(desReg)) util::showWarning("ST instr has wrong arg: " + instr);

    if(util::isReg(words.at(++curIndex))) {
        depRegs.push_back(words.at(curIndex));
        util::formatReg(depRegs.at(0));
    }

    if(havePrSDC) prSDC = std::stod(util::getLstElem(words));
    return;
}

void Node::setInstrNodeLD(const vector<string>& words, string instr, bool havePrSDC) {
    Int curIndex = 2;
    desReg = words.at(curIndex);
    util::formatReg(desReg);
    if(words.size() != curIndex + 2 + (havePrSDC ? 1 : 0)) util::showWarning("Unexpected LD instr: " + instr);
    if(!util::isReg(desReg)) util::showWarning("LD instr has wrong arg: " + instr);
    
    if(util::isReg(words.at(++curIndex))) {
        depRegs.push_back(words.at(curIndex));
        util::formatReg(depRegs.at(0));

        if(!util::isAdd(depRegs.at(0))) util::showWarning("LD instr has wrong arg: " + instr);
    }

    if(havePrSDC) prSDC = std::stod(util::getLstElem(words));
    return;
}

void Node::setInstrNodeUNDO(const vector<string>& words, string instr, bool havePrSDC) {
    // std::cerr << "UNDO instr: " << instr << endl;
    return;
}

void Node::setInstrNodeOTHER(const vector<string>& words, string instr, bool havePrSDC) {
    Int curIndex = 1;
    bool endFlag = false;
    if (words.at(curIndex).find("%") != string::npos) {         // judge for 4-op
        instrType = words.at(curIndex).substr(0, words.at(1).find("%"));
        desReg    = words.at(curIndex).substr(words.at(1).find("%"));
        util::formatReg(desReg);
        ++curIndex;
    } else {                                             // 3 or 2 - op
        instrType = words.at(curIndex);
        desReg    = words.at(++curIndex);
        if(!util::isReg(desReg)) util::showWarning(instr + " have no destination register");
        util::formatReg(desReg);
        ++curIndex;
    }

    for(Int i = curIndex; i < words.size(); i++) {
        string curWord = words.at(i);
        if(endFlag) {
            assert(havePrSDC);
            assert(i == words.size() - 1);
            prSDC = std::stod(words.at(i));
        }
        if(util::getLstElem(curWord) == ';') endFlag = true;

        if(util::isReg(curWord)) {
            util::formatReg(curWord);
            depRegs.push_back(curWord);
        }
    }
}

void Node::setInstrNodeTEX(const vector<string>& words, string instr, bool havePrSDC) {
    Int curIndex = 1;
    if(words.at(curIndex).find("{") == string::npos) curIndex++;
    if(words.at(curIndex).find("{") == string::npos) util::showWarning("Unexpected tex instr desRegs begin: " + instr);

    bool desFlag = true, depFlag = false;
    for(; curIndex < words.size(); curIndex++) {
        if(!desFlag) break;
        string curInstr = words.at(curIndex);
        if(curInstr.find("{") != string::npos) curInstr = curInstr.substr(curInstr.find("{") + 1);
        if(curInstr.find('}') != string::npos) {
            if(words.at(curIndex).substr(words.at(curIndex).size() - 2) != "},") util::showWarning("Unexpected tex instr desRegs end: " + instr);

            curInstr = curInstr.substr(0, curInstr.find("}")) + ',';
            desFlag = false;
        }

        if(util::isReg(curInstr)) {
            desRegs.push_back(curInstr);
            util::formatReg(desRegs.at(desRegs.size() - 1));
        }
         
    }

    if(words.at(curIndex).at(0) != '[') util::showWarning("Unexpected tex instr depRegs begin: " + instr);
    while(words.at(curIndex).find("{") == string::npos && curIndex < words.size()) {
        curIndex++;
        if(curIndex == words.size()) util::showWarning("Unexpected tex instr No depRegs: " + instr);
    }
    depFlag = true;

    for(; curIndex < words.size(); curIndex++) {
        if(!depFlag) break;

        string curInstr = words.at(curIndex);
        if(curInstr.at(0) == '{') curInstr = curInstr.substr(1);
        if(curInstr.find('}') != string::npos) {
            if(words.at(curIndex).substr(words.at(curIndex).size() - 3) != "}];") util::showWarning("Unexpected tex instr depRegs end: " + instr);

            curInstr = curInstr.substr(0, curInstr.size() - 3) + ',';
            depFlag = false;
        }

        if(util::isReg(curInstr)) {
            depRegs.push_back(curInstr);
            util::formatReg(depRegs.at(depRegs.size() - 1));
        }
    }

    if(havePrSDC) prSDC = std::stod(util::getLstElem(words));
}

void Node::printInfo() const {
    cout << instrID << " " << instrType << " " << desReg << " - ";
    for(string reg : depRegs) {
        cout << reg << " ";
    }
    cout << endl;
}

Node::Node() {}

/* class DynamicNode ***********************************************************/
void DynamicNode::setInstrNodeJUMP(const vector<string>& words, string instr, bool havePrSDC) {
    Int curIndex = 1;
    string instrWord = words.at(curIndex);
    if(instrWord.find("%") == string::npos) util::showWarning(instr + " have no register in Jump instr");
    depRegs.push_back(instrWord.substr(instrWord.find("%")));
    // util::formatReg(depRegs.at(depRegs.size() - 1));     Do not need format in JUMP
    // not store other infomation
    return;
}

void DynamicNode::setInstrNode(string instr) {
    std::istringstream inputStringStream(instr);
    vector<string> words;
    std::copy(std::istream_iterator<string>(inputStringStream), std::istream_iterator<string>(), std::back_inserter(words));

    // set instrID
    instrID = std::stoi(words.at(0));
    
    // set instrType & desReg
    string instrWord = words.at(1);
    if(instrWord.find("{")) instrWord = instrWord.substr(0, instrWord.find("{"));
    instrType  = instrWord;
    instrClass = util::judgeInstrDynamic(instrWord);
    
    if(instrClass == InstrClass::UNDO)       setInstrNodeUNDO(words, instr, prSDCFlag);
    else if(instrClass == InstrClass::RET)   setInstrNodeUNDO(words, instr, prSDCFlag);
    else if(instrClass == InstrClass::LD)    setInstrNodeLD(words, instr, prSDCFlag);
    else if(instrClass == InstrClass::ST)    setInstrNodeST(words, instr, prSDCFlag);
    else if(instrClass == InstrClass::JUMP)  setInstrNodeJUMP(words, instr, prSDCFlag);
    else if(instrClass == InstrClass::OTHER) setInstrNodeOTHER(words, instr, prSDCFlag);
    else if(instrClass == InstrClass::TEX)   setInstrNodeTEX(words, instr, prSDCFlag);
    else util::showWarning("Unexpected InstrClass");
}

Float DynamicNode::getOhterThreadInfl() const {
    return otherThreadInfl;
}

void  DynamicNode::setOtherThreadInfl(Float influence) {
    otherThreadInfl = influence;
}

DynamicNode::DynamicNode(){}

DynamicNode::DynamicNode(string instr){
    this->setInstrNode(instr);
}

/* class StaticNode ************************************************************/
void StaticNode::setInstrNodeJUMP(const vector<string>& words, string instr, bool havePrSDC) {
    Int curIndex = 1;
    string instrWord = words.at(curIndex);
    if(instrWord.find("%") == string::npos) util::showWarning(instr + " have no register in Jump instr");
    depRegs.push_back(instrWord.substr(instrWord.find("%")));

    if(words.at(++curIndex) != "bra") util::showWarning("Unexcept Jump instr: " + instr);

    string label = words.at(++curIndex);
    if(util::getLstElem(label) == ';') label = label.substr(0, label.size() - 1);
    nxtLabel.push_back(label);

    if(havePrSDC) prSDC = std::stod(util::getLstElem(words));
    return;
}

void StaticNode::setInstrNodeNJUMP(const vector<string>& words, string instr, bool havePrSDC) {
    Int curIndex = 1;

    string label = words.at(++curIndex);
    if(util::getLstElem(label) == ';') label = label.substr(0, label.size() - 1);
    nxtLabel.push_back(label);
    return;
}

const vector<string>& StaticNode::getNxtLabel() const {
    return nxtLabel;
}

const vector<string>& Node::getDesRegs() const {
    if(instrClass != InstrClass::TEX) util::showWarning("Call getDesRegs beside Tex isntr " + to_string(instrID));
    return desRegs;
}

void StaticNode::setInstrNode(string instr) {
    std::istringstream inputStringStream(instr);
    vector<string> words;
    std::copy(std::istream_iterator<string>(inputStringStream), std::istream_iterator<string>(), std::back_inserter(words));

    // set instrID staticNode need format instr
    instrID = std::stoi(words.at(0));
    
    // set instrType & desReg
    const string& instrWord = words.at(1);
    instrType  = instrWord;
    instrClass = util::judgeInstrStatic(instrWord);

    if(instrClass == InstrClass::UNDO)       setInstrNodeUNDO(words, instr, prSDCFlag);
    else if(instrClass == InstrClass::RET)   setInstrNodeUNDO(words, instr, prSDCFlag);
    else if(instrClass == InstrClass::LD)    setInstrNodeLD(words, instr, prSDCFlag);
    else if(instrClass == InstrClass::ST)    setInstrNodeST(words, instr, prSDCFlag);
    else if(instrClass == InstrClass::JUMP)  setInstrNodeJUMP(words, instr, prSDCFlag);
    else if(instrClass == InstrClass::TEX)   setInstrNodeTEX(words, instr, prSDCFlag);
    else if(instrClass == InstrClass::OTHER) setInstrNodeOTHER(words, instr, prSDCFlag);
    else if(instrClass == InstrClass::NJUMP) setInstrNodeNJUMP(words, instr, prSDCFlag);
    else if(instrClass == InstrClass::LABEL) {if(util::getLstElem(instrType) == ':') instrType = instrType.substr(0, instrType.size() - 1);}
    else {util::showWarning("Unexpected InstrClass");}
}

void StaticNode::printInfo() const {
    cout << instrID << " " << instrType << " ";

    if(instrClass == InstrClass::TEX) {
        for(string reg : desRegs) cout << reg << " ";
    } else cout << desReg;

    cout << " - ";

    for(string reg : depRegs) cout << reg << " ";

    if(!nxtLabel.empty()) {
        cout << "  Jump: ";
        for(string label : nxtLabel) cout << label << " ";
    }
    cout << endl;
}

StaticNode::StaticNode(){}

StaticNode::StaticNode(string instr) {
    this->setInstrNode(instr);
}

/* class Graph *****************************************************************/

// add Node wile genPtxGraph not init !
// void Graph::addNode(string instr) {
//     string desReg = 
//     assert(re)
// }

void Graph::addEdge(Int st, Int ed, EdgeType eType) {
    addEdge(st, ed, eType, 1);
}

void Graph::addEdge(Int st, Int ed, EdgeType eType, Int eTime) {
    // Can change weight of edge
    Int stID = getNodeIDFromInstrID(st);
    Int edID = getNodeIDFromInstrID(ed);

    assert(instrNodes.at(stID)->getInstrID() == st);
    assert(instrNodes.at(edID)->getInstrID() == ed);

    if(edgeTypes.at(stID).at(edID) != EdgeType::NONE && edgeTypes.at(stID).at(edID) != eType) 
        util::showWarning("Add different Edge Type on same edge");

    graphTable.at(stID).at(edID)  = 1;
    edgeTypes .at(stID).at(edID)  = eType;
    edgeTimes .at(stID).at(edID) += eTime;
}

void Graph::addReg(string reg, Int instrID) {
    if(reg2LstInstr.find(reg) != reg2LstInstr.end()) {
        reg2LstInstr.at(reg)  = instrID;
        regRefreshID.at(reg) += 1;
    } else {
        reg2LstInstr.insert(std::make_pair(reg, instrID));
        regRefreshID.insert(std::make_pair(reg, 0));
    }
}

void Graph::addLabel(string label, Int instrID) {
    // cout << "Add label " + label << endl;
    if(label2Instr.find(label) != label2Instr.end()) {
        util::showWarning("Duplicate Label: " + label);
    } else {
        label2Instr.insert(std::make_pair(label, instrID));
    }
}

Int Graph::getNodeIDFromInstrID(Int instrID) const {
    if(instr2Node.find(instrID) == instr2Node.end()) util::showError("getNodeIDFromInstrID Unexpected instrID: " + to_string(instrID));
    return instr2Node.at(instrID);
}

Set<Int> Graph::getSTDepNodes(Int nodeID) const {
    assert(instrNodes.at(nodeID)->getInstrClass() == InstrClass::ST);
    Set<Int> depNodeIDs;
    queue<Int> nodeIDQueue;

    for(Int i = 0; i < nodeCnt; i++) {
        if(judgeEdgeByNodeID(i, nodeID, EdgeType::ADD) || judgeEdgeByNodeID(i, nodeID, EdgeType::JUMP)) nodeIDQueue.push(i);
    }

    // nodeIDQueue.push(nodeID);

    while(!nodeIDQueue.empty()) {
        Int curNodeID  = nodeIDQueue.front(); nodeIDQueue.pop();

        if(depNodeIDs.find(curNodeID) != depNodeIDs.end()) continue;
        
        depNodeIDs.insert(curNodeID);
        for(Int i = 0; i < nodeCnt; i++) 
            if(judgeEdgeByNodeID(i, curNodeID)) nodeIDQueue.push(i);
    }

    depNodeIDs.insert(nodeID);

    return depNodeIDs;
} 

const Node* Graph::getNodeFromInstrID(Int instrID) const {
    const Node* curNode = instrNodes.at(getNodeIDFromInstrID(instrID));
    assert(curNode->getInstrID() == instrID);
    return curNode;
}

bool Graph::judgeEdgeByNodeID(Int st, Int ed) const {
    if(st >= nodeCnt || ed >= nodeCnt) util::showError("nodeID >= nodeCnt in judgeEdge");
    return graphTable.at(st).at(ed) > 0;
}

bool Graph::judgeEdgeByNodeID(Int st, Int ed, EdgeType edgeT) const {
    if(st >= nodeCnt || ed >= nodeCnt) util::showError("nodeID >= nodeCnt in judgeEdge");
    return (graphTable.at(st).at(ed) > 0 && edgeTypes.at(st).at(ed) == edgeT);
}

bool Graph::judgeNodeByInstrID(Int instrID) const {
    if(instr2Node.find(instrID) == instr2Node.end()) return false;
    return true;
}

bool Graph::judgeEdgeByInstrID(Int st, Int ed) const {
    Int stID = getNodeIDFromInstrID(st);
    Int edID = getNodeIDFromInstrID(ed);

    return judgeEdgeByNodeID(stID, edID);
}

bool Graph::judgeEdgeByInstrID(Int st, Int ed, EdgeType edgeT) const {
    Int stID = getNodeIDFromInstrID(st);
    Int edID = getNodeIDFromInstrID(ed);

    return judgeEdgeByNodeID(stID, edID, edgeT);
}

EdgeType Graph::getEdgeTypeByInstrID(Int st, Int ed) const {
    if(!judgeEdgeByInstrID(st, ed)) return EdgeType::NONE;
    Int stID = getNodeIDFromInstrID(st);
    Int edID = getNodeIDFromInstrID(ed);

    return edgeTypes.at(stID).at(edID);         // edgeTypes[stID][edID];
}

Int Graph::getEdgeTimeByInstrID(Int st, Int ed) const {
    if(!judgeEdgeByInstrID(st, ed)) return 0;
    Int stID = getNodeIDFromInstrID(st);
    Int edID = getNodeIDFromInstrID(ed);

    return edgeTimes.at(stID).at(edID);
}

void Graph::genDynamicPtxNodes(const vector<string>& instrs) {
    nodeCnt = 0;
    for(Int i = 0; i < instrs.size(); i++) {
        Int instrID = util::getInstrID(instrs.at(i));
        if(instr2Node.find(instrID) == instr2Node.end()) {
            instr2Node.insert(std::make_pair(instrID, nodeCnt++));
            instrNodes.push_back((Node*)new DynamicNode(instrs.at(i)));
            // util::getLstElem(instrNodes)->printInfo();
            assert(instrNodes.size() == nodeCnt);
        }
    }
}

void Graph::genStaticPtxNodes(const vector<string>& instrs) {
    nodeCnt = 0;
    for(Int i = 0; i < instrs.size(); i++) {
        Int instrID = util::getInstrID(instrs.at(i));
        if(instr2Node.find(instrID) == instr2Node.end()) {
            instr2Node.insert(std::make_pair(instrID, nodeCnt++));
            instrNodes.push_back((Node*)new StaticNode(instrs.at(i)));
            // util::getLstElem(instrNodes)->printInfo();
            assert(instrNodes.size() == nodeCnt);
        }
    }

    initStaticLabels(instrs);
}

void Graph::initPtxGraph() {
    assert(nodeCnt == instrNodes.size());
    
    graphTable.resize(nodeCnt);
    for(Int i = 0; i < nodeCnt; i++) graphTable.at(i).resize(nodeCnt, 0);
    
    edgeTypes.resize(nodeCnt);
    for(Int i = 0; i < nodeCnt; i++) edgeTypes.at(i).resize(nodeCnt, EdgeType::NONE);

    edgeTimes.resize(nodeCnt);
    for(Int i = 0; i < nodeCnt; i++) edgeTimes.at(i).resize(nodeCnt, 0);
}

void Graph::initStaticLabels(const vector<string>& instrs) {
    for(Int i = 0; i < instrs.size(); i++) {
        Int instrID = util::getInstrID(instrs.at(i));
        
        const Node* curNode = getNodeFromInstrID(instrID);
        if(curNode->getInstrClass() == InstrClass::LABEL) {
            addLabel(curNode->getInstrType(), instrID + 1);
        }
    }
}

vector<EdgeInfo> Graph::getStaticDepRegEdges(const string instr, const vector<Graph>& dynamicGraphs, const vector<Int>& dynamicWeights) const {    
    Int instrID = util::getInstrID(instr);
    vector<EdgeInfo> res;
    assert(dynamicGraphs.size() == dynamicWeights.size());
    for(Int i = 0; i < dynamicGraphs.size(); i++) {
        const Graph& curGraph  = dynamicGraphs.at(i);
        const Int    curWeight = dynamicWeights.at(i);
        
        if(!curGraph.judgeNodeByInstrID(instrID)) continue;

        for(Node* curNode : curGraph.getInstrNodes()) {
            Int curInstrID = curNode->getInstrID();

            if(curGraph.judgeEdgeByInstrID(curInstrID, instrID)) {
                EdgeType eType = curGraph.getEdgeTypeByInstrID(curInstrID, instrID);
                Int      eTime = curGraph.getEdgeTimeByInstrID(curInstrID, instrID);
                res.push_back((EdgeInfo){curInstrID, instrID, eType, eTime * curWeight});
            }
        }
    }

    return res;
}

void Graph::genDynamicPtxGraph(const vector<string>& instrs) {
    genDynamicPtxNodes(instrs);
    initPtxGraph();

    for(Int i = 0; i < instrs.size(); i++) {
        Int instrID = util::getInstrID(instrs.at(i));
        const Node* curNode = getNodeFromInstrID(instrID);

        InstrClass instrClass = curNode->getInstrClass();
        if(instrClass == InstrClass::UNDO) {
            continue; // UNDO
        } else if(instrClass == InstrClass::LD) {
            assert(curNode->getDepRegs().size() <= 1);
            for(string depRegADD : curNode->getDepRegs()) {
                if(!util::isAdd(depRegADD)) util::showWarning("LD instr has wrong arg: " + instrs.at(i));
                string depReg = util::getRegFromAdd(depRegADD);

                // Reg store Address
                const auto &itReg = reg2LstInstr.find(depReg);
                if(itReg != reg2LstInstr.end()) addEdge(itReg->second, instrID, EdgeType::ADD);
                else util::showWarning("LD instr load unused Reg: " + depReg);

                // Out Memory store Data
                const auto &itOut = reg2LstInstr.find(depRegADD);
                if(itOut != reg2LstInstr.end()) addEdge(itOut->second, instrID, EdgeType::DATA);
            }

            addReg(curNode->getDesReg(), instrID);
        } else if(instrClass == InstrClass::ST) {
            assert(curNode->getDepRegs().size() == 1);
            string desRegAdd = curNode->getDesReg();
            if(!util::isAdd(desRegAdd)) util::showWarning("ST instr has wrong arg: " + instrs.at(i));

            string desReg = util::getRegFromAdd(desRegAdd);

            // Reg store Address
            const auto &itReg = reg2LstInstr.find(desReg);
            if(itReg != reg2LstInstr.end()) addEdge(itReg->second, instrID, EdgeType::ADD);
            else util::showWarning("ST instr load unused Reg: " + desReg);

            for(string depReg : curNode->getDepRegs()) {
                const auto &it = reg2LstInstr.find(depReg);
                if(it != reg2LstInstr.end()) addEdge(it->second, instrID, EdgeType::DATA);
            }

            addReg(curNode->getDesReg(), instrID);
        } else if(instrClass == InstrClass::JUMP) {
            assert(curNode->getDepRegs().size() == 1);

            Int lstInstrID, nxtInstrID, index;
            for(index = i - 1; index >= 0; index--) {
                lstInstrID = util::getInstrID(instrs.at(index));
                const Node* lstNode = getNodeFromInstrID(lstInstrID);
                if(lstNode->getInstrClass() == InstrClass::UNDO) continue;
                break;
            }
            assert(index >= 0);

            for(index = i + 1; index < instrs.size(); index++) {
                nxtInstrID = util::getInstrID(instrs.at(index));
                const Node* nxtNode = getNodeFromInstrID(nxtInstrID);
                if(nxtNode->getInstrClass() == InstrClass::UNDO) continue;
                break;
            }
            assert(index < instrs.size());

            addEdge(lstInstrID, nxtInstrID, EdgeType::JUMP);
        } else if(instrClass == InstrClass::TEX) {
            for(string depReg : curNode->getDepRegs()) {
                const auto &it = reg2LstInstr.find(depReg);
                if(it != reg2LstInstr.end()) addEdge(it->second, instrID, EdgeType::DATA);
            }

            for(string desReg : curNode->getDesRegs()) {
                addReg(desReg, instrID);
            }
        } else if(instrClass == InstrClass::RET) {
            assert(i > 0);
            Int lstInstrID = util::getInstrID(instrs.at(i - 1));
            const Node* lstNode = getNodeFromInstrID(lstInstrID);
            if(lstNode->getInstrClass() != InstrClass::JUMP) {
                addEdge(lstInstrID, instrID, EdgeType::JUMP);
            }
        } else if(instrClass == InstrClass::OTHER) {
            for(string depReg : curNode->getDepRegs()) {
                const auto &it = reg2LstInstr.find(depReg);
                if(it != reg2LstInstr.end()) addEdge(it->second, instrID, EdgeType::DATA);
            }
            addReg(curNode->getDesReg(), instrID);
        }
    }
}

void Graph::genStaticPtxGraph(const vector<string>& instrs, const vector<Graph>& dynamicGraphs, const vector<Int>& dynamicWeight) {
    genStaticPtxNodes(instrs);
    initPtxGraph();

    for(Int i = 0; i < instrs.size(); i++) {
        // cout << "Line: " << instrs.at(i) << endl;
        Int instrID = util::getInstrID(instrs.at(i));
        const Node* curNode = getNodeFromInstrID(instrID);
        InstrClass instrClass = curNode->getInstrClass();

        if(instrClass == InstrClass::UNDO || instrClass == InstrClass::JUMP || instrClass == InstrClass::NJUMP) {
            continue;
        } else if(instrClass == InstrClass::LD) {
            assert(curNode->getDepRegs().size() <= 1);

            vector<EdgeInfo> depInstrEdges = getStaticDepRegEdges(instrs.at(i), dynamicGraphs, dynamicWeight);
            for(EdgeInfo& edge : depInstrEdges) {
                assert(edge.edInstrID == instrID);
                if(edge.edgeType != EdgeType::NONE)
                    addEdge(edge.stInstrID, edge.edInstrID, edge.edgeType, edge.edgeTime);
            }
        } else if(instrClass == InstrClass::ST) {
            assert(curNode->getDepRegs().size() == 1);
            vector<EdgeInfo> depInstrEdges = getStaticDepRegEdges(instrs.at(i), dynamicGraphs, dynamicWeight);
            for(EdgeInfo& edge : depInstrEdges) {
                assert(edge.edInstrID == instrID);
                if(edge.edgeType != EdgeType::NONE)
                    addEdge(edge.stInstrID, edge.edInstrID, edge.edgeType, edge.edgeTime);
            }
        } else if(instrClass == InstrClass::TEX) {      // new judge for NJUMP, different with Dynamic
            vector<EdgeInfo> depInstrEdges = getStaticDepRegEdges(instrs.at(i), dynamicGraphs, dynamicWeight);
            for(EdgeInfo& edge : depInstrEdges) {
                assert(edge.edInstrID == instrID);
                if(edge.edgeType != EdgeType::NONE)
                    addEdge(edge.stInstrID, edge.edInstrID, edge.edgeType, edge.edgeTime);
            }
        } else if(instrClass == InstrClass::OTHER) {
            vector<EdgeInfo> depInstrEdges = getStaticDepRegEdges(instrs.at(i), dynamicGraphs, dynamicWeight);
            for(EdgeInfo& edge : depInstrEdges) {
                assert(edge.edInstrID == instrID);
                if(edge.edgeType != EdgeType::NONE)
                    addEdge(edge.stInstrID, edge.edInstrID, edge.edgeType, edge.edgeTime);
            }
        } else if(instrClass == InstrClass::RET) {
            vector<EdgeInfo> depInstrEdges = getStaticDepRegEdges(instrs.at(i), dynamicGraphs, dynamicWeight);
            for(EdgeInfo& edge : depInstrEdges) {
                assert(edge.edInstrID == instrID);
                if(edge.edgeType != EdgeType::NONE)
                    addEdge(edge.stInstrID, edge.edInstrID, edge.edgeType, edge.edgeTime);
            }
        } else if(instrClass == InstrClass::LABEL) {    // new judge
            continue;
        } else util::showWarning("Un Expected InstrCalss for instr: " + instrs.at(i));
    }
}

bool Graph::haveNeighborNodeID(const Int nodeID) const {
    for(Int i = 0; i < nodeCnt; i++) {
        if(judgeEdgeByNodeID(i, nodeID) || judgeEdgeByNodeID(nodeID, i)) return true;
    }
    return false;
}

bool Graph::haveNeighborInstrID(const Int instrID) const {
    Int nodeID = getNodeIDFromInstrID(instrID);
    return haveNeighborNodeID(nodeID);
}

void Graph::printNodeCsv(const string outFile) const {
    std::ofstream ofs(outFile);
    if(!ofs.is_open()) {
        util::showError("Can not open \"" + outFile + "\"");
        return ;
    }

    for(Int i = 0; i < instrNodes.size(); i++) {
        Node* curNode = instrNodes.at(i);
        if(!haveNeighborNodeID(i)) continue;

        ofs << curNode->getInstrID() << endl;
    }
}

void Graph::printEdgeCsv(const string outFile) const {
    std::ofstream ofs(outFile);
    if(!ofs.is_open()) {
        util::showError("Can not open \"" + outFile + "\"");
        return ;
    }

    for(Int i = 0; i < instrNodes.size(); i++) {
        for(Int j = 0; j < instrNodes.size(); j++) {
            if(graphTable.at(i).at(j) == 1) {
                ofs << instrNodes.at(i)->getInstrID() 
                    << "," << instrNodes.at(j)->getInstrID() 
                    << "," << edgeTimes.at(i).at(j)<< endl;
            }
        }
    }
}

Int Graph::getNodeCnt() const {
    return nodeCnt;
}

const vector<Node*>& Graph::getInstrNodes() const {
    return instrNodes;
}

const Map<Int, Int>& Graph::getInstr2Node() const {
    return instr2Node;
}

const vector<vector<Int> >& Graph::getGraphTable() const {
    return graphTable;
}

const vector<vector<Int> >& Graph::getEdgeTimes() const {
    return edgeTimes;
}

const vector<vector<EdgeType> >& Graph::getEdgeTypes() const {
    return edgeTypes;
}

Graph::Graph(){}

// Graph::Graph(Int maxInstrID) {
//     maxInstrID += 2;
//     usedInstrs.resize(maxInstrID, false);
//     instrNodes.resize(maxInstrID);
//     graphTable.resize(maxInstrID);
//     for(Int i = 0; i < maxInstrID; i++) graphTable.at(i).resize(maxInstrID, 0);
//     edgeTypes.resize(maxInstrID);
//     for(Int i = 0; i < maxInstrID; i++) edgeTypes.at(i).resize(maxInstrID, EdgeType::NONE);
// }