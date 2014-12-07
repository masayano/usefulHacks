/*******************************************************
/
/  Copyright 2014, Masahiro Yano 
/  Licensed under the BSD licenses. 
/  https://github.com/masayano 
/
/  What is this?
/
/   [tab separated word count file"s": word, count]
/   -> [tab separated word slope/average file:
/               word,
/               slope of smoothed probability / average,
/               JSON word number history (not smoothed),
/               JSON word smoothed probability history]
/
/********************************************************/
#include <fstream>
#include <string>
#include <map>
#include <vector>
#include <boost/tokenizer.hpp>
#include <boost/lexical_cast.hpp>
#include <algorithm>
#include <cmath>
#include <ctime>
#include <sstream>
#include <iomanip>

const double MIN_AVERAGE_PROBABILITY = 1.0e-6;

typedef boost::char_separator<char> char_separator;
typedef boost::tokenizer<char_separator> tokenizer;
char_separator tabSep("\t");

const std::vector<std::string> splitString(const std::string& str) {
    std::vector<std::string> parts;
    tokenizer tokens(str, tabSep);
    for (const auto& part : tokens) {
        parts.push_back(part);
    }
    return parts;
}

void loadFile(
        std::map<std::string, std::vector<int> >&    smoothedNumMatrix,
        std::map<std::string, std::vector<double> >& smoothedProbMatrix,
        std::vector<std::map<std::string, int> >& wordCounters,
        std::vector<double>& totalWordNums,
        const std::string& fileName) {
    std::map<std::string, int> wordCounter;
    int totalWordNum = 0;
    std::ifstream ifs(fileName.c_str());
    std::string buf;
    while(ifs && std::getline(ifs, buf)) {
        const auto parts = splitString(buf);
        const auto& word  = parts[0];
        const auto& count = boost::lexical_cast<int>(parts[1]);
        wordCounter[word] = count;
        const auto& it = smoothedNumMatrix.find(word);
        if(it == std::end(smoothedNumMatrix)) {
            smoothedNumMatrix [word] = std::vector<int>();
            smoothedProbMatrix[word] = std::vector<double>();
        }
        totalWordNum += 1;
    }
    wordCounters .push_back(wordCounter);
    totalWordNums.push_back(static_cast<double>(totalWordNum));
}

void makeMatrix(
        std::map<std::string, std::vector<int> >&    smoothedNumMatrix,
        std::map<std::string, std::vector<double> >& smoothedProbMatrix,
        const std::vector<std::map<std::string, int> >& wordCounters,
        const std::vector<double>& totalWordNums) {
    const auto wordTypeNum = static_cast<double>(smoothedNumMatrix.size());
    for(int i = 0; i < wordCounters.size(); ++i) {
        const auto& wordCounter  = wordCounters [i];
        const auto& totalWordNum = totalWordNums[i];
        const auto& totalNumAfterSmoothed = totalWordNum + wordTypeNum;
        for(const auto& elem : smoothedNumMatrix) {
            const auto& key = elem.first;
            const auto& it  = wordCounter.find(key);
            int smoothedNumber;
            if(it != std::end(wordCounter)) {
                smoothedNumber = (*it).second + 1; // smoothing
            } else {
                smoothedNumber = 1; // smoothing
            }
            const auto probability = smoothedNumber / totalNumAfterSmoothed;
            smoothedNumMatrix [key].push_back(smoothedNumber);
            smoothedProbMatrix[key].push_back(probability);
        }
    }
}

const std::vector<double> range(int num) {
    std::vector<double> output;
    for(int i = 0; i < num; ++i) {
        output.push_back(i);
    }
    return output;
}

double calcSlope(
        const std::vector<double>& values_x,
        const std::vector<double>& values_y) {
    const auto length = static_cast<double>(values_x.size());
    const auto average_x = std::accumulate(std::begin(values_x), std::end(values_x), 0.0) / length;
    const auto average_y = std::accumulate(std::begin(values_y), std::end(values_y), 0.0) / length;
    double coVar = 0;
    double var_x = 0;
    for(int i = 0; i < length; ++i) {
        const auto xDiff = values_x[i] - average_x;
        const auto yDiff = values_y[i] - average_y;
        coVar += (xDiff * yDiff);
        var_x += (xDiff * xDiff);
    }
    return coVar / var_x;
}

