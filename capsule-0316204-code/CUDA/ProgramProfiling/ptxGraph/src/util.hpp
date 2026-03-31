#pragma once

/******************************************************************************/
/* inclusions *****************************************************************/
#include <assert.h>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <iterator>
#include <random>
#include <sstream>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <queue>

/* uses ***********************************************************************/
using std::cout;
using std::endl;
using std::string;
using std::to_string;
using std::vector;
using std::queue;

/* types **********************************************************************/
using Float = double; 
using Int   = int;

template <typename K, typename V>
using Map = std::unordered_map<K, V>;
template <typename T>
using Set = std::unordered_set<T>;
template <typename T1, typename T2>
using Pair = std::pair<T1, T2>;

/* constants ******************************************************************/
extern const string COMMENT_WORD;

extern const string PTX_FILE_OPTION;
extern const string PR_SDC_OPTION;
extern const string DYNAMIC_OPTION;
extern const string STATIC_OPTION;
extern const string DYNAMIC_PTX_LIST_OPTION;
extern const string DYNAMIC_PTX_FILES_OPTION;
extern const string DYNAMIC_PTX_WEIGHT_OPTION;
extern const string HELP_OPTION;

/* global variables ***********************************************************/
extern string dotPath;
extern string csvPath;
extern bool prSDCFlag;

/* enmu classes ***************************************************************/

enum class InstrClass {ST, LD, JUMP, NJUMP, TEX, UNDO, OTHER, LABEL, RET};
enum class EdgeType   {NONE, DATA, JUMP, ADD};

/* util ***********************************************************************/
namespace util {
    void printComment(const string& message, Int preceedingNewLines = 0, Int followingNewLines = 1, bool commented = true);
    void printBoldLine(bool commented);
    void printThickLine(bool commented = true);
    void printThinLine();

    void showWarning(const string& message, bool commented = true);
    void showError(const string& message, bool commented = true);

    InstrClass judgeInstrDynamic(const string& str);
    InstrClass judgeInstrStatic(const string& str);

    bool isReg(const string& reg);
    bool isAdd(const string& reg);
    bool isLabel(const string& label);
    string getRegFromAdd(const string& reg);
    
    void formatReg(string& reg);
    void formatLabel(string& label);

    Int  getInstrID(const string& str);
    
    template <typename T>
    T getLstElem(vector<T> t) {
        return t.at(t.size() - 1);
    }
    char getLstElem(string t);
}

class MyError {
   public:
    MyError(const string& message, bool commented);
};
