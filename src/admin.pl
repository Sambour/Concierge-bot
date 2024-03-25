% member function.
member(X, [X|_]).
member(X, [A|T]) :- A \= X, member(X, T).

neg_member(X, []).
neg_member(X, [Y|T]) :- X \= Y, neg_member(X, T).
% neg_member(X, Y) :- member(X, Y), !, fail.
% neg_member(X, Y).

% append function.
append([], L, L).
append([H|T], L, [H|R]) :- append(T, L, R).

% subtract function. subtract(A, B, C) :- A-B=C.
subtract([], _, []).
subtract([A|C], B, D) :- member(A, B), subtract(C, B, D).
subtract([A|B], C, [A|D]) :- neg_member(A, C), subtract(B, C, D).

% unique function.
unique(L, U) :- unique(L, [], U).
unique([], _, []).
unique([H|T], C, [H|U]) :- neg_member(H, C), unique(T, [H|C], U).
unique([H|T], C, U) :- member(H, C), unique(T, [H|C], U).

% Key Features
key_feature('name'). key_feature('price range'). key_feature('customer rating'). key_feature('address').

% State generate.
admin_action(X) :- admin(X, Feature, Value).
admin('add', Feature, Value) :- add(Feature, Value).
admin('delete', Feature, Value) :- delete(Feature, Value).
admin('edit', Feature, Value) :- edit(Feature, Value).

% Request to act one by one.
multi_op :- admin_action(A), admin_action(B), A \= B.

% Find the Number of the final Place.
find_last_place(X) :- find_last_place(1, X), !.
find_last_place(I, X) :- place(I), Next is I + 1, find_last_place(Next, X).
find_last_place(I, I) :- place(I), Next is I + 1, not place(Next).

% Checking the updating mode and find the venue to modify.
updating_place(X1) :- admin_action('add'), find_last_place(X), X1 is X + 1.
updating_place(X) :- admin_action('edit').
updating_place(X) :- admin_action('delete').

% Gathering State before finish updating.
get_admin_state(State) :- updating_place(X), admin_action(Op), findall(admin(Op, F, V), admin(Op, F, V), S), append([admin_action(Op)], S, State).

% CKT: get required features.
next_feature(X) :- key_feature(X), not neg_next_feature(X).
neg_next_feature(X) :- not next_feature(X).
neg_next_feature(X) :- admin('add', X, _).

next_has_feature(X) :- next_feature(X).
next_has_feature(X).

% Update: after all info collected, update it to the knowledge base.
%edited_place(X, A, V) :- admin_action(I), I \= 'delete', places(P), member(place(X, A, V), P), not admin(I, A, V).
edited_place(X, A, V) :- admin_action(I), I \= 'delete', admin(I, A, V).

update_admin_state(State, 'add') :- admin_action('add'), updating_place(I), findall(edited_place(I, A, V), edited_place(I, A, V), Ls), unique(Ls, L), replace_place(L, State).
update_admin_state(State, 'edit') :- admin_action('edit'), updating_place(I), findall(edited_place(I, A, V), edited_place(I, A, V), L), replace_place(L, State).
update_admin_state(State, 'delete') :- admin_action('delete'), updating_place(I), places(L1), 
    findall(place(I, A, V), place(I, A, V), L2), subtract(L2, L1, State).

replace_place([], []).
replace_place([edited_place(A, B, C)|L], [place(A, B, C)|R]) :- replace_place(L, R).

% Next Action.
next_action_admin(State, 'quit', None) :- quit, !.
next_action_admin(State, 'one by one', None) :- multi_op, !.
next_action_admin(State, 'cancel', None) :- admin_action(X), cancel(X), !.
next_action_admin(State, 'irrelevant', Question) :- irrelevant, !, next_has_feature(Question, X), get_admin_state(State).
next_action_admin(State, 'ask', Question) :- next_feature(Question), !, get_admin_state(State).
next_action_admin(State, 'updated', X) :- update_admin_state(State, X), !.

add('name', 'ARRS'). add('price range', 'expensive'). add('customer rating', 'low'). add('address', '102 W Campbell Rd').

?- findall(edited_place(X, A, V), edited_place(X, A, V), Ls), unique(Ls, L), replace_place(L, L1), places(L2), append(L2, [place(I)|L1], State).