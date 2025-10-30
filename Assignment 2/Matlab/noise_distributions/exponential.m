function pdf = exponential(mu, var)
    arguments
        mu = 0
        var = 1  % mean is 1/lambda, variance is mean^2
    end
    sign = randi([0, 1])*2-1;
    pdf = mu + sign*exprnd(sqrt(var/2)); % divide by 2 because of symmetric distribution
end

%{
a = 
c = 0
v = zeros(1000,1);
for i= 1:1000
    v(i) = poisson(0, 0.1, 0.1);
end
b = a/i
c/i
%}