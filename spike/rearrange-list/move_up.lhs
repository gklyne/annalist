= List re-arrangement

'move_up' moves selected elements one place towards the head of a list.

'move_down' moves selected elements one place towards the tail of a list.

== Requirements

Given:

A list L = [ v1, v2, ... vn ]

and

A predicate P which applies to members of the list

Implement a function move_up(L, P) that returns new list L1, such that:

(a) the ordering of L[i] for P(L[i]) == True is preserved
(b) the ordering of L[i] for P(L[i]) == False is preserved
(c) for any L[i] such that P(L[i]) == True and which is preceded 
    by some L[j] s.t. P(L[j]) == False then L1[i-1] = L[i]
(d) for any L[i] that is not preceded by L[j] s.t. P(L[j]) == False 
    then L1[i] = L[i]

The idea is that all members of the list for which P evaluates True are moved 
up the list by one slot, except where they occur at the start of the list.

== Algorithm

Thus, we have:

> move_up p []  = []
> move_up p [v] = [v]
> move_up p (v:vtail)
>    | p v      = v:(move_up p vtail)
> move_up p (v1:v2:vtail)
>    | not (p v1) && (p v2) 
>               = v2:(move_up p (v1:vtail))
>    | not (p v1) && not (p v2) 
>               = v1:(move_up p (v2:vtail))

Under induction (i.e. assuming move_up satifies all contditions for a list of length N, 
it also satisfies for a list of length N+1);  clearly, cases 1 and 2 satisfy the 
ordering constraints for lists of length 0 and 1:

1. order is preserved per (a), (b) in the first three cases. The 4th case changes 
the order of two elements which are not covered by either of the order-preserving
requirements (a) or (b). 

2. concerning requirement (d), any element not preceded by another which does not 
satisfy P must clearly be part of a list whose first element does not satisfy P.  
This case is covered by case 4, and repeated application of this deals with a 
leading sequence for which P is False,

3. that requirement (c) is satisfied is confirmed by noting that in a list of 
length 2 of more, the position of an element satisfying p following one that does 
not is moved up by just one place, and immediately becomes part of the result 
sequence.  Further, if the next element also satisfies p, it will be preceded on
recursive evaluation of the updated tail of the list by an element that does 
satisfy p.

== Test cases

Strings in alist that begin with 'x' arer moved up thye list by one place.

> p (c:v) = c == 'x'

> mu_test =
>     [ move_up p []     == []
>     , move_up p ["o1"] == ["o1"]
>     , move_up p ["x1"] == ["x1"]
>     , move_up p ["o1","o2"] == ["o1","o2"]
>     , move_up p ["x1","o2"] == ["x1","o2"]
>     , move_up p ["o1","x2"] == ["x2","o1"]
>     , move_up p ["x1","x2"] == ["x1","x2"]
>     , move_up p ["o1","o2","o3"] == ["o1","o2","o3"]
>     , move_up p ["x1","o2","o3"] == ["x1","o2","o3"]
>     , move_up p ["o1","x2","o3"] == ["x2","o1","o3"]
>     , move_up p ["x1","x2","o3"] == ["x1","x2","o3"]
>     , move_up p ["o1","o2","x3"] == ["o1","x3","o2"]
>     , move_up p ["x1","o2","x3"] == ["x1","x3","o2"]
>     , move_up p ["o1","x2","x3"] == ["x2","x3","o1"]
>     , move_up p ["x1","x2","x3"] == ["x1","x2","x3"]
>     , move_up p ["x1","o2","o3","x4","x5","o6","o7","x8","o9"] 
>                                  == ["x1","o2","x4","x5","o3","o6","x8","o7","o9"]
>     ]

To confirm the result, evaluate "all id mu_test"

== Move down

To move the selected elements towards the tail, we use:

> move_down p = reverse . (move_up p) . reverse

Which satisfies the the following test cases:

> md_test =
>     [ move_down p []     == []
>     , move_down p ["o1"] == ["o1"]
>     , move_down p ["x1"] == ["x1"]
>     , move_down p ["o1","o2"] == ["o1","o2"]
>     , move_down p ["x1","o2"] == ["o2","x1"]
>     , move_down p ["o1","x2"] == ["o1","x2"]
>     , move_down p ["x1","x2"] == ["x1","x2"]
>     , move_down p ["o1","o2","o3"] == ["o1","o2","o3"]
>     , move_down p ["x1","o2","o3"] == ["o2","x1","o3"]
>     , move_down p ["o1","x2","o3"] == ["o1","o3","x2"]
>     , move_down p ["x1","x2","o3"] == ["o3","x1","x2"]
>     , move_down p ["o1","o2","x3"] == ["o1","o2","x3"]
>     , move_down p ["x1","o2","x3"] == ["o2","x1","x3"]
>     , move_down p ["o1","x2","x3"] == ["o1","x2","x3"]
>     , move_down p ["x1","x2","x3"] == ["x1","x2","x3"]
>     , move_down p ["x1","o2","o3","x4","x5","o6","o7","x8","o9"] 
>                          == ["o2","x1","o3","o6","x4","x5","o7","o9","x8"]
>     ]

Voila!




