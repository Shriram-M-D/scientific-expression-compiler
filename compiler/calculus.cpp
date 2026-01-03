#include "calculus.h"
#include "evaluator.h"
#include <cmath>
#include <sstream>

const double Calculus::EPSILON = 0.0001;

double Calculus::differentiate(
    std::shared_ptr<ASTNode> expr,
    const std::string& variable,
    double point,
    Evaluator* evaluator,
    std::vector<CalculusStep>& steps
) {
    steps.clear();
    
    double h = EPSILON;
    
    // Evaluate f(x + h)
    evaluator->setVariable(variable, point + h);
    double f_plus = evaluator->evaluate(expr);
    
    std::ostringstream oss1;
    oss1 << "f(" << point + h << ") = " << f_plus;
    steps.push_back({point + h, f_plus, oss1.str()});
    
    // Evaluate f(x - h)
    evaluator->setVariable(variable, point - h);
    double f_minus = evaluator->evaluate(expr);
    
    std::ostringstream oss2;
    oss2 << "f(" << point - h << ") = " << f_minus;
    steps.push_back({point - h, f_minus, oss2.str()});
    
    // Central finite difference: f'(x) ≈ [f(x+h) - f(x-h)] / (2h)
    double derivative = (f_plus - f_minus) / (2.0 * h);
    
    std::ostringstream oss3;
    oss3 << "f'(" << point << ") ≈ [" << f_plus << " - " << f_minus 
         << "] / " << (2.0 * h) << " = " << derivative;
    steps.push_back({point, derivative, oss3.str()});
    
    return derivative;
}

double Calculus::integrateTrapezoid(
    std::shared_ptr<ASTNode> expr,
    const std::string& variable,
    double lowerBound,
    double upperBound,
    Evaluator* evaluator,
    std::vector<CalculusStep>& steps,
    int numSteps
) {
    steps.clear();
    
    double h = (upperBound - lowerBound) / numSteps;
    double sum = 0.0;
    
    // Evaluate at lower bound
    evaluator->setVariable(variable, lowerBound);
    double f_lower = evaluator->evaluate(expr);
    sum += f_lower;
    
    std::ostringstream oss1;
    oss1 << "f(" << lowerBound << ") = " << f_lower;
    steps.push_back({lowerBound, f_lower, oss1.str()});
    
    // Evaluate at interior points
    for (int i = 1; i < numSteps; i++) {
        double x = lowerBound + i * h;
        evaluator->setVariable(variable, x);
        double fx = evaluator->evaluate(expr);
        sum += 2.0 * fx;
        
        // Only record some steps to avoid overwhelming output
        if (i < 5 || i == numSteps - 1) {
            std::ostringstream oss;
            oss << "f(" << x << ") = " << fx;
            steps.push_back({x, fx, oss.str()});
        }
    }
    
    // Evaluate at upper bound
    evaluator->setVariable(variable, upperBound);
    double f_upper = evaluator->evaluate(expr);
    sum += f_upper;
    
    std::ostringstream oss2;
    oss2 << "f(" << upperBound << ") = " << f_upper;
    steps.push_back({upperBound, f_upper, oss2.str()});
    
    // Trapezoidal rule: I ≈ (h/2)[f(a) + 2Σf(xi) + f(b)]
    double integral = (h / 2.0) * sum;
    
    std::ostringstream oss3;
    oss3 << "Integral ≈ (" << h << "/2) × " << sum << " = " << integral;
    steps.push_back({0, integral, oss3.str()});
    
    return integral;
}

double Calculus::integrateSimpson(
    std::shared_ptr<ASTNode> expr,
    const std::string& variable,
    double lowerBound,
    double upperBound,
    Evaluator* evaluator,
    std::vector<CalculusStep>& steps,
    int numSteps
) {
    steps.clear();
    
    // Simpson's rule requires even number of intervals
    if (numSteps % 2 != 0) numSteps++;
    
    double h = (upperBound - lowerBound) / numSteps;
    double sum = 0.0;
    
    // Evaluate at lower bound
    evaluator->setVariable(variable, lowerBound);
    double f_lower = evaluator->evaluate(expr);
    sum += f_lower;
    
    std::ostringstream oss1;
    oss1 << "f(" << lowerBound << ") = " << f_lower;
    steps.push_back({lowerBound, f_lower, oss1.str()});
    
    // Evaluate at interior points
    for (int i = 1; i < numSteps; i++) {
        double x = lowerBound + i * h;
        evaluator->setVariable(variable, x);
        double fx = evaluator->evaluate(expr);
        
        // Alternating coefficients: 4, 2, 4, 2, ...
        if (i % 2 == 0) {
            sum += 2.0 * fx;
        } else {
            sum += 4.0 * fx;
        }
        
        // Only record some steps
        if (i < 5 || i == numSteps - 1) {
            std::ostringstream oss;
            oss << "f(" << x << ") = " << fx;
            steps.push_back({x, fx, oss.str()});
        }
    }
    
    // Evaluate at upper bound
    evaluator->setVariable(variable, upperBound);
    double f_upper = evaluator->evaluate(expr);
    sum += f_upper;
    
    std::ostringstream oss2;
    oss2 << "f(" << upperBound << ") = " << f_upper;
    steps.push_back({upperBound, f_upper, oss2.str()});
    
    // Simpson's rule: I ≈ (h/3)[f(a) + 4Σf(odd) + 2Σf(even) + f(b)]
    double integral = (h / 3.0) * sum;
    
    std::ostringstream oss3;
    oss3 << "Integral ≈ (" << h << "/3) × " << sum << " = " << integral;
    steps.push_back({0, integral, oss3.str()});
    
    return integral;
}
