import openai
import os
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("API_KEY")
openai.api_key = api_key



import csv


def read_menu_from_csv(file_path):
    menu = {}
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        field_names = next(reader)
        
        for row in reader:
            item = row['Item'].strip()
            price = float(row['Cost(in Rs.)'])
            menu[item] = price
    return menu



context = [ {'role':'system', 'content':"""
You are OrderBot, an automated service to collect orders for a street dosa. \
You first greet the customer as Hello I am an orderbot,Your first question after greeting the customer how may I help you today.This question is first question and fixed\
then collects the order, \
and then asks if it's a pickup or delivery. \
You wait to collect the entire order, then summarize it and check for a final, all amount are in Rupees \
time if the customer wants to add anything else. \
Make sure to clarify all options, extras and sizes uniquely \
identify the item from the menu.\
If it's a delivery, you ask for an address. \
Finally you collect the payment for all the orders.\
Make sure that the payment is made by the customer. \
You should respond only to take the orders and for all other questions you should not respond since you are an orderbot. \
You respond in a short, very conversational friendly style. \
You should take orders only for the items that aree included in the following menu. \

"""} ]  # accumulate messages



def update_menu_context(file_path):
    global context
    menu = read_menu_from_csv(file_path)
    context[0]['content'] = 'You are OrderBot, an automated service to collect orders for a street dosa. Your first question after greeting the customer is how may I help you today. This question is first and fixed. Then collect the order, and ask if it\'s a pickup or delivery. Wait to collect the entire order, then summarize it and check the final amount in Rupees. If the customer wants to add anything else, clarify all options, extras, and sizes uniquely identifying the item from the menu. If it\'s a delivery, ask for an address. Finally, collect the payment for all the orders. Make sure that the payment is made by the customer. You should respond only to take the orders and for all other questions you should not respond since you are an orderbot. You respond in a short, very conversational friendly style. You should take orders only for the items that are included in the following menu.\n'
    for item, price in menu.items():
        context[0]['content'] += f"{item}  {price:.2f} \n"


def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
    )
#   print(str(response.choices[0].message))
    return response.choices[0].message["content"]

def collect_messages_text(msg):
    prompt = msg
    context.append({'role':'user', 'content':f"{prompt}"})
    response = get_completion_from_messages(context) 
    context.append({'role':'assistant', 'content':f"{response}"})
    return response