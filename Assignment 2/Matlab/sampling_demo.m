x = (0:2*pi/50:2*pi*2).';
y = 1+sin(x);

noise = generate_noise(x, @() gaussian(0, 0.1));
y_noise = y + noise;
subsampling = 5;

x_sub = x(1:subsampling:end);
y_sub = y(1:subsampling:end);
noise_sub = noise(1:subsampling:end);
y_noise_sub = y_noise(1:subsampling:end);

subplot(3, 1, 1);
plot(x, y, '-o')
hold on
%scatter(x_sub, y_sub, 'o')
subplot(3, 1, 2);
plot(x, noise);
hold on
%scatter(x_sub, noise_sub, 'o')
subplot(3, 1, 3);
hold on
plot(x_sub, y_noise_sub)
%plot(x_sub, y_noise_sub)