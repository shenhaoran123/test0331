#include "graph.hpp"
#include "util.hpp"
#include "visual.hpp"

#include "../lib/cxxopts.hpp"

class OptionDict {
   public:
    string ptxFile;
    string ptxWeightFile;
    vector<string> dynamicPtxFiles;
    bool dynamicFlag;
    bool staticFlag;

    Map<string, Int> fileID2Weight;

    bool judgeLine(string line) const;
    vector<string> readDynamicFile(string filePath) const;
    void setPtxWeight();

    void genDynamicPtxGraph(string filePath) const;
    void genStaticPtxGraph(string filePath, vector<string> dynamicPtxFiles) const;

    void runCommand() const;

    OptionDict(int argc, char** argv);
};

/* global functions ========================================================= */

int main(int argc, char** argv);
