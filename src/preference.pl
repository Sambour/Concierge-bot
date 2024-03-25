new_require('food type', X) :- new_prefer(X).
new_require('establishment', 'shop') :- new_prefer('drink'), not not_require('establishment', 'shop').
new_prefer('bar') :- new_require('food type', 'bar').
new_require('establishment', 'bar') :- new_prefer('bar').
new_require('establishment', 'pub') :- new_prefer('bar'), not not_require('establishment', 'pub').
new_require('establishment', 'sports bar') :- new_prefer('bar'), not not_require('establishment', 'sports bar').
new_require('establishment', 'bar&grill') :- new_prefer('bar'), not not_require('establishment', 'bar&grill').
new_prefer('bar') :- new_prefer('alcohol').
new_prefer('bar') :- new_prefer('drink').
new_require('establishment', 'buffet') :- new_require('establishment', 'restaurant'), not not_require('establishment', 'buffet').

new_not_require('food type', X) :- new_not_prefer(X).
new_not_require('establishment', 'shop') :- new_not_prefer('drink'), not require('establishment', 'shop').
new_not_require('establishment', 'pub') :- new_not_prefer('bar'), not require('establishment', 'pub').
new_not_require('establishment', 'sports bar') :- new_not_prefer('bar'), not require('establishment', 'sports bar').
new_not_require('establishment', 'bar&grill') :- new_not_prefer('bar'), not require('establishment', 'bar&grill').
new_not_prefer('bar') :- new_not_prefer('alcohol').

entail(prefer(X), require('food type', X)).
entail(prefer('bar'), require('establishment', 'pub')).
entail(prefer('bar'), require('establishment', 'sports bar')).
entail(prefer('bar'), require('establishment', 'bar&grill')).
entail(prefer('alcohol'), require('establishment', 'pub')).
entail(prefer('alcohol'), require('establishment', 'sports bar')).
entail(prefer('alcohol'), require('establishment', 'bar&grill')).
entail(require('establishment', 'restaurant'), require('establishment', 'buffet')).