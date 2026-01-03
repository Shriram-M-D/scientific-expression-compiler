#ifndef LEXER_H
#define LEXER_H

#include <string>
#include <vector>
#include <unordered_map>

// Token types for the lexical analyzer
enum class TokenType {
    NUMBER,
    PLUS, MINUS, MULTIPLY, DIVIDE, MODULO, POWER,
    LPAREN, RPAREN, COMMA,
    FACTORIAL,
    FUNCTION,
    CONSTANT,
    VARIABLE,
    END,
    INVALID
};

// Token structure
struct Token {
    TokenType type;
    std::string value;
    double numValue;
    int precedence;
    bool rightAssociative;
    
    Token(TokenType t = TokenType::INVALID, const std::string& v = "", double nv = 0.0)
        : type(t), value(v), numValue(nv), precedence(0), rightAssociative(false) {}
};

class Lexer {
private:
    std::string input;
    size_t position;
    std::unordered_map<std::string, TokenType> functions;
    std::unordered_map<std::string, double> constants;
    
    char currentChar();
    char peek(int offset = 1);
    void advance();
    void skipWhitespace();
    Token readNumber();
    Token readIdentifier();
    
public:
    Lexer(const std::string& input);
    std::vector<Token> tokenize();
    static std::string tokenTypeToString(TokenType type);
};

#endif // LEXER_H
