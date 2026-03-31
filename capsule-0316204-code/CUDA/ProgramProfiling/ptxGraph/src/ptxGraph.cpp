#include "ptxGraph.hpp"

OptionDict::OptionDict(int argc, char** argv) {
    cxxopts::Options options("ptxGraph", "Generate Dynamic/Static Ptx Graph");
    options.set_width(118);

    using cxxopts::value;
    options.add_options()
        (PTX_FILE_OPTION, "Ptx file path; string (required)", value<string>())
        (DYNAMIC_OPTION, "Generate Dynamic Ptx Graph")
        (STATIC_OPTION, "Generate Static Ptx Graph")
        (PR_SDC_OPTION, "Pr SDC Flag")
        // (DYNAMIC_PTX_LIST_OPTION, "Dynamic Ptx_File List", value<vector<string> >())
        (DYNAMIC_PTX_FILES_OPTION, "Read Dynamic Ptx_File from File", value<string>())
        (DYNAMIC_PTX_WEIGHT_OPTION, "Dynamic Ptx Weight File", value<string>()->default_value(""))
        (HELP_OPTION, "help");

    cxxopts::ParseResult result = options.parse(argc, argv);
    if (result.count(HELP_OPTION) || !result.count(PTX_FILE_OPTION)) {
        cout << options.help();
    } else {
        ptxFile = result[PTX_FILE_OPTION].as<string>();

        dynamicFlag = result.count(DYNAMIC_OPTION);
        staticFlag  = result.count(STATIC_OPTION);
        if(!dynamicFlag && !staticFlag) util::showError("Need one graph type --dynamic or --static");
        if(dynamicFlag  &&  staticFlag) util::showError("Need only one graph type --dynamic or --static");

        prSDCFlag   = result.count(PR_SDC_OPTION);      // global var

        if(staticFlag) {
            if(result.count(DYNAMIC_PTX_FILES_OPTION)) {
                string readDynamicFilePath = result[DYNAMIC_PTX_FILES_OPTION].as<string>();
                std::ifstream inputFileStream(readDynamicFilePath);
                string line;

                if (!inputFileStream.is_open()) util::showError("unable to open dynamic ptx file '" + readDynamicFilePath + "'");

                while (std::getline(inputFileStream, line)) dynamicPtxFiles.push_back(line);
                inputFileStream.close();
            // } else if(result.count(DYNAMIC_PTX_LIST_OPTION)) {      // unused
            //     dynamicPtxFiles = result[DYNAMIC_PTX_LIST_OPTION].as<vector<string> >();
            } else {
                util::showError("Static Ptx Graph need dynamic file");
            }

            if(result.count(DYNAMIC_PTX_WEIGHT_OPTION)) {
                ptxWeightFile = result[DYNAMIC_PTX_WEIGHT_OPTION].as<string>();
                setPtxWeight();
            }
        }

        runCommand();
    }
}

void OptionDict::runCommand() const{
    if (staticFlag) {
        genStaticPtxGraph(ptxFile, dynamicPtxFiles);
    } else if (dynamicFlag) {
        genDynamicPtxGraph(ptxFile);
    }
}

bool OptionDict::judgeLine(string line) const {
    if (util::isReg(line)) return true;
    if (line.find("BB") != string::npos) return true;
    if (line.find("ret") != string::npos) return true;

    return false;
}

vector<string> OptionDict::readDynamicFile(string filePath) const {
    std::ifstream inputFileStream(filePath);

    if (!inputFileStream.is_open()) {
        util::showError("unable to open dynamic file '" + filePath + "'");
    }

    string line;
    vector<string> retInstrs;

    while (std::getline(inputFileStream, line)) {
        retInstrs.push_back(line);
    }

    inputFileStream.close();
    return retInstrs;
}

void OptionDict::setPtxWeight() {
    std::ifstream inputFileStream(ptxWeightFile);
    string line;

    if (!inputFileStream.is_open()) util::showError("unable to open ptx weight file '" + ptxWeightFile + "'");


    while (std::getline(inputFileStream, line)) {
        string fileID = line.substr(0, line.find(","));
        Int weight    = std::stoi(line.substr(line.find(",") + 1));
        fileID2Weight.insert(std::make_pair(fileID, weight));
    }
    inputFileStream.close();
}

