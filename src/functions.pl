% Key Info List: Which are to ask.
key_info('food type'). key_info('price range'). key_info('customer rating').

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

% select function.
select(A, [A|T], T).
select(A, [H|T], [H|R]) :- A \= H, select(A, T, R).

% merge function.
merge([], A, A).
merge([H|T], B, C) :- member(H, B), merge(T, B, C).
merge([H|T], B, D) :- neg_member(H, B), append(B, [H], C), merge(T, C, D).

% intersection function.
intersection([], _, []).
intersection([H|T], L, [H|Res]) :- member(H, L), intersection(T, L, Res).
intersection([H|T], L, Res) :- not member(H, L), intersection(T, L, Res).

% replace function. (replace(A, B, L1, L2) :- replace item A from L1 to B to get L2.)
replace(_, _, [], []).
replace(O, R, [O|T1], [R|T2]) :- replace(O, R, T1, T2).
replace(O, R, [H|T1], [H|T2]) :- H \= O, replace(O, R, T1, T2).

% subtract function. subtract(A, B, C) :- A-B=C.
subtract([], _, []).
subtract([A|C], B, D) :- member(A, B), subtract(C, B, D).
subtract([A|B], C, [A|D]) :- neg_member(A, C), subtract(B, C, D).

% If not detect query, add query(name).
query('name') :- not other_query('name').
other_query(X) :- query(Y), X \= Y.

% 1. Generate what would be the next predicate.
next_info(X) :- key_info(X), not neg_next_info(X).
neg_next_info(X) :- not next_info(X).
neg_next_info(X) :- not_require(X, _).
neg_next_info(X) :- require(X, _).

% 2. Give the recommendation.
recommend(Recommendation) :- answer_current('yes'), current(Recommendation).
recommend(Recommendation) :- answer_current('yes'), result(Recommendation).
recommend(Recommendation) :- another_option('yes'), not answer_current('yes'), result(Recommendation).
recommend(Recommendation) :- not another_option('yes'), requirement_satisfy(Recommendation).

%place_s(X, Attr) :- place(X, Attr, Value), require(Attr, Value).
%req_s(Attr) :- require(Attr, _).
%uncover(X) :- req_s(Attr), not place_s(X, Attr).
%all_attr_satisfy(X) :- place(X), not uncover(X).
%requirement_satisfy(X) :- all_attr_satisfy(X), not neg_requirement_satisfy(X).
%neg_requirement_satisfy(X) :- not_require(Attr, Value), place(X, Attr, Value), not requirement_satisfy(X).

requirement_satisfy(Recommendation) :- 
	get_query_list(Queries), get_state_list(States), get_satisfied_places(States, Recommendation).

get_query_list(Queries) :- 
	findall(query(Query), query(Query), Queries).

get_state_list(States) :-
	findall(require(Attr, Value), require(Attr, Value), States).

get_satisfied_places(State, X) :- 
	select_requirement(State, State_Option), requirement_satisfy(X, State_Option).

% 3. Choose which action to apply next.
next_action('ask', Question) :- next_info(Question), !.
next_action('recommend', Result) :- recommend(Result).

% 4. Look up: Given a restaurant ID, return the querying information of this restaurant.
look_up(X, Attr, Value) :- query(Attr), place(X, Attr, Value).

% 5. Explain: show information for the restaurant.
explain(Place, Attr, Value) :- 
	place(Place), require(Attr, Value), place(Place, Attr, Value).

explain(Place, 'prefer', Prefer) :- 
	require(Attr, Value), place(Place, Attr, Value), prefer(Prefer), entail(prefer(Prefer), require(Attr, Value)).

explain_fail(Success, Fail) :-
	findall(require(Attr, Value), require(Attr, Value), State), select_requirement(State, Option), explain_fail(Option, [], Success, Fail).
explain_fail([Requirement|Rest], Success, Updated, Fail) :- 
	append(Success, [Requirement], Next), requirement_satisfy(X, Next), explain_fail(Rest, Next, Updated, Fail).
explain_fail([Requirement|Rest], Success, Success, Requirement) :- 
	append(Success, [Requirement], Next), no_requirement_satisfy(Next).

select_attr([], Attrs, Attrs).
select_attr([require(Attr, _)|R], Current, Attrs) :- neg_member(Attr, Current), append(Current, [Attr], Next), select_attr(R, Next, Attrs).
select_attr([require(Attr, _)|R], Current, Attrs) :- member(Attr, Current), select_attr(R, Current, Attrs).

select_requirement(State, Result) :- 
	select_attr(State, [], Attrs), select_requirement(State, Attrs, Option), findall(not_require(Attr, Value), not_require(Attr, Value), State2),
	append(Option, State2, Result).
select_requirement(State, [], []).
select_requirement(State, [Attr|Rest], [require(Attr, Value)|Options]) :- member(require(Attr, Value), State), select_requirement(State, Rest, Options).
select_requirement(State, [Attr|Rest], [require(Attr, Value)|Options]) :- member(require(Attr, Value), State), select_requirement(State, Rest, Options).

requirement_satisfy(X, []).
requirement_satisfy(X, [require(Attr, Value)|R]) :- 
	place(X, Attr, Value), requirement_satisfy(X, R).
requirement_satisfy(X, [not_require(Attr, Values)|R]) :- 
	place(X, Attr, Value), not member(Value, Values), requirement_satisfy(X, R).

no_requirement_satisfy(X) :- requirement_satisfy(A, X), !, fail.
no_requirement_satisfy(X).

% 6. View History Recommendations.

view(I, I, State) :- history(I, State).
view('first', 1, State) :- history(1, State).
view('last', X, State) :- find_last_history(1, X, State).
view('next', X, State) :- current(I), X is I + 1, history(X, State).
view('previous', X, State) :- current(I), X is I - 1, history(X, State).

find_last_history(I, X, State) :- history(I, _), Next is I + 1, find_last_history(Next, X, State).
find_last_history(I, I, State) :- history(I, State), Next is I + 1, forall(S, not history(Next, S)).

%query('name'). require('food type', 'pizza'). require('food type', 'Italian'). query('address'). require('price range', 'moderate'). require('customer rating', 'high'). require('customer rating', 'average'). require('customer rating', 'low'). another_option('yes').

%?- view('last', I, State).