function pdf = uniform(mu, var)
    arguments
        mu=0
        var=1
    end
    a = mu - sqrt(3*var);
    b = mu + sqrt(3*var);
    pdf = rand*(b-a) + a;
end

% b - a = sqrt(12*var)
% b + a = 2*mu
% 2*mu - b = a
% 2b - 2mu = sqrt(12*var)
% b = mu + sqrt(3*var)
% a = mu - sqrt(3*var)

% use as pdf = @() gaussian(mu, sigma)
% feval(pdf)