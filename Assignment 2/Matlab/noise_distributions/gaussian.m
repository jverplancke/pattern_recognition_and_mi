function pdf = gaussian(mu, sigma)
    arguments
        mu=0
        sigma=1
    end

    pdf = sigma*randn + mu;
end

% use as pdf = @() gaussian(mu, sigma)
%feval(pdf)