void OptionDict::genDynamicPtxGraph(string filePath) const {
    string fileName = filePath.find_last_of("//") != string::npos ? filePath.substr(filePath.find_last_of("//") + 1, filePath.find_last_of(".") - filePath.find_last_of("//") - 1)
                                                                  : filePath.substr(0, filePath.find_last_of("."));

    vector<string> instrs = readDynamicFile(filePath);

    Graph graph;
    graph.genDynamicPtxGraph(instrs);

    visual::printPtxGraph2Dot(graph, dotPath + fileName + ".dot");

    // const vector<Node*>& instrNodes = graph.getInstrNodes();
    // for (Int i = 0; i < instrNodes.size(); i++) {
    //     if (instrNodes.at(i)->getInstrClass() == InstrClass::ST) {
    //         Set<Int> depNodeIDs = graph.getSTDepNodes(i);

    //         depNodeIDs.insert(i);
    //         visual::printPtxGraph2Dot(graph, dotPath + fileName + "st" + to_string(instrNodes.at(i)->getInstrID()) + ".dot", depNodeIDs);
    //     }
    // }
}

void OptionDict::genStaticPtxGraph(string filePath, vector<string> dynamicFiles) const {
    string fileName = filePath.find_last_of("//") != string::npos ? filePath.substr(filePath.find_last_of("//") + 1, filePath.find_last_of(".") - filePath.find_last_of("//") - 1)
                                                                  : filePath.substr(0, filePath.find_last_of("."));

    std::ifstream inputFileStream(filePath);

    if (!inputFileStream.is_open()) {
        util::showError("unable to open file '" + filePath + "'");
    }

    string line;
    vector<vector<string> > kernelInstrs;
    Int kernelCnt = 0, lineCnt = 0;
    bool kernelStart = false;

    while (std::getline(inputFileStream, line)) {
        lineCnt++;
        if (line == "" || line.at(0) == '.') continue;
        if (line == "{") { kernelStart = true; kernelInstrs.resize(kernelCnt + 1); continue;}
        if (line == "}") { kernelStart = false; kernelCnt++; continue;}
        if (!kernelStart) continue;
        if (!judgeLine(line)) continue;
        line = to_string(lineCnt) + " " + line;
        kernelInstrs.at(kernelCnt).push_back(line);
    }

    inputFileStream.close();

    vector<vector<string> > dynamicInstrsList;
    vector<Int> dynamicPtxWeights;
    for (string file : dynamicFiles) {
        dynamicInstrsList.push_back(readDynamicFile(file));
        
        if(ptxWeightFile != ""){
            string fileID = file.substr(file.find("_") + 1, file.find("-") - file.find("_") - 1);
            if(fileID2Weight.find(fileID) == fileID2Weight.end()) util::showError("Dynamic file: " + file + " doesn't have weight"); 
            dynamicPtxWeights.push_back(fileID2Weight.at(fileID));
        } else {
            dynamicPtxWeights.push_back(1);
        }
    }

    vector<Graph> dynamicGraphs;
    for(const vector<string>& dyInstrs : dynamicInstrsList) {
        dynamicGraphs.push_back(Graph());
        dynamicGraphs.at(dynamicGraphs.size() - 1).genDynamicPtxGraph(dyInstrs);
    }

    for (Int i = 0; i < kernelCnt; i++) {
        Graph graph;
        graph.genStaticPtxGraph(kernelInstrs.at(i), dynamicGraphs, dynamicPtxWeights);

        string kernelFileName = fileName + "_kernel" + to_string(i);
        visual::printPtxGraph2Dot(graph, dotPath + kernelFileName + ".dot");

        graph.printNodeCsv(csvPath + kernelFileName + "_node.csv");
        graph.printEdgeCsv(csvPath + kernelFileName + "_edge.csv");

        cout << kernelFileName << "  Done\n";
    }
}

int main(int argc, char** argv) {
    OptionDict optionDict(argc, argv);
    return 0;
}