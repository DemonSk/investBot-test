import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import urllib.request, json
import datetime
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from keras.callbacks import ModelCheckpoint
from keras.models import load_model
from sklearn.metrics import mean_squared_error


def tickerfromuser(userTicker):
    data_source = 'alphavantage'

    if data_source == 'alphavantage':

        api_key = 'Api Key'

        ticker = userTicker

        url_string = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=%s&outputsize=full&apikey=%s"%(ticker,api_key)

        file_to_save = 'stock_market_data-%s.csv'%ticker

        with urllib.request.urlopen(url_string) as url:
            data = json.loads(url.read().decode())
            data = data['Time Series (Daily)']
            df = pd.DataFrame(columns=['Date','Low','High','Close','Open'])
            for k,v in data.items():
                date = datetime.datetime.strptime(k, '%Y-%m-%d')
                data_row = [date.date(),float(v['3. low']),float(v['2. high']),
                            float(v['4. close']),float(v['1. open'])]
                df.loc[-1,:] = data_row
                df.index = df.index + 1
        print('Data saved to : %s'%file_to_save)
        df.to_csv(file_to_save)

    ticker = pd.read_csv('stock_market_data-%s.csv'%ticker)

    ticker = ticker[['Date', 'Close']]

    ticker.Date = pd.to_datetime(ticker.Date, format ='%Y/%m/%d')

    ticker_length = len(ticker)
    new_ticker = ticker.loc[0:ticker_length//2]

    new_ticker = new_ticker.drop('Date', axis = 1)
    new_ticker = new_ticker.reset_index(drop = True)

    T = new_ticker.values
    T = T.astype('float32')
    T = np.reshape(T, (-1, 1))

    scaler = MinMaxScaler(feature_range = (0, 1))
    T = scaler.fit_transform(T)

    train_size = int(len(T) * 0.80)
    test_size = int(len(T) - train_size)
    train, test = T[0:train_size,:], T[train_size:len(T),:]


    def create_features(data, window_size):
        X, Y = [], []
        for i in range(len(data) - window_size - 1):
            window = data[i:(i + window_size), 0]
            X.append(window)
            Y.append(data[i + window_size, 0])
        return np.array(X), np.array(Y)

    window_size = 20
    X_train, Y_train = create_features(train, window_size)

    X_test, Y_test = create_features(test, window_size)

    X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))

    X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

    T_shape = T.shape
    train_shape = train.shape
    test_shape = test.shape

    def isLeak(T_shape, train_shape, test_shape):
        return not(T_shape[0] == (train_shape[0] + test_shape[0]))

    print(isLeak(T_shape, train_shape, test_shape))

    tf.random.set_seed(11)
    np.random.seed(11)

    model = Sequential()

    model.add(LSTM(units = 50, activation = 'relu',
                   input_shape = (X_train.shape[1], window_size)))
    model.add(Dropout(0.2))

    model.add(Dense(1, activation = 'linear'))
    model.compile(loss = 'mean_squared_error', optimizer = 'adam')

    filepath = 'saved_models/model_epoch_{epoch:02d}.hdf5'

    checkpoint = ModelCheckpoint(filepath = filepath,
                                 monitor = 'val_loss',
                                 verbose = 1,
                                 save_best_only = True,
                                 mode ='min'
                                )

    history = model.fit(X_train, Y_train, epochs = 100, batch_size = 20, validation_data = (X_test, Y_test),
                        callbacks = [checkpoint],
                        verbose = 1, shuffle = False)

    model.summary()

    best_model = load_model('saved_models/model_epoch_93.hdf5')

    train_predict = best_model.predict(X_train)

    Y_hat_train = scaler.inverse_transform(train_predict)

    test_predict = best_model.predict(X_test)

    Y_hat_test = scaler.inverse_transform(test_predict)

    Y_test = scaler.inverse_transform([Y_test])
    Y_train = scaler.inverse_transform([Y_train])
    Y_hat_train = np.reshape(Y_hat_train, newshape = len(Y_hat_train))
    Y_hat_test = np.reshape(Y_hat_test, newshape = len(Y_hat_test))

    Y_train = np.reshape(Y_train, newshape = len(Y_hat_train))
    Y_test = np.reshape(Y_test, newshape = len(Y_hat_test))

    Y = np.append(Y_train, Y_test)
    Y_hat = np.append(Y_hat_train, Y_hat_test)

    result_df = pd.DataFrame()

    result_df['Actual_Y'] = Y
    result_df['Predicted_Y'] = Y_hat

    return round(result_df['Predicted_Y'][0], 3)
