function make_plot(errors, ms, n_samples, axtitle)
    [x_p, y_p] = meshgrid(ms, n_samples);
    %subplot(2,2,p);
    img = contourf(x_p, y_p, errors, 0:0.001:1, 'LineStyle','none');
    
    clim([0 1])
    colormap(turbo)
    colorbar
    
    % annotation
    xlabel("Polynomial order M")
    ylabel("Sample points N")
    
    set(gca,{'XScale','YScale'},{'log','log'});
    xlim([1 ms(end)]);
    ylim([1 y_p(1, 1)]);
    axis on
    axis equal
    
    title(axtitle);
end