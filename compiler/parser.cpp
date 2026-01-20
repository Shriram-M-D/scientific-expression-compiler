#include "parser.h"
#include "evaluator.h"
#include <stdexcept>
#include <algorithm>

Parser::Parser(const std::vector<Token>& tokens) : tokens(tokens), position(0) {}

Token Parser::currentToken() {
    if (position >= tokens.size()) {
        return Token(TokenType::END, "");
    }
    return tokens[position];
}

Token Parser::peek(int offset) {
    size_t pos = position + offset;
    if (pos >= tokens.size()) {
        return Token(TokenType::END, "");
    }
    return tokens[pos];
}

void Parser::advance() {
    position++;
}

bool Parser::isOperator(const Token& token) {
    return token.type == TokenType::PLUS ||
           token.type == TokenType::MINUS ||
           token.type == TokenType::MULTIPLY ||
           token.type == TokenType::DIVIDE ||
           token.type == TokenType::MODULO ||
           token.type == TokenType::POWER ||
           token.type == TokenType::FACTORIAL;
}

bool Parser::isFunction(const Token& token) {
    return token.type == TokenType::FUNCTION;
}

std::vector<Token> Parser::infixToPostfix() {
    std::vector<Token> output;
    std::stack<Token> opStack;
    operatorStack.clear();
    
    position = 0;
    bool expectOperand = true;
    
    while (currentToken().type != TokenType::END) {
        Token token = currentToken();
        
        if (token.type == TokenType::NUMBER || token.type == TokenType::CONSTANT) {
            output.push_back(token);
            expectOperand = false;
            advance();
        }
        else if (token.type == TokenType::VARIABLE) {
            output.push_back(token);
            expectOperand = false;
            advance();
        }
        else if (token.type == TokenType::FUNCTION) {
            opStack.push(token);
            operatorStack.push_back(token.value);
            advance();
        }
        else if (token.type == TokenType::COMMA) {
            while (!opStack.empty() && opStack.top().type != TokenType::LPAREN) {
                output.push_back(opStack.top());
                opStack.pop();
            }
            advance();
        }
        else if (token.type == TokenType::MINUS && expectOperand) {
            // Unary minus
            Token unaryMinus(TokenType::FUNCTION, "neg");
            opStack.push(unaryMinus);
            operatorStack.push_back("neg");
            advance();
        }
        else if (isOperator(token)) {
            while (!opStack.empty() && isOperator(opStack.top())) {
                Token top = opStack.top();
                if ((token.rightAssociative && token.precedence < top.precedence) ||
                    (!token.rightAssociative && token.precedence <= top.precedence)) {
                    output.push_back(top);
                    opStack.pop();
                } else {
                    break;
                }
            }
            opStack.push(token);
            operatorStack.push_back(token.value);
            expectOperand = true;
            advance();
        }
        else if (token.type == TokenType::LPAREN) {
            opStack.push(token);
            expectOperand = true;
            advance();
        }
        else if (token.type == TokenType::RPAREN) {
            while (!opStack.empty() && opStack.top().type != TokenType::LPAREN) {
                output.push_back(opStack.top());
                opStack.pop();
            }
            if (!opStack.empty() && opStack.top().type == TokenType::LPAREN) {
                opStack.pop();
            }
            if (!opStack.empty() && opStack.top().type == TokenType::FUNCTION) {
                output.push_back(opStack.top());
                opStack.pop();
            }
            expectOperand = false;
            advance();
        }
        else {
            advance();
        }
    }
    
    while (!opStack.empty()) {
        if (opStack.top().type == TokenType::LPAREN || 
            opStack.top().type == TokenType::RPAREN) {
            throw std::runtime_error("Mismatched parentheses");
        }
        output.push_back(opStack.top());
        opStack.pop();
    }
    
    postfixTokens = output;
    return output;
}

