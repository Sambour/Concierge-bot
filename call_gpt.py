import openai
import jsonlines


def predicate_gen(prompt):
    #price range(expensive / moderate / cheap / cheap / moderate / high) cuisine(Chinese / English / Fast food / French / Indian / Italian / Japanese) typeToEat(restaurant / pub / coffee shop) customer rating(low / average / high / low / average / high)

    context = '''
    *tips*

    prefer(drink/curry/spicy/pizza/taco/chicken/alcohol/bagel) price range(cheap/moderate/expensive) establishment(restaurant/pub/fast food/shop/sports bar/bar&grill) customer rating(low/average/high) food type(Indian/American/southern American/Mexican/Italian/Japanese/Chinese/Thai/Halal)

    Never generate perfer(Indian), etc., since it's not in prefer scope mentioned above. Use food type(Indian) since cuisines such as Indian is in the scope of food type.
    
    When more than one value occurs in a 'prefer' predicate, if we need all of them satisfied, add them in one "()"; if either one is okay, treat them as different predicates.
    
    Examples only provide output format. Don't use any information from them!

    *example*

    There is a place in the city centre, Alimentum, that is not family-friendly. ### name(Alimentum), family-friendly(no)

    Fitzbillies coffee shop provides a kid friendly venue at an average price point in the riverside area. It is highly rated by customers. ### name(Fitzbillies), establishment(shop), food type(coffee), price range(moderate), customer rating(high), family-friendly(yes)

    What coffee shop is located in the city centre? ### establishment(shop), food type(coffee), name(query)

    What is the customer rating of the Eagle? ### name(The Eagle), customer rating(query)

    What is the name of the restaurant at the end of the city? ### name(query), establishment(restaurant)

    Located near Raja Indian Cuisine in the Riverside area is Travellers Rest Beefeaters which receives low customer ratings. ### name(Travellers Rest Beefeater), customer rating(low)

    The Cambridge Blue is a kids friendly pub near Burger King in the riverside area. ### name(The Cambridge Blue), establishment(pub), customer rating(low), family-friendly(yes)

    The Waterman has American food in high price near Crowne Plaza Hotel. ### name(The Waterman), food type(American), price range(expensive)

    Can you find a place for food in low price? ### name(query), price range(cheap)

    I need the address and phone number for this restaurant. ### address(query), phone number(query)

    How can I contact The Tagrita? ### name(The Tagrita), phone number(query)

    Where is it? ### address(query)

    I want some alcohol. ### name(query), prefer(alcohol)

    Both English and Indian food suit for me. ### food type(English, Indian)

    I do not care the price. ### price range(cheap, moderate, expensive)

    On a scale of one to five, how important is the customer rating of the location you are looking for? I think the rating doesn't matter. ### name(query), customer rating(high, average, low)

    Are you looking for a restaurant with a particular customer rating? Above average rating is fine ### name(query), establishment(restaurant), customer rating(high, average)

    I want to find a place for delicious food. ### name(query), customerRange(high)

    I'd prefer Italian and Indian, but better not spicy. ### food type(Thai, Indian), not prefer(spicy)

    I like spicy food, so can you find a high rating place for that? ### name(query), prefer(spicy), customer rating(high)

    I want a pub for curry. Could you please tell me where can I find a not pricey one? ### name(query), address(query), establishment(pub), prefer(curry), price range(cheap, moderate)

    Can you recommend me a restaurant which is both family-friendly and provide pizza? ### name(query), establishment(restaurant), family-friendly(yes), prefer(pizza)

    Can you recommend me a fast food pub? I'm looking for either spicy curry or pizza. ### name(query), establishment(pub), cuisine(fast food), prefer(spicy, curry), prefer(pizza)

    I don't like spicy food and pizza. Also don't recommend me Japanese cuisine or English food. ### not prefer(spicy, pizza), not food type(Japanese, English).
    
    I really appreciat it! ### thank

    Sounds nice. Thank you! ### thank
    
    I don't like this one. Any other choice? ### another_option(yes)

    I'd prefer Halal food, do you have another restaurant for that? ### another_option(yes), food type(Halal)

    *start*

    '''

    prompt += ' ###'
    prediction = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=context + prompt, max_tokens=50, temperature=0)
    return prediction['choices'][0]['text']


def sentence_gen(prompt):
    context = '''
    Turn the predicates to the sentence.
    It happens in the restaurant or bar recommendation situation.

    *example*

    name(Alimentum), price range(cheap) ### The name is Alimentum, and it is a cheap restaurant.

    name(Fitzbillies), establishment(shop), food type(cofffee), price range(moderate), customer rating(high), family-friendly(yes) ### I would recommend you the coffee shop Fitzbillies. It provides a kid friendly venue at an average price point. It is highly rated by customers.

    name(Travellers Rest Beefeater), customer rating(low), address(1270 Coit Rd, Richardson) ### Located at 1270 Coit Road in Richardson is Travellers Rest Beefeaters is the suggestion for you. But I should mention that it receives low customer ratings.

    name(The Waterman), food type(Japanese), phone number(414-247-2758) ### Maybe you are looking for the Waterman. It has Japanese food. You can call 414-247-2758 for reservation.

    *start*

    '''

    prompt += ' ###'
    prediction = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=context + prompt, max_tokens=500, temperature=0.65)
    return prediction['choices'][0]['text']


def sentence_diversity(prompt):
    context = '''
    Rewrite the sentence in a different expression.
    Do not mention the word "restaurant" if there is no clue saying it's a restaurant.

    *example*

    What can I do for you, sir? -> Hello, what can I help you today?

    What kind of food do you prefer? -> What type of cuisine are you looking for?

    Sorry, I didn't get what you mean. -> Sorry, I didn't understand. Could you please say that again?

    *start*

    '''

    prompt += ' ->'
    prediction = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=context + prompt, max_tokens=500, temperature=1)
    return prediction['choices'][0]['text']

'''

# Problem: if use max_tokens option, then generates unformatted sentences until max;
# if not use this option, then generates incomplete predicates

with open('output_train.jsonl', 'r+') as f:
    data = jsonlines.Reader(f)

    score = 0.
    count = 0

    for item in data:
        if count < 0:
            pass
        elif count < 500:
            completion = item['completion']
            prompt = item['prompt']
            prediction = openai.Completion.create(
                model="text-davinci-003",
                prompt=context + prompt + ' ###', temperature=0, max_tokens=50)
            prediction = prediction['choices'][0]['text']
            
            score += 1 if prediction == completion else 0
            temp = {"prompt": prompt, "completion": completion, "prediction": prediction}
            with jsonlines.open('predictions_11shots.jsonl', mode='a') as writer:
                writer.write(temp)
        
        #else:
            #break

        count += 1

    score /= count
    print(score)
'''