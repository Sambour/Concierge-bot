import openai
import jsonlines


def predicate_gen(prompt):
    #priceRange(expensive / moderate / cheap / cheap / moderate / high) cuisine(Chinese / English / Fast food / French / Indian / Italian / Japanese) require("style","restaurant / pub / coffee shop) customer rating(low / average / high / low / average / high)

    context = '''
    *tips*

    require("prefer","curry") require("prefer","spicy") require("price range","cheap") require("price range","moderate") require("price range","expensive") require("cuisine","Chinese") require("cuisine","English") require("cuisine","fast food") require("establishment","pub") require("establishment","coffee shop") require("customer rating","low") require("customer rating","average") require("customer rating","high") require("property","family-friendly")

    When more than one value occurs in a predicate, if we need all of them satisfied, use "[]" to add them together; if either one is okay, treat them as different predicates.
    
    "query" only show up in the questions for the value the question is asking for.

    Examples only provide output format. Don't use any information from them!

    *example*

    There is a place in the city centre, Alimentum, that is not family-friendly. ### require("name","Alimentum")

    Fitzbillies coffee shop provides a kid friendly venue for Chinese food at an average price point in the riverside area. It is highly rated by customers. ### require("name","Fitzbillies"), require("establishment","coffee shop"), require("cuisine","Chinese"), require("price range","moderate"), require("customer rating","high"), require("property","family-friendly")

    What coffee shop is located in the city centre? ### require("establishment","coffee shop"), require("name","query")

    The Eagle coffee shop is a family-friendly restaurant that provides English food in a low price range. It is located near Burger King in the city centre and has a low customerRating. ### require("name","The Eagle"), require("cuisine","English"), require("establishment","coffee shop"), require("price range","cheap"), require("customer rating","low"), require("property","family-friendly")

    What is the customerRating of the Eagle? ### require("name","The Eagle"), require("customer rating","query")

    What is the name of the French restaurant at the end of the city? ### require("name","query"), require("cuisine","French")

    There is a Indian coffee shop near Café Sicilia in the moderate price range called The Punter. It has a customerRating of low and is kid friendly. ### require("name","The Punter"), require("cuisine","Indian"), require("establishment","coffee shop"), require("price range","moderate"), require("customer rating","low"), require("property","family-friendly")

    Located near Raja Indian Cuisine in the Riverside area is Travellers Rest Beefeaters which receives low customerRatings. ### require("name","Travellers Rest Beefeater"), require("customer rating","low")

    The Cambridge Blue is a kids friendly pub near Burger King in the riverside area. ### require("name","The Cambridge Blue"), require("establishment","pub"), require("customer rating","low"), require("property","family-friendly")

    The Waterman has Japanese food in high price near Crowne Plaza Hotel. ### require("name","The Waterman"), require("cuisine","Japanese"), require("price range","expensive")

    Can you find a place for food in low price? ### require("name","query"), require("price range","cheap")

    I need the address and phone number for Alimentum. ### require("name","Alimentum"), require("address","query"), require("phoneNumber","query")

    How can I contact The Tagrita? ### require("name","The Tagrita"), require("phoneNumber","query")

    Where is it? ### require("address","query")

    Either English and Indian suit for me. ### require("cuisine","English"), require("cuisine","Indian")

    I do not care the price. ### require("price range","cheap"), require("price range","moderate"), require("price range","expensive")

    On a scale of one to five, how important is the customer rating of the location you are looking for? I think the rating doesn't matter. ### require("name","query"), require("customer rating","high"), require("customer rating","average"), require("customer rating","low")

    Are you looking for a restaurant with a particular customer rating? Above average rating is fine ### require("name","query"), require("customer rating","high"), require("customer rating","average")

    I want to find a place for delicious food. ### require("name","query"), require("customer rating","high")

    I like spicy food, so can you find a high rating place for that? ### require("name","query"), require("prefer","spicy"), require("customer rating","high")

    I want a pub for curry. Could you please tell me where can I find a not pricey one? ### require("name","query"), require("address","query"), require("establishment","pub"), require("prefer","curry"), require("price range"), require("price range","cheap"), require("price range","moderate")

    Can you recommend me a restaurant with spicy food? ### require("name","query"), require("prefer","spicy")
    
    I really appreciat it! ### thank

    Sounds nice. Thank you! ### thank

    *start*

    '''

    prompt += ' ###'
    prediction = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=context + prompt, max_tokens=200, temperature=0)
    return prediction['choices'][0]['text']


def sentence_gen(prompt):
    context = '''
    Turn the predicates to the sentence.
    It happens in the restaurant recommendation situation.

    *example*

    name(Alimentum), familyFriendly(no) ### The name is Alimentum, and it is not family-friendly.

    name(Fitzbillies), typeToEat(coffee shop), cuisine(Chinese), priceRange(moderate), customerRating(high), familyFriendly(yes) ### I would recommend you the coffee shop Fitzbillies. It provides a kid friendly venue for Chinese food at an average price point. It is highly rated by customers.

    name(Travellers Rest Beefeater), customerRating(low), address(1270 Coit Rd, Richardson) ### Located at 1270 Coit Road in Richardson is Travellers Rest Beefeaters is the suggestion for you. But I should mention that it receives low customer ratings.

    name(The Waterman), cuisine(Japanese), phoneNumber(414-247-2758) ### Maybe you are looking for the Waterman. It has Japanese food. You can call 414-247-2758 for reservation.

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

if __name__ == "__main__":
    prompt = "Hi I need a restaurant for my families. A Chinese bar or a Indian coffee shop is fine for me."
    out = predicate_gen(prompt)
    print(out)