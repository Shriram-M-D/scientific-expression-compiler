#ifndef EVALUATOR_H
#define EVALUATOR_H

#include <memory>
#include <unordered_map>
#include <string>
#include <vector>
#include "ast.h"
#include "calculus.h"

class Evaluator {
private:
    std::unordered_map<std::string, double> variables;
    std::vector<std::string> intermediateCode;
    int tempCounter;
    
    double evaluateNode(std::shared_ptr<ASTNode> node);
    std::string newTemp();
    
public:
    Evaluator();
    
    void setVariable(const std::string& name, double value);
    double getVariable(const std::string& name);
    bool hasVariable(const std::string& name);
    
    double evaluate(std::shared_ptr<ASTNode> ast);
    std::string generateIntermediateCode(std::shared_ptr<ASTNode> node);
    std::vector<std::string> getIntermediateCode();
    void clearIntermediateCode();
    
    // Helper functions
    static double factorial(double n);
};

#endif // EVALUATOR_H
