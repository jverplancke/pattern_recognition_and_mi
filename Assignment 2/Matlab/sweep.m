function [errors, ms, n_samples] = sweep(k, ds, phase, lambda, pdf)
    arguments
        k
        ds
        phase=0
        lambda=0  % default is no regularisation
        pdf=@() gaussian(0, 1)
    end

    x = (0:ds:2*pi*k).' + phase;
    y = 1 + sin(x);

    [x_s, min_x, range_x] = scale(x);  % prevent A from blowing up
    
    geom_step = 1.01;
    sample_spacings = unique(fix(geom_step.^(1:log(length(x))/log(geom_step))));  % order
    n_samples = unique(ceil(length(x)./sample_spacings));
    sample_spacings = unique(ceil(length(x)./n_samples));
    n_samples = ceil(length(x)./sample_spacings);  % update with unique values
    % select by number of unique sample points
    
    ms = 1:n_samples(1);
    
    errors = NaN(length(n_samples), length(ms));
    
    rng(37302)  % for reproducibility
    noise = generate_noise(x, pdf);
    y = y + noise;
    
    for i = 1:length(sample_spacings)
        n = sample_spacings(i);
        % subsample x and y here
        x_subsampled = x_s(1:n:end);
        y_subsampled = y(1:n:end);
        for j = 1:length(ms)
            m = ms(j);
            
            if m >= length(x_subsampled)
               break
            end
            w = coefficients(x_subsampled, y_subsampled, m, lambda);
            
            % fit around sample points
            fit = polynomial(x_s, w);
            
            errors(i, j) = rms_error(fit, y);
        end
    end
end