import pandas as pd
from datetime import datetime
from keras.models import Sequential
from keras.layers import Input, Flatten, Dense
from keras.regularizers import L2
from DataProviderLite import DataProviderLite


def handler(event, context):
    """ Daily DNN Model Lambda – calculates portfolio weights
    from pre-trained DNN Model. """

    read_date = datetime.today().date()
    no_months = 6
    limit_date = (read_date - pd.DateOffset(months=12)).strftime('%Y-%m-%d')
    print('Reading indicators from', limit_date, 'to', read_date)

    data_provider = DataProviderLite()
    data_provider.initialize_current_correlations(limit_date, read_date)
    print('Initialized correlations')

    x_today = data_provider.calculate_principal_component_from_calendar(
        read_date, no_months, limit_date)
    x_today = x_today.values.reshape(1, 6, 27)
    print('Prepared input data of shape', x_today.shape)

    loaded_dnn_model = Sequential((
        Input(shape=(6, 27)),
        Flatten(),
        Dense(32, activation='relu',
              kernel_regularizer=L2(0.2)),
        Dense(27, activation='softmax')
    ))
    loaded_dnn_model.load_weights('daily_dnn_model_from_calendar.weights.h5')
    print('Loaded Keras model')

    predicted_weights = loaded_dnn_model.predict(x_today, verbose=False)
    predictions = pd.Series(predicted_weights[0],
                            index=data_provider.selected_countries)
    predictions['Russia'] = 0  # Russia is uninvestible after 02/2022
    predictions = predictions/predictions.sum()

    print('Portfolio weights')
    print(predictions)
