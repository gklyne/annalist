= Tree scan

The challenge is to construct a scanning order to locate immediate and 
indirect child elements of a parent node, taking account of possible
alternative parents and preserving depth oprdering.

== Requirements

Given:

> data Entity = Entity { eid :: String, altparents :: [Entity] } deriving Eq

> instance Show Entity where
>     show e = eid e ++ ":" ++ show [ eid a | a <- altparents e ]

Define a function to return all unique possible parents:

> parentlist :: Entity -> [Entity]

such that:

(a) the initial entity is the first element of thje list
(b) all entities that are reachable directly or indirectly as alternative parents are in the list,
(c) no entity appears more than once, and
(d) depth ordering is preserved; i.e, if any entity e2 is an alternative parent of e1, then e2 appears after e1 in the resulting list.  This means that alparents must for a directed graph.

The intent is that the resulting list can be used as a search path for finding child entities, first within the supplied entity, and then in alternative parents, culminating in a common alternatiuve pareent of all entities.

== Algorithm

> parentlist e@(Entity {altparents=alts}) = e:altpath -- req (a)
>     where
>         altpath = mergealts e [ parentlist p | p <- alts ]
>
> mergealts :: Entity -> [[Entity]] -> [Entity]
> mergealts _ []            = []
> mergealts parent [altpath]
>   | parent `elem` altpath = error ("Entity "++(show parent)++" has recursive altparent path")
>   | otherwise             = altpath
> mergealts parent (alt1:alt2:morealts) = 
>     mergealts parent ((mergealtpair alt1 alt2):morealts)
>
> mergealtpair :: [Entity] -> [Entity] -> [Entity]
> mergealtpair [] alt2      = alt2
> mergealtpair alt1 []      = alt1
> mergealtpair alt1@(h1:t1) alt2@(h2:t2)
>   | h1 == h2              = h1:mergealtpair t1 t2     -- req (b) (part)
>   | h1 `notElem` t2       = h1:mergealtpair t1 alt2   -- req (d)
>   | h2 `notElem` t1       = h2:mergealtpair alt1 t2   -- req (d)
>   | otherwise             = error ("Cannot preserve depth ordering of "++(show h1)++" and "++(show h2))

== Test cases

> root = Entity { eid = "root", altparents = [] }
> e1   = Entity { eid = "e1",   altparents = [root] }
> e2   = Entity { eid = "e2",   altparents = [root] }
> e3   = Entity { eid = "e3",   altparents = [root] }
>
> e4   = Entity { eid = "e4",   altparents = [e1] }
> e5   = Entity { eid = "e5",   altparents = [e2, root] }
> e6   = Entity { eid = "e6",   altparents = [e1, e3] }
> e7   = Entity { eid = "e7",   altparents = [e3, e1] }
>
> e10  = Entity { eid = "e10",  altparents = [e4, e5] }
> e11  = Entity { eid = "e11",  altparents = [e4, e5, e6] }
> e12  = Entity { eid = "e12",  altparents = [e5, e6] }
> e13  = Entity { eid = "e13",  altparents = [e6, e5] }
> e14  = Entity { eid = "e14",  altparents = [e10, e12] }
> e15  = Entity { eid = "e15",  altparents = [e10, e13] }
> e16  = Entity { eid = "e16",  altparents = [e13, e10] }

> e20  = Entity { eid = "e10",  altparents = [e6, e7] }     -- error
> e21  = Entity { eid = "e10",  altparents = [e1, e2, e1] } -- should be error

> parents_test =
>     [ parentlist root == [root]
>     , parentlist e1   == [e1,  root] 
>     , parentlist e2   == [e2,  root] 
>     , parentlist e3   == [e3,  root] 
>     , parentlist e4   == [e4,  e1, root] 
>     , parentlist e5   == [e5,  e2, root] 
>     , parentlist e6   == [e6,  e1, e3, root] 
>     , parentlist e7   == [e7,  e3, e1, root] 
>     , parentlist e10  == [e10, e4, e1, e5, e2, root] 
>     , parentlist e11  == [e11, e4, e6, e1, e5, e2, e3, root] 
>     , parentlist e12  == [e12, e5, e2, e6, e1, e3, root] 
>     , parentlist e13  == [e13, e6, e1, e3, e5, e2, root] 
>     , parentlist e15  == [e15, e10, e4, e13, e6, e1, e3, e5, e2, root] 
>     , parentlist e16  == [e16, e13, e6, e10, e4, e1, e3, e5, e2, root] 
>     ]

> failing_tests = 
>     [ parentlist e14
>     , parentlist e20
>     ]

To confirm the result, evaluate "all id parents_test"

