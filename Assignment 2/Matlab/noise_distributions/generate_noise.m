function noise = generate_noise(x, pdf)
    noise = zeros(length(x), 1);

    for i = 1:length(x)
        if isa(pdf, 'string') & pdf == "Poisson"
            noise(i) = poisson(0, x(i), 100);  % scale x by 100
        else
            noise(i) = feval(pdf);
        end
    end
end