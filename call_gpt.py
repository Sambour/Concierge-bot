import openai
import os

openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_version = "2023-05-15" 
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")


def predicate_gen(prompt):
    #price range(expensive / moderate / cheap / cheap / moderate / high) cuisine(Chinese / English / Fast food / French / Indian / Italian / Japanese) typeToEat(restaurant / pub / coffee shop) customer rating(low / average / high / low / average / high)

    context = '''

Now you are a concierge serving the restaurant recommendation. Reply "irrelevant" with anything not related to this topic.

*tips*

prefer(bar/drink/curry/spicy/pizza/...) require(price range, cheap/moderate/expensive) require(establishment, restaurant/pub/fast food/shop/sports bar/bar&grill) require(customer rating, low/average/high) require(food type, Indian/American/southern American/...) require(distance, in campus/near/far)

Never generate perfer(Indian), or prefer(American), etc. Use require(food type, Indian) and require(food type, American) instead. But for certain food (pizza, sushi, noodles, etc.), use prefer.
    
"in campus" option in distance is closer than "near" option.
    
Examples only provide output format. Don't use any information from them!

*example*

Fitzbillies cafe provides a kid friendly venue at an average price point in the riverside area. It is highly rated by customers. ### require(name, Fitzbillies). establishment(shop). require(food typem, coffee). require(price range, moderate). require(customer rating, high). require(family-friendly, yes).

What coffee shop is located in the city centre? Is it romantic? ### require(establishment, shop). require(food type, coffee). query(name). query(dating).

What is the customer rating of the Eagle? ### require(name, The Eagle). query(customer rating).

What is the name of the restaurant at the end of the city? ### query(name). require(establishment, restaurant).

Located in the campus is Travellers Rest Beefeaters which receives low customer ratings. ### require(name, Travellers Rest Beefeater). require(customer rating, low). require(distance, in campus).

The Cambridge Blue is a kids friendly pub near Chick-fil-A in the riverside area. ### require(name, The Cambridge Blue). require(establishment, pub). require(customer rating, low). require(family-friendly, yes).

The Waterman has American food in high price near Crowne Plaza Hotel. ### require(name, The Waterman). require(food type, American). require(price range, expensive).

Can you find a nearby place for food in low price? ### query(name). require(price range, cheap). require(distance, in campus). require(distance, near).

I need the address and phone number for this restaurant. ### query(address). query(phone number).

How can I contact The Tagrita? ### require(name, The Tagrita). query(phone number).

Where is it? ### query(address).

I'm going to hold a birthday party tonight ### require(establishment, restaurant). require(family-friendly, yes).

I want to have some alcohol with my boyfriend. ### query(name). prefer(alcohol). require(dating, yes).

Both English and Indian food suit for me. ### require(food type, English). require(food type, Indian).

[begin context] Are you looking for a restaurant with a particular customer rating? [end context] I do not care the price. ### require(price range, any).

On a scale of one to five, how important is the customer rating of the location you are looking for? I don't care the ratings. ### query(name). require(customer rating, any).

What type of cuisine do you prefer? Anything is fine for me. ### require(food type, any).
    
[begin context] Are you looking for a restaurant with a particular customer rating? [end context] Above average rating is fine ### query(name). require(establishment, restaurant). require(customer rating, high). require(customer rating, average).

I want to find a place for delicious food. ### query(name). require(customer range, high).

[begin context] Do you still want Italian food, like spaghetti? [end context] No. ### not_require(food type, Italian). not_prefer(spaghetti).

Sorry I've changed my mind. I'd prefer Italian and Indian, but better not spicy. ### require(food type, Thai). require(food type, Indian). not_prefer(spicy).

I like spicy food, so can you find a high rating place for that? ### query(name). prefer(spicy). require(customer rating, high).

I want a pub for curry. Could you please tell me where can I find a not pricey one? ### query(name). query(address). require(establishment, pub). prefer(curry). not_require(price range, expensive).

Can you recommend me a restaurant which is both family-friendly and provide pizza? ### query(name). require(establishment, restaurant). require(family-friendly, yes). prefer(pizza).

Can you recommend me a fast food pub? I'm looking for either spicy curry or pizza. ### query(name). require(establishment, pub). require(food type, fast food). prefer(spicy). prefer(curry). prefer(pizza).

I don't like spicy food and pizza. Also I don't like Japanese cuisine or English food. ### not_prefer(spicy). not_prefer(pizza). not_require(food type, Japanese). not_require(food type, English).
    
I really appreciat it! ### thank.

Sounds nice. Thank you! ### thank.

Do you like the movie Star War? ### irrelevant.

What brands of toilet papers did you sell? ### irrelevant.
    
I don't like this one. Any other choice? ### another_option(yes).

I'd prefer Halal food, do you have another restaurant for that? ### another_option(yes). require(food type, Halal).

Can you say that again? What's the name of it? ### view_history(last).

What's your second recommendation? I don't remember. ### view_history(2).

No, not this one. The previous one, please. ### view_history(previous).

Where can I find a Starbucks? ### query(address). require(name, Starbucks).

What did you recommend after that? Is that Burger King? ### view_history(next).

Sorry I need to leave. ### quit.

*start*

'''

    prompt += ' ###'
    #sleep(60)
    '''
    prediction = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=context + prompt, max_tokens=50, temperature=0)'''
    #return prediction['choices'][0]['text']
    prediction = openai.ChatCompletion.create(
                    engine='AutoConcierge',
                    messages=[{'role': 'system', 'content': 'please strictly follow the format in the following input.'},
                            {'role': 'user', 'content': context + prompt}],
                    max_tokens=50, temperature=0)
    return prediction['choices'][0]['message']['content']