const std::vector<std::pair<double, std::string> > calcSlope(
        const std::map<std::string, std::vector<double> >& smoothedProbMatrix) {
    std::vector<std::pair<double, std::string> > results;
    const auto length = (*std::begin(smoothedProbMatrix)).second.size();
    const auto values_x = range(length);
    for(const auto& elem : smoothedProbMatrix) {
        const auto& key      = elem.first;
        const auto& values_y = elem.second;
        const auto z = calcSlope(values_x, values_y);
        const auto average = std::accumulate(std::begin(values_y), std::end(values_y), 0.0) / length;
        results.push_back(std::make_pair(z / average, key));
    }
    std::sort(std::begin(results), std::end(results), std::greater<std::pair<double, std::string>>());
    return results;
}

const std::string getDate() {
    time_t now;
    time(&now);
    const auto date = localtime(&now);
    const auto year   = date->tm_year + 1900;
    const auto month  = date->tm_mon + 1;
    const auto day    = date->tm_mday;
    const auto hour   = date->tm_hour;
    const auto minute = date->tm_min;
    std::stringstream ss;
    ss << year << "_" << month << "_" << day << "_" << hour << "_" << minute;
    return ss.str();
}

const std::string makeStrProbArray(const std::vector<double>& probArray) {
    std::stringstream output;
    output << "[";
    for(int i = 0; i < probArray.size(); ++i) {
        output << std::setprecision(3) << probArray[i];
        if(i != probArray.size()-1) {
            output << ", ";
        }
    }
    output << "]";
    return output.str();
}

const std::string makeStrNumArray(const std::vector<int>& numArray) {
    std::stringstream output;
    output << "[";
    for(int i = 0; i < numArray.size(); ++i) {
        output << numArray[i] - 1;
        if(i != numArray.size()-1) {
            output << ", ";
        }
    }
    output << "]";
    return output.str();
}

void writeResults(
        const std::vector<std::pair<double, std::string> >& results,
        std::map<std::string, std::vector<int> >&    smoothedNumMatrix,
        std::map<std::string, std::vector<double> >& smoothedProbMatrix) {
    const auto fileName = "analysis/" + getDate() + ".log";
    std::ofstream ofs(fileName.c_str());
    for(const auto& elem : results) {
        const auto& slope = elem.first;
        const auto& key   = elem.second;
        const auto& probArray = smoothedProbMatrix[key];
        const auto strProbArray = makeStrProbArray(probArray);
        const auto averageProb = std::accumulate(std::begin(probArray), std::end(probArray), 0.0) / probArray.size();
        if(averageProb > MIN_AVERAGE_PROBABILITY) {
            const auto strNumArray = makeStrNumArray(smoothedNumMatrix[key]);
            ofs
                    << key
                    << "\t"
                    << std::setprecision(3) << slope
                    << "\t"
                    << strNumArray
                    << "\t"
                    << strProbArray
                    << std::endl;
        }
    }
}

int main(int argc, char** argv) {
    std::map<std::string, std::vector<int> >    smoothedNumMatrix;
    std::map<std::string, std::vector<double> > smoothedProbMatrix;
    std::vector<std::map<std::string, int> >    wordCounters;
    std::vector<double>                         totalWordNums;
    if(argc >= 2) {
        for(int i = 1; i < argc; ++i) {
            const auto fileName = argv[i];
            std::cout << "[Load for analyzing] " << fileName << std::endl;
            loadFile(
                    smoothedNumMatrix,
                    smoothedProbMatrix,
                    wordCounters,
                    totalWordNums,
                    fileName);
        }
        makeMatrix(
                smoothedNumMatrix,
                smoothedProbMatrix,
                wordCounters,
                totalWordNums);
        const auto results = calcSlope(smoothedProbMatrix);
        writeResults(
                results,
                smoothedNumMatrix,
                smoothedProbMatrix);
    } else {
        std::cout << "Usage: python analyzeWord.py [word count file name(s)]" << std::endl;
    }
    return 0;
}
