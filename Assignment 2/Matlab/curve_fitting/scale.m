function [r, min_x, range_x] = scale(x)
    min_x = min(x);
    range_x = max(x)-min_x;
    %r = (x - mean(x))/std(x);
    r = 2*(x - min_x)/range_x - 1;
end