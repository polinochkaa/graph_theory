n = int(input())
a = [int(i) for i in input().split()]
l = a.index(min(a))
r = n-a[::-1].index(max(a))-1
if l > r:
    l, r = r, l
print(l,r)
a[l:r+1] = a[r+1:l:-1]
print(*a)