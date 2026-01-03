#ifndef CALCULUS_H
#define CALCULUS_H

#include <memory>
#include <vector>
#include <string>
#include "ast.h"

class Evaluator; // Forward declaration

struct CalculusStep {
    double x;
    double fx;
    std::string description;
};

class Calculus {
private:
    static const double EPSILON; // Step size for numerical methods
    
public:
    // Numerical Differentiation using Central Finite Difference
    static double differentiate(
        std::shared_ptr<ASTNode> expr,
        const std::string& variable,
        double point,
        Evaluator* evaluator,
        std::vector<CalculusStep>& steps
    );
    
    // Numerical Integration using Trapezoidal Rule
    static double integrateTrapezoid(
        std::shared_ptr<ASTNode> expr,
        const std::string& variable,
        double lowerBound,
        double upperBound,
        Evaluator* evaluator,
        std::vector<CalculusStep>& steps,
        int numSteps = 1000
    );
    
    // Numerical Integration using Simpson's Rule
    static double integrateSimpson(
        std::shared_ptr<ASTNode> expr,
        const std::string& variable,
        double lowerBound,
        double upperBound,
        Evaluator* evaluator,
        std::vector<CalculusStep>& steps,
        int numSteps = 1000
    );
};

#endif // CALCULUS_H
