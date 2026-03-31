#include "util.hpp"


/* constants ******************************************************************/
const string COMMENT_WORD = "c";

const string PTX_FILE_OPTION = "pf";
const string PR_SDC_OPTION = "pr";
const string DYNAMIC_OPTION = "dynamic";
const string STATIC_OPTION = "static";
const string DYNAMIC_PTX_LIST_OPTION = "dl";
const string DYNAMIC_PTX_FILES_OPTION = "df";
const string DYNAMIC_PTX_WEIGHT_OPTION = "dw";
const string HELP_OPTION = "h,help";

/* global variables ***********************************************************/
string dotPath = "./dot/";
string csvPath = "./csv/";
bool prSDCFlag = false;

/* namespace util *************************************************************/
void util::printComment(const string& message, Int preceedingNewLines, Int followingNewLines, bool commented) {
    for (Int i = 0; i < preceedingNewLines; i++)
        cout << "\n";
    cout << (commented ? COMMENT_WORD + " " : "") << message;
    for (Int i = 0; i < followingNewLines; i++)
        cout << "\n";
}

void util::printBoldLine(bool commented) {
    printComment("******************************************************************", 0, 1, commented);
}

void util::printThickLine(bool commented) {
    printComment("==================================================================", 0, 1, commented);
}

void util::printThinLine() {
    printComment("------------------------------------------------------------------");
}

void util::showWarning(const string& message, bool commented) {
    printBoldLine(commented);
    printComment("MY_WARNING: " + message, 0, 1, commented);
    printBoldLine(commented);
}

void util::showError(const string& message, bool commented) {
    throw MyError(message, commented);
}

InstrClass util::judgeInstrDynamic(const string& str) {
    if(str.substr(0, 2) == "ld") return InstrClass::LD;
    if(str.substr(0, 2) == "st") return InstrClass::ST;
    if(str.substr(0, 1) == "@") return InstrClass::JUMP;
    if(str.substr(0, 3) == "tex") return InstrClass::TEX;
    if(str.substr(0, 3) == "ret") return InstrClass::RET;
    if(str.substr(0, 7) == "bra.uni") return InstrClass::UNDO;
    if(str.substr(0, 8) == "bar.sync") return InstrClass::UNDO;

    return InstrClass::OTHER;
}

InstrClass util::judgeInstrStatic(const string& str) {
    if(str.substr(0, 2) == "ld") return InstrClass::LD;
    if(str.substr(0, 2) == "st") return InstrClass::ST;
    if(str.substr(0, 1) == "@") return InstrClass::JUMP;
    if(str.substr(0, 3) == "ret") return InstrClass::RET;
    if(str.substr(0, 3) == "tex") return InstrClass::TEX;
    if(str.substr(0, 7) == "bra.uni") return InstrClass::NJUMP;
    if(str.substr(0, 8) == "bar.sync") return InstrClass::UNDO;
    if(str.substr(0, 2) == "BB") return InstrClass::LABEL;
    return InstrClass::OTHER;
}

bool util::isReg(const string& reg) {
    if(reg.find("%") != string::npos) return true;
    else return false;
}

bool util::isAdd(const string& reg) {
    if(reg.at(0) == '[' && getLstElem(reg) == ']') return true;
    else return false;
}

bool util::isLabel(const string& label) {
    if(label.substr(0, 2) == "BB" ) return true;
    return false;
}

string util::getRegFromAdd(const string& reg) {
    if(!isReg(reg) || !isAdd(reg)) showError("Wrong  in gerRegFromAdd: " + reg);
    Int stPos = reg.find("%"), edPos = reg.size() - 1;

    if(reg.find("+") != string::npos) edPos = reg.find("+"); 

    return reg.substr(stPos, edPos - stPos);    // [stPos, edPos)
}

void util::formatReg(string& reg) {
    if(!isReg(reg)) showWarning("Formated string (" + reg + ") is not reg !!!");
    if(getLstElem(reg) != ',' && getLstElem(reg) != ';') showWarning("Formated string (" + reg + ") have no end char");

    reg = reg.substr(0, reg.size() - 1);
}

void util::formatLabel(string& label) {
    if(!isLabel(label)) showWarning("Formated string (" + label + ") is not reg !!!");

    if(getLstElem(label) == ';' || getLstElem(label) == ':') label = label.substr(0, label.size() - 1);
}

Int util::getInstrID(const string& str) {
    return std::stoi(str.substr(0, str.find(" ")));
}

char util::getLstElem(string t) {
    return t.at(t.size() - 1);
}

/* class MyError **************************************************************/
MyError::MyError(const string& message, bool commented) {
    util::printComment("MY_ERROR: " + message, 0, 1, commented);
}