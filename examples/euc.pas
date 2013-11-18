program Euc;
var
    a, b, t: integer;
begin
    a := readint();
    b := readint();
    if (a < b) then
    begin
        t := a;
        a := b;
        b := t;
    end

    while (b > 0) do
    begin
        writeln('a = ', a, ', b = ', b);
        a := a - b;
        if (a < b) then
        begin
            t := a;
            a := b;
            b := t;
        end
    end
    writeln('GCD is ', a);
    { here is a commentary:
    writeln('41 / 17 = ', 41 / 17, ' or ', real_to_int(41 / 17)); 
    }
end
