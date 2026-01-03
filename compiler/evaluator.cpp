#include "evaluator.h"
#include <cmath>
#include <stdexcept>
#include <sstream>

Evaluator::Evaluator() : tempCounter(0) {}

void Evaluator::setVariable(const std::string& name, double value) {
    variables[name] = value;
}

double Evaluator::getVariable(const std::string& name) {
    if (variables.find(name) == variables.end()) {
        throw std::runtime_error("Undefined variable: " + name);
    }
    return variables[name];
}

bool Evaluator::hasVariable(const std::string& name) {
    return variables.find(name) != variables.end();
}

std::string Evaluator::newTemp() {
    return "t" + std::to_string(tempCounter++);
}

double Evaluator::factorial(double n) {
    if (n < 0 || n != std::floor(n)) {
        throw std::runtime_error("Factorial requires non-negative integer");
    }
    if (n > 170) {
        throw std::runtime_error("Factorial overflow");
    }
    double result = 1.0;
    for (int i = 2; i <= static_cast<int>(n); i++) {
        result *= i;
    }
    return result;
}

std::string Evaluator::generateIntermediateCode(std::shared_ptr<ASTNode> node) {
    std::ostringstream code;
    
    switch (node->type) {
        case ASTNodeType::NUMBER: {
            auto numNode = std::dynamic_pointer_cast<NumberNode>(node);
            std::string temp = newTemp();
            code << temp << " = " << numNode->value;
            intermediateCode.push_back(code.str());
            return temp;
        }
        
        case ASTNodeType::VARIABLE: {
            auto varNode = std::dynamic_pointer_cast<VariableNode>(node);
            std::string temp = newTemp();
            code << temp << " = " << varNode->name;
            intermediateCode.push_back(code.str());
            return temp;
        }
        
        case ASTNodeType::BINARY_OP: {
            auto binNode = std::dynamic_pointer_cast<BinaryOpNode>(node);
            std::string left = generateIntermediateCode(binNode->left);
            std::string right = generateIntermediateCode(binNode->right);
            std::string temp = newTemp();
            code << temp << " = " << left << " " << binNode->op << " " << right;
            intermediateCode.push_back(code.str());
            return temp;
        }
        
        case ASTNodeType::UNARY_OP: {
            auto unaryNode = std::dynamic_pointer_cast<UnaryOpNode>(node);
            std::string operand = generateIntermediateCode(unaryNode->operand);
            std::string temp = newTemp();
            code << temp << " = " << unaryNode->op << " " << operand;
            intermediateCode.push_back(code.str());
            return temp;
        }
        
        case ASTNodeType::FUNCTION_CALL: {
            auto funcNode = std::dynamic_pointer_cast<FunctionCallNode>(node);
            std::string arg = generateIntermediateCode(funcNode->arguments[0]);
            std::string temp = newTemp();
            code << temp << " = " << funcNode->name << "(" << arg << ")";
            intermediateCode.push_back(code.str());
            return temp;
        }
        
        case ASTNodeType::DIFF_NODE: {
            auto diffNode = std::dynamic_pointer_cast<DiffNode>(node);
            std::string temp = newTemp();
            code << temp << " = diff(" << diffNode->expression->toString() 
                 << ", " << diffNode->variable << ", " << diffNode->point << ")";
            intermediateCode.push_back(code.str());
            return temp;
        }
        
        case ASTNodeType::INTEGRATE_NODE: {
            auto intNode = std::dynamic_pointer_cast<IntegrateNode>(node);
            std::string temp = newTemp();
            code << temp << " = integrate(" << intNode->expression->toString() 
                 << ", " << intNode->variable << ", " << intNode->lowerBound 
                 << ", " << intNode->upperBound << ")";
            intermediateCode.push_back(code.str());
            return temp;
        }
        
        default:
            throw std::runtime_error("Unknown node type in code generation");
    }
}

