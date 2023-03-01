% Key Info List: Which are to ask.
key_info(['food type', 'price range', 'customer rating']). 

% Preference List: prefer(A, B), prefer(C) means either A with B, or just C.
style('alcohol', ['pub', 'bar']).
style('drink', ['coffee', 'smoothie', 'bubble tea', 'pub', 'sports bar', 'bar&grill']).
style('curry', ['Indian', 'Thai', 'Japanese']).
style('spicy', ['Indian', 'Thai', 'Mexican']).
style('taco', ['Mexican', 'taco']).
style('chicken', ['American', 'chicken', 'southern American', 'Thai']).
style('pizza', ['Italian', 'American', 'pizza']).
style('bagel', ['bagel']).
style('cookie', ['cookie']).

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

% Update the preference first.
set_prefer(State, Updated, []) :- set_prefer(State, [], [], Updated).
set_prefer(State, Updated, [require('food type', Recm_List)]) :- 
	set_prefer(State, [], Recm_List, Updated), Recm_List \= [].
set_prefer(State, Recm_List, Updated_Recm_List, Rest_State) :- 
	select(require('prefer', Values), State, Current), get_prlist(Values, Pr_List), 
	merge(Recm_List, Pr_List, New_Recm_List), set_prefer(Current, New_Recm_List, Updated_Recm_List, Rest_State).
set_prefer(State, Updated, Updated, State) :-
	forall(Values, neg_member(require('prefer', Values), State)).

% We don't support the case like "I don't like food that is both curry and spicy, but with only one of them is acceptable."
% Which means, no conjunction in two "not_prefer"s.
% So only update once and no recursion.
set_not_prefer(State, Updated, [not_require('food type', Recm_List)]) :- 
	select(not_require('prefer', Values), State, Updated), get_non_prlist(Values, Recm_List).
set_not_prefer(State, State, []) :- 
	forall(Values, neg_member(not_require('prefer', Values), State)).

get_prlist(Values, Pr_List) :- 
	get_prlist(Values, [], Pr_List).
get_prlist([], Pr_List, Pr_List).
get_prlist([Value|Rest], Current, Pr_List) :- 
	style(Value, S_List), prefer_inter(Current, S_List, Next), get_prlist(Rest, Next, Pr_List).
get_prlist([Value|Rest], Current, Pr_List) :- 
	forall(S_List, not style(Value, S_List)), get_prlist(Rest, Current, Pr_List).

get_non_prlist(Values, Non_Pr_List) :- 
	get_non_prlist(Values, [], Non_Pr_List).
get_non_prlist([], Non_Pr_List, Non_Pr_List).
get_non_prlist([Value|Rest], Current, Non_Pr_List) :- 
	style(Value, S_List), merge(Current, S_List, Next), get_non_prlist(Rest, Next, Non_Pr_List).
get_non_prlist([Value|Rest], Current, Non_Pr_List) :- 
	forall(S_List, not style(Value, S_List)), get_non_prlist(Rest, Current, Non_Pr_List).

prefer_inter([], A, A).
prefer_inter(A, B, C) :- 
	A \= [], intersection(A, B, C).

% Update the List of Requirement State. 
% Note that if the user ask for different type of requirement (e.g. both Indian and English restaurant), the recent query has higher priority.
add_state([], Updated, Updated).
add_state([require(Attr, Values)|Rest], State, Updated) :-
	member('query', Values), member(require(Attr, Values1), State), add_state(Rest, State, Updated).
add_state([require(Attr, Values)|Rest], State, Updated) :-
	neg_member('query', Values), member(require(Attr, Values1), State), select('query', Values1, Values2), merge(Values2, Values, Values3), 
	replace(require(Attr, Values1), require(Attr, Values3), State, Next), remove_not_require(Next, Attr, Values, Next1), add_state(Rest, Next1, Updated).
add_state([require(Attr, Values)|Rest], State, Updated) :-
	neg_member('query', Values), member(require(Attr, Values1), State), neg_member('query', Values1), merge(Values1, Values, Values2), 
	replace(require(Attr, Values1), require(Attr, Values2), State, Next), remove_not_require(Next, Attr, Values, Next1), add_state(Rest, Next1, Updated).
add_state([require(Attr, Values)|Rest], State, Updated) :-
	forall(Values1, neg_member(require(Attr, Values1), State)), append(State, [require(Attr, Values)], Next), 
	remove_not_require(Next, Attr, Values, Next1), add_state(Rest, Next1, Updated).
add_state([not_require(Attr, Values)|Rest], State, Updated) :-
	member(not_require(Attr, Values1), State), merge(Values1, Values, Values2), 
	replace(not_require(Attr, Values1), not_require(Attr, Values2), State, Next), add_state(Rest, Next, Updated).
