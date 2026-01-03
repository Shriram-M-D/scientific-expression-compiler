#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <sstream>
#include "lexer.h"
#include "parser.h"
#include "ast.h"
#include "evaluator.h"
#include "calculus.h"

// JSON helper functions
std::string escapeJSON(const std::string& str) {
    std::string result;
    for (char c : str) {
        switch (c) {
            case '"': result += "\\\""; break;
            case '\\': result += "\\\\"; break;
            case '\n': result += "\\n"; break;
            case '\r': result += "\\r"; break;
            case '\t': result += "\\t"; break;
            default: result += c;
        }
    }
    return result;
}

std::string tokensToJSON(const std::vector<Token>& tokens) {
    std::ostringstream json;
    json << "[";
    for (size_t i = 0; i < tokens.size(); i++) {
        if (i > 0) json << ",";
        json << "{\"type\":\"" << Lexer::tokenTypeToString(tokens[i].type) << "\",";
        json << "\"value\":\"" << escapeJSON(tokens[i].value) << "\"";
        if (tokens[i].type == TokenType::NUMBER || tokens[i].type == TokenType::CONSTANT) {
            json << ",\"numValue\":" << tokens[i].numValue;
        }
        json << "}";
    }
    json << "]";
    return json.str();
}

std::string astToJSON(std::shared_ptr<ASTNode> node) {
    if (!node) return "null";
    
    std::ostringstream json;
    json << "{";
    
    switch (node->type) {
        case ASTNodeType::NUMBER: {
            auto numNode = std::dynamic_pointer_cast<NumberNode>(node);
            json << "\"type\":\"NUMBER\",\"value\":" << numNode->value;
            break;
        }
        case ASTNodeType::VARIABLE: {
            auto varNode = std::dynamic_pointer_cast<VariableNode>(node);
            json << "\"type\":\"VARIABLE\",\"name\":\"" << varNode->name << "\"";
            break;
        }
        case ASTNodeType::BINARY_OP: {
            auto binNode = std::dynamic_pointer_cast<BinaryOpNode>(node);
            json << "\"type\":\"BINARY_OP\",\"op\":\"" << escapeJSON(binNode->op) << "\",";
            json << "\"left\":" << astToJSON(binNode->left) << ",";
            json << "\"right\":" << astToJSON(binNode->right);
            break;
        }
        case ASTNodeType::UNARY_OP: {
            auto unaryNode = std::dynamic_pointer_cast<UnaryOpNode>(node);
            json << "\"type\":\"UNARY_OP\",\"op\":\"" << escapeJSON(unaryNode->op) << "\",";
            json << "\"operand\":" << astToJSON(unaryNode->operand);
            break;
        }
        case ASTNodeType::FUNCTION_CALL: {
            auto funcNode = std::dynamic_pointer_cast<FunctionCallNode>(node);
            json << "\"type\":\"FUNCTION_CALL\",\"name\":\"" << funcNode->name << "\",";
            json << "\"arguments\":[";
            for (size_t i = 0; i < funcNode->arguments.size(); i++) {
                if (i > 0) json << ",";
                json << astToJSON(funcNode->arguments[i]);
            }
            json << "]";
            break;
        }
        case ASTNodeType::DIFF_NODE: {
            auto diffNode = std::dynamic_pointer_cast<DiffNode>(node);
            json << "\"type\":\"DIFF_NODE\",\"variable\":\"" << diffNode->variable << "\",";
            json << "\"point\":" << diffNode->point << ",";
            json << "\"expression\":" << astToJSON(diffNode->expression);
            break;
        }
        case ASTNodeType::INTEGRATE_NODE: {
            auto intNode = std::dynamic_pointer_cast<IntegrateNode>(node);
            json << "\"type\":\"INTEGRATE_NODE\",\"variable\":\"" << intNode->variable << "\",";
            json << "\"lowerBound\":" << intNode->lowerBound << ",";
            json << "\"upperBound\":" << intNode->upperBound << ",";
            json << "\"expression\":" << astToJSON(intNode->expression);
            break;
        }
    }
    
    json << "}";
    return json.str();
}

