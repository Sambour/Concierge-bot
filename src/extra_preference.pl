new_require('food type', 'Seafood') :- new_prefer('lobster'), not not_require('food type', 'Seafood').
new_not_require('food type', 'Seafood') :- new_not_prefer('lobster'), not require('food type', 'Seafood').
entail(prefer('lobster'), require('food type', 'Seafood')).
new_require('food type', 'Vegetarian') :- new_prefer('carrot'), not not_require('food type', 'Vegetarian').
new_not_require('food type', 'Vegetarian') :- new_not_prefer('carrot'), not require('food type', 'Vegetarian').
entail(prefer('carrot'), require('food type', 'Vegetarian')).
new_require('food type', 'Vegan') :- new_prefer('carrot'), not not_require('food type', 'Vegan').
new_not_require('food type', 'Vegan') :- new_not_prefer('carrot'), not require('food type', 'Vegan').
entail(prefer('carrot'), require('food type', 'Vegan')).