add_state([not_require(Attr, Values)|Rest], State, Updated) :-
	forall(Values1, neg_member(not_require(Attr, Values1), State)), append(State, [not_require(Attr, Values)], Next), add_state(Rest, Next, Updated).

remove_not_require(State, Attr, Values, State) :- forall(Values1, neg_member(not_require(Attr, Values1), State)).
remove_not_require(State, Attr, Values, Updated) :- 
	select(not_require(Attr, Values1), State, Next), subtract(Values1, Values, Values2), append([not_require(Attr, Values2)], Next, Updated).

% Update the State: first set_prefer/set_not_prefer, then add_state.
write_state(L1, L2, L3) :- 
	set_prefer(L1, L4, Recm_List), set_not_prefer(L4, Not_Recm_List, L5), 
	add_state(L5, L2, L6), add_state(Recm_List, L6, L7), add_state(Not_Recm_List, L7, L3).

% 1. Generate what would be the next predicate.
next_info(X, State) :- key_info(L), member(X, L), member(require(X, ['query']), State).
next_info(X, State) :- key_info(L), member(X, L), forall(A, neg_member(require(X, A), State)), forall(B, neg_member(not_require(X, B), State)).

% 2. Give the recommendation.
recommend(State, Result) :- 
	merge([require('name', ['query'])], State, Next), recommend_(Next, Result).
recommend(State, X) :- 
	recommend_(State, X).
recommend_(State, []) :- 
	forall(Attr, neg_member(require(Attr, ['query']), State)).
recommend_(State, [place(X, Attr, Value)|R]) :- 
	select(require(Attr, ['query']), State, L1), select_requirement(State, State_Option), 
	requirement_satisfy(X, State_Option), place(X, Attr, Value), recommend_(L1, R).

select_requirement(State, Option) :- select_requirement(State, [], Option).

select_requirement([], Option, Option).
select_requirement([require(Attr, ['query'])|R], Current, Option) :- 
	select_requirement(R, Current, Option).
select_requirement([require(Attr, Values)|R], Current, Option) :- 
	neg_member('query', Values), member(Value, Values), append([require(Attr, Value)], Current, Next), select_requirement(R, Next, Option).
select_requirement([not_require(Attr, Values)|R], Current, Option) :- 
	append([not_require(Attr, Values)], Current, Next), select_requirement(R, Next, Option).

requirement_satisfy(X, []).
requirement_satisfy(X, [require(Attr, Value)|R]) :- 
	place(X, Attr, Value), requirement_satisfy(X, R).
requirement_satisfy(X, [not_require(Attr, Values)|R]) :- 
	place(X, Attr, Value), not member(Value, Values), requirement_satisfy(X, R).

% 3. Choose which action to apply next.
next_action('ask', Question) :- 
	state(State), next_info(Question, State).
next_action('recommend', Result) :- 
	state(State), recommend(State, Result).

% 4. Explain: show information for the restaurant.
explain(Place, Result) :- 
	state(State), merge([require('name', ['query'])], State, Next), get_explain_attrs(Next, X), explain(Place, Result, X).
explain(Place, [], []).
explain([place(X, Query, Value1)|R], [place(X, Attr, Value2)|Result], [Attr|Info]) :- 
	place(X, Attr, Value2), explain([place(X, Query, Value1)], Result, Info).

get_explain_attrs([], []).
get_explain_attrs([require(Attr, L1)|Next], [Attr|R]) :-
	neg_member('query', L1), get_explain_attrs(Next, R).
get_explain_attrs([require(Attr, L1)|Next], R) :-
	member('query', L1), get_explain_attrs(Next, R).
get_explain_attrs([not_require(Attr, L1)|Next], [Attr|R]) :-
	get_explain_attrs(Next, R).

explain_fail(Success, Fail) :-
	state(State), select_requirement(State, Option), explain_fail(Option, [], Success, Fail).
explain_fail([Requirement|Rest], Success, Updated, Fail) :- 
	append(Success, [Requirement], Next), requirement_satisfy(X, Next), explain_fail(Rest, Next, Updated, Fail).
explain_fail([Requirement|Rest], Success, Success, Requirement) :- 
	append(Success, [Requirement], Next), forall(X, not requirement_satisfy(X, Next)).

% 5. Load Saved Results.
load('recommend', Result) :- 
	state(State), result(X), merge([require('name', ['query'])], State, Next), load_query(Next, Result, X).

load_query(State, [], X) :- forall(Attr, neg_member(require(Attr, ['query']), State)).
load_query(State, [place(X, Attr, Values)|R], X) :-
	select(require(Attr, ['query']), State, L1), place(X, Attr, Values), load_query(L1, R, X).
