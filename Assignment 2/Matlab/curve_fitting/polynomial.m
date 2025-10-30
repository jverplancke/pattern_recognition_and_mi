function y = polynomial(x, coeffs)
    y = zeros(length(x), 1);
    for i = 0:length(coeffs)-1
        y = y + coeffs(i + 1) * x.^i;
    end
end