double Evaluator::evaluateNode(std::shared_ptr<ASTNode> node) {
    switch (node->type) {
        case ASTNodeType::NUMBER: {
            auto numNode = std::dynamic_pointer_cast<NumberNode>(node);
            return numNode->value;
        }
        
        case ASTNodeType::VARIABLE: {
            auto varNode = std::dynamic_pointer_cast<VariableNode>(node);
            return getVariable(varNode->name);
        }
        
        case ASTNodeType::BINARY_OP: {
            auto binNode = std::dynamic_pointer_cast<BinaryOpNode>(node);
            double left = evaluateNode(binNode->left);
            double right = evaluateNode(binNode->right);
            
            if (binNode->op == "+") return left + right;
            if (binNode->op == "-") return left - right;
            if (binNode->op == "*") return left * right;
            if (binNode->op == "/") {
                if (right == 0.0) throw std::runtime_error("Division by zero");
                return left / right;
            }
            if (binNode->op == "%") {
                if (right == 0.0) throw std::runtime_error("Modulo by zero");
                return std::fmod(left, right);
            }
            if (binNode->op == "^") return std::pow(left, right);
            
            throw std::runtime_error("Unknown binary operator: " + binNode->op);
        }
        
        case ASTNodeType::UNARY_OP: {
            auto unaryNode = std::dynamic_pointer_cast<UnaryOpNode>(node);
            double operand = evaluateNode(unaryNode->operand);
            
            if (unaryNode->op == "neg") return -operand;
            if (unaryNode->op == "!") return factorial(operand);
            
            throw std::runtime_error("Unknown unary operator: " + unaryNode->op);
        }
        
        case ASTNodeType::FUNCTION_CALL: {
            auto funcNode = std::dynamic_pointer_cast<FunctionCallNode>(node);
            double arg = evaluateNode(funcNode->arguments[0]);
            
            if (funcNode->name == "sin") return std::sin(arg);
            if (funcNode->name == "cos") return std::cos(arg);
            if (funcNode->name == "tan") return std::tan(arg);
            if (funcNode->name == "asin") {
                if (arg < -1.0 || arg > 1.0) 
                    throw std::runtime_error("asin domain error");
                return std::asin(arg);
            }
            if (funcNode->name == "acos") {
                if (arg < -1.0 || arg > 1.0) 
                    throw std::runtime_error("acos domain error");
                return std::acos(arg);
            }
            if (funcNode->name == "atan") return std::atan(arg);
            if (funcNode->name == "log") {
                if (arg <= 0.0) throw std::runtime_error("log domain error");
                return std::log10(arg);
            }
            if (funcNode->name == "ln") {
                if (arg <= 0.0) throw std::runtime_error("ln domain error");
                return std::log(arg);
            }
            if (funcNode->name == "exp") return std::exp(arg);
            if (funcNode->name == "sqrt") {
                if (arg < 0.0) throw std::runtime_error("sqrt domain error");
                return std::sqrt(arg);
            }
            if (funcNode->name == "cbrt") return std::cbrt(arg);
            if (funcNode->name == "abs") return std::abs(arg);
            
            throw std::runtime_error("Unknown function: " + funcNode->name);
        }
        
        case ASTNodeType::DIFF_NODE: {
            auto diffNode = std::dynamic_pointer_cast<DiffNode>(node);
            std::vector<CalculusStep> steps;
            return Calculus::differentiate(
                diffNode->expression, 
                diffNode->variable, 
                diffNode->point, 
                this, 
                steps
            );
        }
        
        case ASTNodeType::INTEGRATE_NODE: {
            auto intNode = std::dynamic_pointer_cast<IntegrateNode>(node);
            std::vector<CalculusStep> steps;
            return Calculus::integrateTrapezoid(
                intNode->expression, 
                intNode->variable, 
                intNode->lowerBound, 
                intNode->upperBound, 
                this, 
                steps
            );
        }
        
        default:
            throw std::runtime_error("Unknown node type");
    }
}

double Evaluator::evaluate(std::shared_ptr<ASTNode> ast) {
    return evaluateNode(ast);
}

std::vector<std::string> Evaluator::getIntermediateCode() {
    return intermediateCode;
}

void Evaluator::clearIntermediateCode() {
    intermediateCode.clear();
    tempCounter = 0;
}
