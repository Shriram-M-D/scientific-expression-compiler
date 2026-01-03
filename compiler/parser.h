#ifndef PARSER_H
#define PARSER_H

#include <vector>
#include <stack>
#include <memory>
#include "lexer.h"
#include "ast.h"

// Parser using Shunting Yard Algorithm
class Parser {
private:
    std::vector<Token> tokens;
    size_t position;
    
    Token currentToken();
    Token peek(int offset = 1);
    void advance();
    bool isOperator(const Token& token);
    bool isFunction(const Token& token);
    
    std::shared_ptr<ASTNode> parseExpression();
    std::shared_ptr<ASTNode> parsePrimary();
    std::vector<std::shared_ptr<ASTNode>> parseArguments();
    
    // Shunting Yard conversion
    std::vector<Token> infixToPostfix();
    std::shared_ptr<ASTNode> buildASTFromPostfix(const std::vector<Token>& postfix);
    
public:
    std::vector<Token> postfixTokens;
    std::vector<std::string> operatorStack;
    
    Parser(const std::vector<Token>& tokens);
    std::shared_ptr<ASTNode> parse();
};

#endif // PARSER_H
