
from math import sqrt
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout

import numpy as np
import pandas as pd
import time
import datetime

import requests
import tweepy
from textblob import TextBlob

data = pd.read_csv("new_data.csv")
    
datag = data[['Price','Sentiment']].groupby(data['Time']).mean()
values = datag['Price'].values.reshape(-1,1)
sentiment = datag['Sentiment'].values.reshape(-1,1)
    
values = values.astype('float32')
sentiment = sentiment.astype('float32')

scaler = MinMaxScaler(feature_range=(0, 1))
scaled = scaler.fit_transform(values)
    
trial = np.concatenate((scaled,sentiment),axis =1)



#data.plot(x='Time', y='Price' ,figsize=(9,5), grid=True  )
#data.plot(x='Time', y='Sentiment' ,figsize=(9,5), grid=True  )


train_size = int(len(scaled) * 0.7)
test_size = len(scaled) - train_size
train, test = trial, trial[train_size:len(scaled),:]


def create_look_back(dataset, look_back, sentiment):
    dataX, dataY = [], []
    for i in range(len(dataset)):
        if i >= look_back:
            a = dataset[i-look_back:i, :]
            a = a.tolist()
            dataX.append(a)
            dataY.append(dataset[i, 0])
    return np.array(dataX), np.array(dataY)


look_back = 60
trainX, trainY = create_look_back(train, look_back, sentiment[0:train_size])
testX, testY = create_look_back(test, look_back, sentiment[train_size:len(scaled)])


regressor = Sequential()

# Adding the first LSTM layer and some Dropout regularisation
regressor.add(LSTM(units = 50, return_sequences = True, input_shape = (trainX.shape[1], 2)))
regressor.add(Dropout(0.2))

# Adding a second LSTM layer and some Dropout regularisation
regressor.add(LSTM(units = 50, return_sequences = True))
regressor.add(Dropout(0.2))

# Adding a third LSTM layer and some Dropout regularisation
regressor.add(LSTM(units = 50, return_sequences = True))
regressor.add(Dropout(0.2))

# Adding a fourth LSTM layer and some Dropout regularisation
regressor.add(LSTM(units = 50))
regressor.add(Dropout(0.2))

# Adding the output layer
regressor.add(Dense(units = 1))

# Compiling the RNN
regressor.compile(optimizer = 'adam', loss = 'mean_squared_error')

# Fitting the RNN to the Training set
regressor.fit(trainX, trainY, epochs = 1, batch_size = 64)
yhat = regressor.predict(testX)
plt.plot(yhat, label='predict')
plt.plot(testY, label='true')
plt.legend()
plt.show()

yhat_inverse = scaler.inverse_transform(yhat.reshape(-1, 1))
testY_inverse = scaler.inverse_transform(testY.reshape(-1, 1))

rmse_2 = sqrt(mean_squared_error(testY_inverse, yhat_inverse))
print('Test RMSE: %.3f' % rmse_2)
print(" ")

data = data[look_back+1:]
csv_insert = regressor.predict(trainX)
csv_insert_inverse = scaler.inverse_transform(csv_insert.reshape(-1, 1))
data['Prediction'] = csv_insert_inverse
data.to_csv("merge_data.csv", index = False)


def create_dataset_predict(dataset, look_back, sentiment):
    dataX = []
    for i in range(len(dataset) - look_back,len(dataset)-look_back+1):
            a = dataset[i:i+look_back, :]
            a = a.tolist()
            dataX.append(a)
    return np.array(dataX)


    
data = pd.read_csv("new_data.csv")
    
datag = data[['Price','Sentiment']].groupby(data['Time']).mean()
values = datag['Price'].values.reshape(-1,1)
sentiment = datag['Sentiment'].values.reshape(-1,1)
    
values = values.astype('float32')
sentiment = sentiment.astype('float32')
    
scaler = MinMaxScaler(feature_range=(0, 1))
scaled = scaler.fit_transform(values)
trial = np.concatenate((scaled,sentiment),axis =1)
    

predict_past = 0
real_past = 0
count = 0
true_trend = 0


#Open All the csv Files
n_name = "new_data.csv"
b_name = "live_bitcoin.csv"
t_name = "live_tweet.csv"
m_name = "merge_data.csv"
p_name = "prediction.csv"
f = open(n_name,"a")
f1 = open(b_name,"a")
f2 = open(t_name,"a")
f3 = open(m_name,"a")
f4 = open(p_name,"a")

#Define keys you want to collect from CoinMarketCap
keys = ["price_usd","24h_volume_usd","market_cap_usd","available_supply","total_supply","percent_change_1h","percent_change_24h","percent_change_7d"]
vals = [0]*len(keys)

