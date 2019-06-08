"""
created by diksha singla on 08-06-2019
"""

import requests
import json
import os
import pyowm
import wikipedia
import urllib.request

from database import insertdata,get_time
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "chatbot.json"

import dialogflow_v2 as dialogflow
dialogflow_session_client = dialogflow.SessionsClient()
PROJECT_ID = "chatbot-fwfuum"

from gnewsclient import gnewsclient
client=gnewsclient.NewsClient(max_results=3)

def get_news(parameters):
    client.topic=parameters.get('news_type')
    client.language=parameters.get('language')
    client.location=parameters.get('geo-country', '')
    return client.get_news()

def detect_intent_from_text(text, session_id, language_code='en'):
    session = dialogflow_session_client.session_path(PROJECT_ID, session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = dialogflow_session_client.detect_intent(session=session, query_input=query_input)
    return response.query_result

def fetch_reply(msg,session_id):
    response=detect_intent_from_text(msg,session_id)
    if response.intent.display_name=='get_news':
        news=get_news(dict(response.parameters))
        news_str='Here are your news:'
        for row in news: 
            news_str+="\n\n{}\n\n{}\n\n".format(row['title'],row['link']) 
        return news_str

    elif response.intent.display_name=='get_weather':
        owm = pyowm.OWM('2242ac01869a406a63e2cf1f430724ef')
        weather=dict(response.parameters)
        city=weather.get("geo-city")
        country=weather.get("geo-country")
        if country!='':
            observation = owm.weather_at_place(city+','+country)
        else:
            observation = owm.weather_at_place(city+',india')
        w = observation.get_weather()
        wind=w.get_wind()['speed']
        humidity=w.get_humidity()
        temprature=w.get_temperature('celsius')['temp']
        status=w.get_detailed_status()
        userdata={'geo-city':city,'geo-country':country,'time':get_time()}
        insertdata(userdata)
        weather="\nstatus: {}\n".format(status)
        weather+="\ntemprature: {} °c\n".format(temprature)
        weather+="\nhumidity : {}\n".format(humidity)
        weather+="\nwind speed: {}\n".format(wind)
        return weather
        
    elif response.intent.display_name=="get_makeup":
        makeup=dict(response.parameters)
        product=makeup.get('product_type')
        brand=makeup.get('brand')
        if product!='' and brand!='':
            URL="http://makeup-api.herokuapp.com/api/v1/products.json?brand="+brand+"&product_type="+product
            userdata={'product':product,'brand':brand,'time':get_time()}
            insertdata(userdata)
        elif product!='' and brand=='':
            URL="http://makeup-api.herokuapp.com/api/v1/products.json?product_type="+product
            userdata={'product':product,'time':get_time()}
            insertdata(userdata)
        else:
            URL="http://makeup-api.herokuapp.com/api/v1/products.json?brand="+brand
            userdata={'brand':brand,'time':get_time()}
            insertdata(userdata)
        request=requests.get(URL)
        content_data=request.json()
        if len(content_data)!=0:
            data=''
            for i in range(0,2,1):
                data+="Product Name and Price : {} {}".format(content_data[i]['name'],content_data[i]['price'])
                data+="Product Description\n {}\n".format(content_data[i]['description'])
                data+="Product Link\n {}\n\n".format(content_data[i]['product_link'])
            print(len(data))
            return data
        else:
            return "Product not available"

    elif response.intent.display_name=="get_dictionary":
        dictionary=dict(response.parameters)
        app_id="230078d5"
        app_key="52e933da09c08cfc07c21ad20a32b412"
        endpoint = "entries"
        language_code = "en-us"
        word_id =dictionary.get('word_type')
        url = "https://od-api.oxforddictionaries.com/api/v2/" + endpoint + "/" + language_code + "/" + word_id.lower()
        r = requests.get(url, headers = {"app_id": app_id, "app_key": app_key})
        content_data=r.json()
        if len(content_data)!=0:
            data="Meaning of {} is {}".format(word_id,content_data["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]["definitions"][0])
            userdata={'word':word_id,'time':get_time()}
            insertdata(userdata)
            return data
        else:
            return "No meaning found"

    elif response.intent.display_name=="get_company":
        company=dict(response.parameters)
        company_name=company.get('company_name')
        company_data=wikipedia.summary(company_name, sentences=2)
        page_image = wikipedia.page(company_name).images[0]
        return company_data,page_image,"type2"

    else:
        return response.fulfillment_text


def get_intent(msg,session_id):
    response=detect_intent_from_text(msg,session_id)
    return response.intent.display_name