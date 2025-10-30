function w = coefficients(x, y, max_power, l)
    arguments
        x
        y
        max_power
        l=0  % default is no regularisation
    end

    T = zeros(max_power + 1, 1);
    A = zeros(max_power + 1, max_power + 1);

    % down and then across
    for i = 0:max_power
        x_pow = x.^i;
        T(i+1) = sum(y .* x_pow);
        a = sum(x_pow);
        for j = 0:i
            A(i-j+1, j+1) = a;
        end
    end
    for j = 1:max_power
        x_pow = x.^(max_power+j);
        a = sum(x_pow);
        for i = max_power+1:-1:j+1
            A(i, j+(max_power-i)+2) = a;
        end
    end
    
    % regularise
    A = A + l*eye(size(A));
    w = A \ T;
end