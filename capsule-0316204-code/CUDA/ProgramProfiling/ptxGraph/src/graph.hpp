#pragma once

#include "util.hpp"

class Node {
protected:
    Int    instrID;     // unique
    string instrType;
    Float  prSDC;       // probability of SDC
    // Int    opType;      // 0-value 1-address
    string desReg;      // destination register
    vector<string> desRegs;         // for InstrClass::Tex
    vector<string> depRegs;
    InstrClass instrClass;

    virtual void setInstrNodeST(const vector<string>& words, string instr, bool havePrSDC = false);
    virtual void setInstrNodeLD(const vector<string>& words, string instr, bool havePrSDC = false);
    virtual void setInstrNodeJUMP(const vector<string>& words, string instr, bool havePrSDC = false){}
    virtual void setInstrNodeUNDO(const vector<string>& words, string instr, bool havePrSDC = false);
    virtual void setInstrNodeOTHER(const vector<string>& words, string instr, bool havePrSDC = false);
    virtual void setInstrNodeTEX(const vector<string>& words, string instr, bool havePrSDC = false);

public:
    Int    getInstrID() const;
    string getInstrType() const;
    Float  getPrSDC() const;
    Int    getOpType() const;
    string getDesReg() const;
    const vector<string>& getDepRegs() const;
    InstrClass getInstrClass() const;

    virtual const vector<string>& getNxtLabel() const { util::showWarning("Call wrong getNxtLabel"); return depRegs;}
    const vector<string>& getDesRegs() const ;
    virtual void setInstrNode(string instr) = 0;

    virtual void printInfo() const;
    Node();
};

class DynamicNode : Node {
protected:
    void setInstrNodeJUMP(const vector<string>& words, string instr, bool havePrSDC = false);

public:
    Float otherThreadInfl;     // unused
    Float getOhterThreadInfl() const;
    void  setOtherThreadInfl(Float influence);

    void setInstrNode(string instr);

    DynamicNode();
    DynamicNode(string instr);
};

class StaticNode : Node {
protected:
    vector<string> nxtLabel;        // for InstrClass::JUMP

    void setInstrNodeJUMP(const vector<string>& words, string instr, bool havePrSDC = false);
    void setInstrNodeNJUMP(const vector<string>& words, string isntr, bool havePrSDC = false);

public:
    const vector<string>& getNxtLabel() const;

    void setInstrNode(string instr);

    void printInfo() const;

    StaticNode();
    StaticNode(string instr);
};

struct EdgeInfo {
    Int stInstrID;
    Int edInstrID;
    EdgeType edgeType;
    Int edgeTime;
};

class Graph {
private :
    // vector<bool>         usedInstrs;        // fasle - unuse instr
    Int nodeCnt;
    vector<Node*>        instrNodes;
    Map<Int, Int>        instr2Node;           // [instr] = nodeID
    vector<vector<Int> > graphTable;
    Map<string, Int>     reg2LstInstr;
    Map<string, Int>     regRefreshID;
    Map<string, Int>     label2Instr;           // [label] = instrID
    vector<vector<EdgeType> > edgeTypes;
    vector<vector<Int> > edgeTimes;

    void addNode(string instr);
    void addEdge(Int st, Int ed, EdgeType eType);           // st -> ed;
    void addEdge(Int st, Int ed, EdgeType eType,  Int eTime);           // st -> ed;
    void addReg(string reg, Int instrID);  // reg is instrID's desReg
    void addLabel(string label, Int instrID);

    void genDynamicPtxNodes(const vector<string>& instrs);
    void genStaticPtxNodes(const vector<string>& instrs);
    void initPtxGraph();

    void initStaticLabels(const vector<string>& instrs);
    vector<EdgeInfo> getStaticDepRegEdges(const string instr, const vector<Graph>& dynamicGraphs, const vector<Int>& dynamicWeights) const;

    Int  getNodeIDFromInstrID(Int instrID) const;

    bool judgeEdgeByNodeID(Int st, Int ed) const;
    bool judgeEdgeByNodeID(Int st, Int ed, EdgeType edgeT) const;
public :
    void genDynamicPtxGraph(const vector<string>& instrs);
    void genStaticPtxGraph(const vector<string>& instrs, const vector<Graph>& dynamicGraphs, const vector<Int>& dynamicWeight);

    const Node* getNodeFromInstrID(Int instrID) const;

    // const vector<bool>&         getUsedInstrs() const;
    Int getNodeCnt() const;
    const vector<Node*>&        getInstrNodes() const;
    const Map<Int, Int>&        getInstr2Node() const;
    const vector<vector<Int> >& getGraphTable() const;
    const vector<vector<Int> >& getEdgeTimes() const;
    const vector<vector<EdgeType> >& getEdgeTypes() const;
    
    EdgeType getEdgeTypeByInstrID(Int st, Int ed) const;
    Int getEdgeTimeByInstrID(Int st, Int ed) const;

    bool haveNeighborNodeID(const Int nodeID) const;
    bool haveNeighborInstrID(const Int instrID) const;

    void printNodeCsv(const string fileName) const;
    void printEdgeCsv(const string fileMane) const;

    bool judgeNodeByInstrID(Int instrID) const;
    bool judgeEdgeByInstrID(Int st, Int ed) const;
    bool judgeEdgeByInstrID(Int st, Int ed, EdgeType edgeT) const;
    Set<Int> getSTDepNodes(Int nodeID) const;

    Graph();
    // Graph(Int maxInstrID);
};