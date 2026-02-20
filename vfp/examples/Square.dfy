method SquareRoot(n: nat)
returns (r: nat)
ensures r*r <= n <= (r+1)*(r+1)
{
    r := 0;
    while (r+1)*(r+1) <= n
    invariant r*r <= n
    {
        r := r + 1;
    }
}