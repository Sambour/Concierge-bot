flies(X) :- bird(X), not ab(X), not -flies(X).

-flies(X) :- ostrich(X).

bird(sam).
bird(tweety).
ostrich(sam).

?- flies(sam).
