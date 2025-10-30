function pdf = poisson(offset, var, scaling)
    % Generates a random sample from a Poisson distribution which has been
    % shifted by offset.
    % The scaling parameter allows for intervals different from 1, i.e.
    % intervals are given by 1/scaling.
    % The expectation value lambda is the variance, for the purposes of
    % scaling we sample a Poisson distribution with mean = variance =
    % var/scaling, then scale those values back up and apply an offset.
    arguments
        offset=0
        var=1
        scaling=1
    end
    
    pdf = poissrnd(var*scaling)/scaling + offset;
end

% b - a = sqrt(12*var)
% b + a = 2*mu
% 2*mu - b = a
% 2b - 2mu = sqrt(12*var)
% b = mu + sqrt(3*var)
% a = mu - sqrt(3*var)

% use as pdf = @() gaussian(mu, sigma)
% feval(pdf)

%{
v = zeros(1000,1);
for i= 1:1000
    v(i) = poisson(0, 10, 0.1);
end
mean(v)
var(v)
%}