std::shared_ptr<ASTNode> Parser::buildASTFromPostfix(const std::vector<Token>& postfix) {
    std::stack<std::shared_ptr<ASTNode>> nodeStack;
    
    for (const Token& token : postfix) {
        if (token.type == TokenType::NUMBER) {
            nodeStack.push(std::make_shared<NumberNode>(token.numValue));
        }
        else if (token.type == TokenType::CONSTANT) {
            nodeStack.push(std::make_shared<NumberNode>(token.numValue));
        }
        else if (token.type == TokenType::VARIABLE) {
            nodeStack.push(std::make_shared<VariableNode>(token.value));
        }
        else if (token.type == TokenType::FUNCTION) {
            // Special handling for multi-argument functions
            if (token.value == "diff") {
                if (nodeStack.size() < 3) {
                    throw std::runtime_error("diff requires 3 arguments");
                }
                auto point = nodeStack.top(); nodeStack.pop();
                auto var = nodeStack.top(); nodeStack.pop();
                auto expr = nodeStack.top(); nodeStack.pop();
                
                if (var->type != ASTNodeType::VARIABLE) {
                    throw std::runtime_error("diff second argument must be a variable");
                }
                // Allow point to be any expression - will be evaluated
                
                auto varNode = std::dynamic_pointer_cast<VariableNode>(var);
                
                // Evaluate the point expression to get the numeric value
                Evaluator evalPoint;
                double pointValue = evalPoint.evaluate(point);
                
                nodeStack.push(std::make_shared<DiffNode>(
                    expr, varNode->name, pointValue));
            }
            else if (token.value == "integrate") {
                if (nodeStack.size() < 4) {
                    throw std::runtime_error("integrate requires 4 arguments");
                }
                auto upper = nodeStack.top(); nodeStack.pop();
                auto lower = nodeStack.top(); nodeStack.pop();
                auto var = nodeStack.top(); nodeStack.pop();
                auto expr = nodeStack.top(); nodeStack.pop();
                
                if (var->type != ASTNodeType::VARIABLE) {
                    throw std::runtime_error("integrate second argument must be a variable");
                }
                // Allow bounds to be any expression - will be evaluated
                
                auto varNode = std::dynamic_pointer_cast<VariableNode>(var);
                
                // Evaluate the bound expressions to get numeric values
                Evaluator evalBounds;
                double lowerValue = evalBounds.evaluate(lower);
                double upperValue = evalBounds.evaluate(upper);
                
                nodeStack.push(std::make_shared<IntegrateNode>(
                    expr, varNode->name, lowerValue, upperValue));
            }
            else if (token.value == "nCr") {
                if (nodeStack.size() < 2) {
                    throw std::runtime_error("nCr requires 2 arguments");
                }
                auto r = nodeStack.top(); nodeStack.pop();
                auto n = nodeStack.top(); nodeStack.pop();
                
                nodeStack.push(std::make_shared<NCrNode>(n, r));
            }
            else if (token.value == "nPr") {
                if (nodeStack.size() < 2) {
                    throw std::runtime_error("nPr requires 2 arguments");
                }
                auto r = nodeStack.top(); nodeStack.pop();
                auto n = nodeStack.top(); nodeStack.pop();
                
                nodeStack.push(std::make_shared<NPrNode>(n, r));
            }
            else if (token.value == "neg") {
                if (nodeStack.empty()) {
                    throw std::runtime_error("Unary minus requires an operand");
                }
                auto operand = nodeStack.top();
                nodeStack.pop();
                nodeStack.push(std::make_shared<UnaryOpNode>("neg", operand));
            }
            else {
                // Regular function
                if (nodeStack.empty()) {
                    throw std::runtime_error("Function requires an argument");
                }
                auto arg = nodeStack.top();
                nodeStack.pop();
                
                auto funcNode = std::make_shared<FunctionCallNode>(token.value);
                funcNode->arguments.push_back(arg);
                nodeStack.push(funcNode);
            }
        }
        else if (token.type == TokenType::FACTORIAL) {
            if (nodeStack.empty()) {
                throw std::runtime_error("Factorial requires an operand");
            }
            auto operand = nodeStack.top();
            nodeStack.pop();
            nodeStack.push(std::make_shared<FactorialNode>(operand));
        }
        else if (isOperator(token)) {
            if (nodeStack.size() < 2) {
                throw std::runtime_error("Binary operator requires two operands");
            }
            auto right = nodeStack.top();
            nodeStack.pop();
            auto left = nodeStack.top();
            nodeStack.pop();
            nodeStack.push(std::make_shared<BinaryOpNode>(token.value, left, right));
        }
    }
    
    if (nodeStack.size() != 1) {
        throw std::runtime_error("Invalid expression");
    }
    
    return nodeStack.top();
}

std::shared_ptr<ASTNode> Parser::parse() {
    auto postfix = infixToPostfix();
    return buildASTFromPostfix(postfix);
}
