import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

from keras.optimizers import Adam
from keras.callbacks import EarlyStopping, ReduceLROnPlateau


def show_loss(hd):
    epochs = range(1, len(hd['loss'])+1)

    plt.figure(figsize=(15, 5))
    plt.subplot(1, 2, 1)
    plt.plot(epochs, hd['loss'], "r", label="train")
    plt.plot(epochs, hd['val_loss'], "b", label="valid")
    plt.grid(True)
    plt.xlabel("epoch")
    plt.ylabel("loss")
    plt.title("Loss")
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(epochs, hd['loss'], "r", label="train")
    plt.plot(epochs, hd['val_loss'], "b", label="valid")
    plt.grid(True)
    plt.xlabel("epoch")
    plt.ylabel("loss")
    plt.yscale('log')  # Set y-axis to logarithmic scale
    plt.title("Loss log")
    plt.legend()
    plt.show()


def train_and_evaluate_model(model, x_train, y_train,
                             x_val, y_val, x_test, y_test,
                             epochs=200, learning_rate=1e-3,
                             with_early_stopping=False):
    start_time = time.time()

    model.compile(optimizer=Adam(learning_rate=learning_rate),
                  loss='mean_squared_error')
    model.summary()
    print()

    callbacks = []
    if with_early_stopping:
        callbacks.append(EarlyStopping(monitor='val_loss',
                                       patience=100))

    callbacks.append(ReduceLROnPlateau(monitor='val_loss',
                                       patience=50, min_lr=1e-6))

    hist = model.fit(x_train, y_train,
                     validation_data=(x_val, y_val),
                     epochs=epochs,
                     callbacks=callbacks)

    train_error = model.evaluate(x_train, y_train, verbose=0)
    print('Train error:', train_error)

    val_error = model.evaluate(x_val, y_val, verbose=0)
    print('Val error:', val_error)

    test_error = model.evaluate(x_test, y_test, verbose=0)
    print('Test error:', test_error)

    print('Execution time', round(time.time() - start_time, 2), 'seconds')

    show_loss(hist.history)


def calculate_returns_for_model(model, x_test, dates_for_test,
                                df_returns_test, selected_countries):
    predictions = model.predict(x_test)

    # Rescale to sum 1
    predictions_sum = predictions.sum(axis=1).reshape(predictions.shape[0], 1)
    predictions = np.divide(predictions, predictions_sum)

    predictions_df = pd.DataFrame(predictions,
                                  index=dates_for_test,
                                  columns=selected_countries)
    predictions_df = predictions_df.reindex(index=df_returns_test.index)
    # Fill the entire month with predicted weights
    predictions_df = predictions_df.ffill()

    summed_returns = (df_returns_test.values *
                      predictions_df.values).sum(axis=1)
    total_returns = pd.Series(index=df_returns_test.index,
                              data=summed_returns)
    cum_total_returns = (1 + total_returns).cumprod() - 1
    cum_total_returns.loc[dates_for_test[0]] = 0
    cum_total_returns.sort_index(inplace=True)

    return total_returns, cum_total_returns


def daily_to_annual_returns(daily_returns):
    daily_returns.iloc[0] = 0
    tot_ret = (daily_returns + 1).prod() - 1

    init_date = daily_returns.index[0]
    end_date = daily_returns.index[-1]
    fyears = (end_date - init_date) / pd.Timedelta(days=365, hours=6)

    anual_ret = np.power(tot_ret + 1, 1/fyears) - 1
    return anual_ret


def calculate_metrics(df_returns, df_results, name):
    annual_returns = daily_to_annual_returns(df_returns)
    annual_volatility = df_returns.std()*np.sqrt(252)
    annual_sharpe = annual_returns/annual_volatility

    df_results.loc[name, :] = [annual_returns,
                               annual_volatility, annual_sharpe]