def sentence_gen(prompt):
    #sleep(60)
    context = '''
    Turn the predicates to the sentence.
    It happens in the restaurant or bar recommendation situation.

    *example*

    recommend(name,Alimentum). has(price range,cheap) ### The name is Alimentum, and it is a cheap restaurant.

    recommend(name,Fitzbillies). has(establishment,shop). has(food type,cofffee). has(price range,moderate). has(customer rating,high). has(family-friendly,yes) ### I would recommend you the coffee shop Fitzbillies. It provides a kid friendly venue at an average price point. It is highly rated by customers.

    recommend(name,Travellers Rest Beefeater). has(customer rating,low). recommend(address,1270 Coit Rd, Richardson) ### Located at 1270 Coit Road in Richardson, Travellers Rest Beefeaters is the suggestion for you. But I should mention that it receives low customer ratings.

    recommend(name,The Waterman). has(food type,Japanese). recommend(phone number,414-247-2758) ### Maybe you are looking for the Waterman. It has Japanese food. You can call 414-247-2758 for reservation.

    *start*

    '''

    prompt += ' ###'
    prediction = openai.ChatCompletion.create(
                    engine='AutoConcierge',
                    messages=[{'role': 'user', 'content': context + prompt}],
                    max_tokens=150, temperature=0.65)
    return prediction['choices'][0]['message']['content']


def query_confirm(prompt):
    #sleep(60)
    context = '''
    Turn the predicates to the sentence that is confirming the user demands.
    predicate "query" means the customer wants you to provide this kind of information.
    for query('name'), it's okay to omit it to make the sentence natural.

    *example*

    query('name'), require('food type', 'Mexican'), require('establishment', 'restaurant'), require('price range', 'cheap') -> Okay, a cheap Mexican restaurant.

    query('name'), prefer('seafood'), require('price range', 'any') -> Seafood, and the price doesn't matter, I see.

    prefer('spicy'), not_require('food type', 'Indian'), query('address') -> You like spicy food, but not the Indian cuisine, right? I will provide you the address as well.

    view_history(3) -> The third place I recommended, I see.

    another_option('yes') -> Sure, let me check if there is any other choices that satisfy your requirement.

    *start*

    '''

    prompt += ' ->'
    prediction = openai.ChatCompletion.create(
                    engine='AutoConcierge',
                    messages=[{'role': 'user', 'content': context + prompt}],
                    max_tokens=100, temperature=1)
    return prediction['choices'][0]['message']['content']


def change_mind_confirm(prompt):
    #sleep(60)
    context = '''
    Turn the predicates to the sentence with a confirming tone, as if the customer has expressed the preference of these requirements in the past, but then they may change their mind. Use the sentences like \"Do you still like ...\" or \"Are you still considering\", etc.

    Do not use any predicate form in the output.

    *example*

    ask_still_want('food type', 'Mexican'). ask_still_want('food type','Indian'). ask_still_prefer('spicy'). -> Do you still want Indian or Mexican food that are spicy?

    ask_still_want('food type', 'pizza'). ask_still_want('food type', 'Italian'). ask_still_prefer('pizza'). -> Are you still seeking pizza or a place serving Italian cuisine?

    ask_still_want('food type', 'Indian'). ask_still_want('food type','Chinese'). ask_still_want('food type','Thai'). ask_still_want('food type','Japanese'). -> Do you still want to find a eatery with Inidian, Thai, Chinese or Japanese food?

    *start*

    '''

    prompt += ' ->'
    prediction = openai.ChatCompletion.create(
                    deployment_id="AutoConcierge",
                    messages=[{'role': 'user', 'content': context + prompt}],
                    max_tokens=100, temperature=0.8)
    return prediction['choices'][0]['message']['content']


