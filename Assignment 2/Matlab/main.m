clear;
addpath("curve_fitting")
addpath("noise_distributions")

% default values
P = 1;
ds = 2*pi/180;
phase = 0;
lambda = 1e-4;
pdf = @() gaussian(0, 0.1);

[errors, ms, n_samples] = sweep(P, ds, phase, 0, pdf);

% Baseline
figure
make_plot(errors, ms, n_samples, "Lambda = 0")
allAxesInFigure = findall(gcf,'type','axes');
linkaxes(allAxesInFigure)
drawnow()

% Variations:
% Regularisation penalty
lambdas = [1e-8 1e-4 1e-2 1];
figure
for i = 1:length(lambdas)
    subplot(2, 2, i)
    [errors, ms, n_samples] = sweep(P, ds, phase, lambdas(i), pdf);
    make_plot(errors, ms, n_samples, "Lambda = " + lambdas(i))
end
allAxesInFigure = findall(gcf,'type','axes');
linkaxes(allAxesInFigure)
drawnow()

% Number of periods
periods = [1 2 4 8];
figure
for i = 1:length(periods)
    subplot(2, 2, i)
    [errors, ms, n_samples] = sweep(periods(i), ds/2, phase, lambda, pdf);
    make_plot(errors, ms, n_samples, "Periods = " + periods(i))
end
allAxesInFigure = findall(gcf,'type','axes');
linkaxes(allAxesInFigure)
drawnow()

% Sample spacing
spacings = [40 10 2 0.5]*pi/90;
figure
for i = 1:length(spacings)
    subplot(2, 2, i)
    [errors, ms, n_samples] = sweep(P, spacings(i), phase, lambda, pdf);
    make_plot(errors, ms, n_samples, "Sample spacing = " + spacings(i)*180/pi + " degree(s)")
end
allAxesInFigure = findall(gcf,'type','axes');
linkaxes(allAxesInFigure)
drawnow()

% Noise variance
variances = [0.1 0.25 0.4 0.9];
figure
for i = 1:length(variances)
    pdf = @() gaussian(0, variances(i));
    subplot(2, 2, i)
    [errors, ms, n_samples] = sweep(P, ds, phase, lambda, pdf);
    make_plot(errors, ms, n_samples, "Variance = " + variances(i))
end
allAxesInFigure = findall(gcf,'type','axes');
linkaxes(allAxesInFigure)
drawnow()

% Noise distribution
noise_distribs = {
    @() gaussian(0, 0.5)
    @() uniform(0, 0.5)
    @() exponential(0, 0.5)};
noise_labels = ["Gaussian", "Uniform", "Exponential"];
figure
for i = 1:length(noise_distribs)
    pdf_i = noise_distribs{i};
    subplot(2, 2, i)
    [errors, ms, n_samples] = sweep(P, ds, phase, lambda, pdf_i);
    make_plot(errors, ms, n_samples, noise_labels(i))
end
subplot(2, 2, 4)
[errors, ms, n_samples] = sweep(P, ds, phase, lambda, "Poisson");
make_plot(errors, ms, n_samples, "Shot (Poisson)")
allAxesInFigure = findall(gcf,'type','axes');
linkaxes(allAxesInFigure)