#Twitter Credentials
consumer_key = "SK4PUk9IPvz05teH9jvx5T05s"
consumer_secret = "IAWBJtJbTDKzJbMUkDuG421UiXJFxvp1ZMvqMTDRd1BDFaqqJh"
access_token = "1669372777-NnUJmKSmcpJWQAM9H6w7kXjFyQW5glE9BF0ivIh"
access_token_secret = "23blDhmp314JAbFt0EGzCu9Ca0yTPyDqBrLqgoeehqDXu"

#Creating the authenticaton object
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

#Setting your access token and secret
auth.set_access_token(access_token, access_token_secret)

# Creating the API object while passing in auth information
api = tweepy.API(auth)
tweet = []
query = ["bitcoin","price"]
language = "en"



while True:
    
    count+=1
    
    predictX = create_dataset_predict(trial, look_back, sentiment)
    
    yhat = regressor.predict(predictX)
    
    yhat_inverse = scaler.inverse_transform(yhat.reshape(-1, 1))
    
    now = datetime.datetime.now()
    future = now + datetime.timedelta(minutes = 1)
    
    print("Predicted Price: ", end =" ")
    print(*yhat_inverse[0], end =" ")
    print(" for timestamps : ", end =" ")
    print(future.strftime("%y-%m-%d-%H-%M"))
    f4.write(future.strftime("%y-%m-%d-%H-%M"))
    f4.write(","+str(*yhat_inverse[0]))
    f4.write("\n")
    f4.flush()
    
    
    
    while datetime.datetime.now().strftime("%y-%m-%d-%H-%M")!=future.strftime("%y-%m-%d-%H-%M"):
        time.sleep(5)
    
    dataf = requests.get("https://api.coinmarketcap.com/v1/ticker/bitcoin/").json()[0]
    
    bkc = requests.get("https://blockchain.info/ticker").json()

    results = api.search(q=query, lang=language, tweet_mode="extended", count = 100)
    counter = 0
    sum = 0
    for i in results:
        counter+=1
        tweet.append(i.full_text)
        testimonial = TextBlob(i.full_text)
        sum+=testimonial.sentiment.polarity
    print("count is : ", counter)
    sum = sum/counter

    for d in dataf.keys():
        if d in keys:
            indx = keys.index(d)
            vals[indx] = dataf[d]
    for val in vals:
        f.write(val+",")
        f1.write(val+",")
        f3.write(val+",")
        
    #Write data in Merged Data csv.
    f.write("{},{},{}".format(bkc["USD"]["sell"],bkc["USD"]["buy"],bkc["USD"]["15m"]))
    f.write(","+datetime.datetime.now().strftime("%y-%m-%d-%H-%M"))
    f.write(","+str(sum))
    f.write("\n")
    f.flush()
    
    #Write data in Live Bitcoin csv.
    f1.write("{},{},{}".format(bkc["USD"]["sell"],bkc["USD"]["buy"],bkc["USD"]["15m"]))
    f1.write(","+datetime.datetime.now().strftime("%y-%m-%d-%H-%M"))
    f1.write("\n")
    f1.flush()

    #Write data in Live Twitter csv.
    f2.write(str(sum))
    f2.write(","+datetime.datetime.now().strftime("%y-%m-%d-%H-%M"))
    f2.write("\n")
    f2.flush()
    
    #Write data in Merge data csv
    #Write data in Live Twitter csv.
    f3.write("{},{},{}".format(bkc["USD"]["sell"],bkc["USD"]["buy"],bkc["USD"]["15m"]))
    f3.write(","+datetime.datetime.now().strftime("%y-%m-%d-%H-%M"))
    f3.write(","+str(sum))
    f3.write(","+str(*yhat_inverse[0]))
    f3.write("\n")
    f3.flush()
    
        
    data = pd.read_csv("new_data.csv")
    
    datag = data[['Price','Sentiment']].groupby(data['Time']).mean()
    values = datag['Price'].values.reshape(-1,1)
    sentiment = datag['Sentiment'].values.reshape(-1,1)
        
    values = values.astype('float32')
    sentiment = sentiment.astype('float32')
        
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(values)
    trial = np.concatenate((scaled,sentiment),axis =1)
    
    print("Real Price: ", end = " ")
    print(values[len(values)-1])
    if (((yhat_inverse-predict_past)<=0 and (values[len(values)-1] - real_past)<=0) or ((yhat_inverse-predict_past) >= 0 and (values[len(values)-1] - real_past)>=0)):
        true_trend+=1
    accuracy = (true_trend/count)*100
    predict_past = yhat_inverse
    real_past = values[len(values)-1]
    print("Accuracy is : ", end = " " )
    print(accuracy, end = " ")
    print("%")
    print("")
    