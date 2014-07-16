/**********************************
/
/  Copyright 2014, Masahiro Yano 
/  Licensed under the BSD licenses. 
/  https://github.com/masayano 
/
************************************/

#include <map>
#include <string>
#include <fstream>
#include <vector>
#include <iostream>

#include <boost/tokenizer.hpp>
#include <boost/lexical_cast.hpp>

const std::vector<std::string> tokenizeString(
        const std::string& sepChars,
        const std::string& str) {
    using namespace boost;
    typedef char_separator<char> SEP;
    typedef tokenizer<SEP>       TOK;
    SEP sep(sepChars.c_str());
    TOK tok(str, sep);
    std::vector<std::string> tokens;
    for(TOK::iterator it = tok.begin(); it != tok.end(); ++it) {
        tokens.push_back(*it);
    }
    return tokens;
}

const std::vector<std::vector<std::string> > loadTokenFile(
        const std::string& sepChars,
        const std::string& tokenFile) {
    using namespace std;
    std::vector<std::vector<std::string> > tokensArray;
    ifstream ifs(tokenFile.c_str());
    string buf;
    while(ifs && getline(ifs, buf)) {
        tokensArray.push_back(tokenizeString(sepChars, buf));
    }
    return tokensArray;
}

const std::map<std::string, std::map<std::string, std::vector<std::string> > > loadReplyDB(const std::string& replyDBFile) {
    using namespace std;
    map<string, map<string, vector<string> > > replyDB;
    const auto tokensArray = loadTokenFile("\t", replyDBFile);
    for(const auto& line : tokensArray) {
        if(line.size() == 3) {
            replyDB[line[0]][line[1]].push_back(line[2]);
        }
    }
    return replyDB;
}

const std::map<std::string, std::vector<std::string> > loadUserDB(const std::string& userDBFile) {
    using namespace std;
    map<string, vector<string> > userDB;
    const auto tokensArray = loadTokenFile("\t", userDBFile);
    for(const auto& line : tokensArray) {
        if(line.size() == 2) {
            userDB[line[0]].push_back(line[1]);
        }
    }
    return userDB;
}

const std::vector<std::pair<std::string, double> > loadDictionary(const std::string& dictionaryFile) {
    std::vector<std::pair<std::string, double> > dictionary;
    const auto tokensArray = loadTokenFile(":", dictionaryFile);
    for(const auto& line : tokensArray) {
        if(line.size() == 4) {
            try {
                const double score = boost::lexical_cast<double>(line[3]);
                dictionary.push_back(std::make_pair(line[0], score));
            } catch(boost::bad_lexical_cast) {
                std::cout << "[Error] On casting \"" << line[3] << "\" in \"" << dictionaryFile << "\"." << std::endl;
            }
        }
    }
    return dictionary;
}

const std::string stringVectorToJSON(const std::vector<std::string>& stringVector) {
    std::string JSON = "[";
    const int length = stringVector.size()-1;
    for(int i = 0; i < length; ++i) {
        JSON += ("\""+stringVector[i] + "\",");
    }
    JSON += ("\""+stringVector[length] + "\"]");
    return JSON;
}

double calcReplyEmotionScore(
        const std::vector<std::pair<std::string, double> >& dictionary,
        const std::vector<std::string>& tokenizedReply) {
    double totalScore = 0;
    for(const auto& pair : dictionary) {
        const auto& word  = pair.first;
        const auto& score = pair.second+1;
        int count = 0;
        for(const auto& token :tokenizedReply) {
            if(token == word) {
                ++count;
            }
        }
        totalScore += count*score;
    }
    return totalScore;
}

int calcRepliesEmotionScore(
        const std::vector<std::pair<std::string, double> >& dictionary,
        const std::vector<std::string>& replies) {
    double score = 0;
    for(const auto& reply : replies) {
        const auto tokenizedReply = tokenizeString(":", reply);
        score += calcReplyEmotionScore(dictionary, tokenizedReply);
    }
    return static_cast<int>(score);
}

const std::vector<std::map<int, std::vector<std::string> > > analyzeReplies(
        const std::map<std::string, std::map<std::string, std::vector<std::string> > >& replyDB,
        const std::map<std::string, std::vector<std::string> >& userDB,
        const std::vector<std::pair<std::string, double> >& dictionary) {
    using namespace std;
    vector<map<int, vector<string> > > analysis;
    int progress = 1;
    for(map<string, map<string, vector<string> > >::const_iterator it1 = replyDB.begin(); it1 != replyDB.end(); ++it1) {
        cout << "Progress:" << progress++ << "/" << replyDB.size() << endl;
        const auto& userId = (*it1).first;
        const auto  userNames = stringVectorToJSON((*(userDB.find(userId))).second);
        const auto& replies_of_user = (*it1).second;
        map<int, vector<string> > analysis_of_user;
        for(map<string, vector<string> >::const_iterator it2 = replies_of_user.begin(); it2 != replies_of_user.end(); ++it2) {
            const auto& toUserId = (*it2).first;
            const auto  toUserNames = stringVectorToJSON((*(userDB.find(toUserId))).second);
            const auto& replies = (*it2).second;
            const auto  replyNum = replies.size();
            const auto  score = calcRepliesEmotionScore(dictionary, replies);
            analysis_of_user[score] = {
                    userNames,
                    toUserNames,
                    boost::lexical_cast<string>(replyNum),
                    stringVectorToJSON(replies)};
        }
        analysis.push_back(analysis_of_user);
    }
    return analysis;
}

void writeAnalysis(
        const std::vector<std::map<int, std::vector<std::string> > >& analysis,
        const std::string& analysisFile) {
    using namespace std;
    ofstream ofs(analysisFile.c_str());
    for(const auto& line : analysis) {
        for(map<int, vector<string> >::const_iterator it = line.begin(); it != line.end(); ++it) {
            const auto& key   = (*it).first;
            const auto& value = (*it).second;
            ofs << value[0] << "\t"
                << value[1] << "\t"
                << value[2] << "\t"
                << key      << "\t"
                << value[3] << "\n";
        }
    }
}

int main() {
    const auto replyDB    = loadReplyDB("data/replyDB.tsv");
    const auto userDB     = loadUserDB("data/userDB.tsv");
    const auto dictionary = loadDictionary("settings/pn_ja.dic.utf8.lf");
    const auto analysis   = analyzeReplies(replyDB, userDB, dictionary);
    writeAnalysis(analysis, "data/analysis.tsv");
    return 0;
}
