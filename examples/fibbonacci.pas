program Ololo;
var
    a, b : integer;
    c : boolean;
    d, e, f: real;
    i : integer;
begin
    a := 1;
    b := 1;
    d := 10000.0 / 10.0;
    e := -1000.0;
    {c := false;}
    i := 0;
    while (b <= 10000) do 
    begin
        b := a + b;
        a := b - a;
        f := b / a;
        if (d > f) then
            d := f;
        if (e < f) then
            e := f;
        if ((f - 1.618 < 0.001) or (f - 1.618 > 0.001)) then
            c := true;
        i := i + 1;
        writeln('Fibbonacci pair #', i, ' is ', a, ' ', b, ' and its ratio is ', f, ', log(a) = ', ln(a), ', log(phi ^ ', i - 1, ') = ', (i + 1) * ln((1 + sqrt(5)) / 2) - 0.5 * ln(5));

    end

end.