std::string intermediateCodeToJSON(const std::vector<std::string>& code) {
    std::ostringstream json;
    json << "[";
    for (size_t i = 0; i < code.size(); i++) {
        if (i > 0) json << ",";
        json << "\"" << escapeJSON(code[i]) << "\"";
    }
    json << "]";
    return json.str();
}

std::string calculusStepsToJSON(const std::vector<CalculusStep>& steps) {
    std::ostringstream json;
    json << "[";
    for (size_t i = 0; i < steps.size(); i++) {
        if (i > 0) json << ",";
        json << "{\"x\":" << steps[i].x << ",";
        json << "\"fx\":" << steps[i].fx << ",";
        json << "\"description\":\"" << escapeJSON(steps[i].description) << "\"}";
    }
    json << "]";
    return json.str();
}

int main(int argc, char* argv[]) {
    try {
        // Read input expression
        std::string expression;
        if (argc > 1) {
            expression = argv[1];
        } else {
            std::getline(std::cin, expression);
        }
        
        if (expression.empty()) {
            std::cerr << "{\"error\":\"Empty expression\"}" << std::endl;
            return 1;
        }
        
        // Lexical Analysis
        Lexer lexer(expression);
        std::vector<Token> tokens = lexer.tokenize();
        
        // Parsing
        Parser parser(tokens);
        std::shared_ptr<ASTNode> ast = parser.parse();
        
        // Intermediate Code Generation
        Evaluator evaluator;
        evaluator.clearIntermediateCode();
        evaluator.generateIntermediateCode(ast);
        std::vector<std::string> intermediateCode = evaluator.getIntermediateCode();
        
        // Evaluation
        double result = evaluator.evaluate(ast);
        
        // Check for calculus operations and get steps
        std::vector<CalculusStep> calculusSteps;
        std::string calculusType = "none";
        
        if (ast->type == ASTNodeType::DIFF_NODE) {
            auto diffNode = std::dynamic_pointer_cast<DiffNode>(ast);
            calculusType = "differentiation";
            Calculus::differentiate(
                diffNode->expression, 
                diffNode->variable, 
                diffNode->point, 
                &evaluator, 
                calculusSteps
            );
        } else if (ast->type == ASTNodeType::INTEGRATE_NODE) {
            auto intNode = std::dynamic_pointer_cast<IntegrateNode>(ast);
            calculusType = "integration";
            Calculus::integrateTrapezoid(
                intNode->expression, 
                intNode->variable, 
                intNode->lowerBound, 
                intNode->upperBound, 
                &evaluator, 
                calculusSteps
            );
        }
        
        // Generate JSON output
        std::cout << "{";
        std::cout << "\"success\":true,";
        std::cout << "\"expression\":\"" << escapeJSON(expression) << "\",";
        std::cout << "\"tokens\":" << tokensToJSON(tokens) << ",";
        std::cout << "\"postfix\":" << tokensToJSON(parser.postfixTokens) << ",";
        std::cout << "\"operatorStack\":[";
        for (size_t i = 0; i < parser.operatorStack.size(); i++) {
            if (i > 0) std::cout << ",";
            std::cout << "\"" << escapeJSON(parser.operatorStack[i]) << "\"";
        }
        std::cout << "],";
        std::cout << "\"ast\":" << astToJSON(ast) << ",";
        std::cout << "\"intermediateCode\":" << intermediateCodeToJSON(intermediateCode) << ",";
        std::cout << "\"result\":" << result << ",";
        std::cout << "\"calculusType\":\"" << calculusType << "\",";
        std::cout << "\"calculusSteps\":" << calculusStepsToJSON(calculusSteps);
        std::cout << "}" << std::endl;
        
        return 0;
        
    } catch (const std::exception& e) {
        std::cerr << "{\"success\":false,\"error\":\"" << escapeJSON(e.what()) << "\"}" << std::endl;
        return 1;
    }
}