def sentence_diversity(prompt):
    #sleep(60)
    context = '''
    Rewrite the sentence in a different expression.
    Filter out all the predicates (like require(cuisine, Indian)) in the input and make it natural language expressions.
    Do not mention the word "restaurant" if there is no clue saying it's a restaurant.
    Do not ignore some words like "still", "yet", "can be"

    *example*

    What can I do for you, sir? -> Hello, what can I help you today?

    What kind of food do you prefer? -> What type of cuisine are you looking for?

    Sorry, I didn't get what you mean. -> Sorry, I didn't understand. Could you please say that again?

    You are welcome. It's my pleasure to help. -> It's my pleasue to be of service.

    Do you still want Chinese or Japanese food? -> Are you still looking for Chinese or Japanese food?

    *start*

    '''

    prompt += ' ->'
    prediction = openai.ChatCompletion.create(
                    engine='AutoConcierge',
                    messages=[{'role': 'system', 'content': 'Please complete the following task. Not that the sentence meaning should not be changed.'},
                            {'role': 'user', 'content': context + prompt}],
                    max_tokens=200, temperature=0.5)
    return prediction['choices'][0]['message']['content']


def preference_classify(classes, prompt):
    #sleep(60)
    context = '''
    Below lists different types of cuisines available. For the input food, please choose one or more categories of cuisines that serves this type of food.
    Note that the output should be among the following list.

    *list*

    '''
    context += classes + '\n'
    context += '''
    
    *example*

    Input: curry -> Output: Indian, Thai

    Input: pizza -> Output: Italian

    Input: taco -> Output: Mexican

    Input: noodle -> Output: Chinese, Thai, Japanese

    Input: Shawarma -> Output: Halal

    Input: cuppuccino -> Output: coffee

    Input: cocktail -> Output: bar

    Input: drink -> Output: coffee, smoothie, bubble tea

    *start*

    Input: 
    '''

    prompt += ' -> Output: '
    prediction = openai.ChatCompletion.create(
                    engine='AutoConcierge',
                    messages=[{'role': 'user', 'content': context + prompt}], 
                    max_tokens=10, temperature=1)

    return prediction['choices'][0]['message']['content']


def chat(prompt):
    instruct = 'You are now a human concierge of restaurant recommendation. One customer comes to chat with you. Behave as a human with greeting and do simple chat. You can also discuss with the user for general topics, sports, news or entertainments, but don\'t provide make-up information. Finally you should lead the topic back into the restaurant recommendation. If they are going to leave, just let them leave.'
    #sleep(60)
    prediction = openai.ChatCompletion.create(
                    engine='AutoConcierge',
                    messages=[{'role': 'system', 'content': instruct},
                            {'role': 'user', 'content': prompt}],
                    max_tokens=300, temperature=0)
    output = prediction['choices'][0]['message']['content']
    return output


def irrelevant_reply(prompt):
    instruct = 'You are now a human concierge of restaurant recommendation helping with recommending restaurants, pubs, food shops, etc. One customer comes and ask you some questions that is irrelevant and beyond your expertise. Behave as a human with polite response. Make the reply short and concise.'
    #sleep(60)
    prediction = openai.ChatCompletion.create(
                    engine='AutoConcierge',
                    messages=[{'role': 'system', 'content': instruct},
                            {'role': 'user', 'content': prompt}],
                    max_tokens=50, temperature=1)
    output = prediction['choices'][0]['message']['content']
    return output


def same_name(prompt, name_list):
    #sleep(60)
    instruct = 'You are a classifier with a vocabulary of below: ' + ';'.join(name_list) + '. Choose the best match string of the input given by user. Only give the answer and do not explain.'
    context = ''
    
    prediction = openai.ChatCompletion.create(
                    engine='AutoConcierge',
                    messages=[{'role': 'system', 'content': instruct},
                            {'role': 'user', 'content': prompt}],
                    max_tokens=10, temperature=1)
    output = prediction['choices'][0]['message']['content']
    return output


if __name__ == "__main__":
    prompt = 'require(\'food type\',\'Japanese\'). prefer(\'sushi\').'
    print(change_mind_confirm(prompt))
    #result = predicate_gen(prompt)
    #prompt = 'require(name,Mellina). require(establishment, restaurant). require(food type, French). require(family-friendly, yes).'
    #result = sentence_gen(prompt)
    # _, context_list = get_predicates()
    # names = [x[2] for x in context_list if x[0] == 'name']
    # print(names)
    # name = 'bagel'
    # chosen = same_name(name, names)
    # print(chosen)