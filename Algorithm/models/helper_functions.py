import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

from keras.optimizers import Adam
from keras.callbacks import ReduceLROnPlateau


def train_and_evaluate_model(model, x_train, y_train,
                             x_val, y_val, x_test, y_test,
                             epochs=100, verbose=True,
                             with_reduce_on_plateu=False):
    start_time = time.time()

    model.compile(optimizer=Adam(), loss='mse')
    if verbose:
        model.summary()
        print()

    callbacks = []
    if with_reduce_on_plateu:
        callbacks.append(ReduceLROnPlateau(monitor='val_loss',
                                           patience=50, min_lr=1e-6))

    hist = model.fit(x_train, y_train,
                     validation_data=(x_val, y_val),
                     epochs=epochs,
                     callbacks=callbacks,
                     verbose=verbose)

    train_error = model.evaluate(x_train, y_train, verbose=0)
    print('Train error:', train_error)

    val_error = model.evaluate(x_val, y_val, verbose=0)
    print('Val error:', val_error)

    test_error = model.evaluate(x_test, y_test, verbose=0)
    print('Test error:', test_error)

    print('Execution time', round(time.time() - start_time, 2), 'seconds')

    if verbose:
        show_loss(hist.history)


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


def run_full_backtesting(data_provider, models):
    df_countries, benchmark = data_provider.get_etf_data()
    days_to_recalculate = data_provider.get_days_to_recalculate()
    dates_for_test = days_to_recalculate[-58:]

    dates_for_test.insert(29, df_countries.index.values[-1])
    df_prices_test = df_countries[dates_for_test[0]:]
    df_returns_test = np.log(df_prices_test).diff().fillna(0)

    benchmark_test = benchmark[dates_for_test[0]:]
    benchmark_returns = np.log(benchmark_test).diff().dropna()
    total_returns_dict = {'Benchmark': benchmark_returns}

    cum_benchmark_returns = (1 + benchmark_returns).cumprod() - 1
    cum_benchmark_returns.loc[dates_for_test[0]] = 0
    cum_benchmark_returns.sort_index(inplace=True)
    cum_total_returns_dict = {'Benchmark': cum_benchmark_returns}

    for key, (model, x_test) in models.items():
        total_returns, cum_total_returns = calculate_returns_for_model(
            model, x_test, dates_for_test, df_returns_test)

        total_returns_dict[key] = total_returns
        cum_total_returns_dict[key] = cum_total_returns

    plt.figure(figsize=(20, 5))
    for key, cum_total_returns in cum_total_returns_dict.items():
        plt.plot(cum_total_returns, label=key)
    plt.legend()
    plt.title('Returns comparison')
    plt.show()

    df_results = pd.DataFrame(columns=['Annual Returns',
                                       'Annual Volatility',
                                       'Sharpe Ratio',
                                       'Sortino Ratio',
                                       'Max Drawdown',
                                       'Max Time Under Water',
                                       'Calmar Ratio',
                                       'Information Ratio'])
    for key, total_returns in total_returns_dict.items():
        if key != 'Benchmark':
            calculate_metrics(total_returns, df_results, key,
                              total_returns_dict['Benchmark'])
        else:
            calculate_metrics(total_returns, df_results, key)

    df_results = df_results.astype(float).round(4)
    return df_results


def calculate_returns_for_model(model, x_test, dates_for_test,
                                df_returns_test):
    predictions = model.predict(x_test)
    total_returns, cum_total_returns = calculate_returns_for_predictions(
        predictions, dates_for_test, df_returns_test)
    return total_returns, cum_total_returns


def calculate_returns_for_predictions(predictions, dates_for_test,
                                      df_returns_test):
    # Allows long only allocations
    predictions[predictions < 0] = 0

    # Rescale to sum 1
    predictions_sum = predictions.sum(axis=1).reshape(predictions.shape[0], 1)
    predictions = np.divide(predictions, predictions_sum)

    predictions_df = pd.DataFrame(predictions,
                                  index=dates_for_test)
    predictions_df = predictions_df.reindex(index=df_returns_test.index)
    # Fill the entire month with predicted weights
    predictions_df = predictions_df.ffill()

    summed_returns = (df_returns_test.values *
                      predictions_df.values).sum(axis=1)
    total_returns = pd.Series(index=df_returns_test.index,
                              data=summed_returns)

    # Deduce transaction fees from returns on days of rebalancing
    transaction_fees = calculate_transaction_fees(predictions, dates_for_test)
    total_returns[transaction_fees.index] -= transaction_fees

    cum_total_returns = (1 + total_returns).cumprod() - 1
    cum_total_returns.loc[dates_for_test[0]] = 0
    cum_total_returns.sort_index(inplace=True)

    return total_returns, cum_total_returns


def calculate_transaction_fees(predictions, dates_for_test, fee_value=0.003):
    turnover = pd.DataFrame(predictions, index=dates_for_test)
    turnover = turnover.diff()  # Calculate delta/turnover

    # Use complete weights for initial portfolio
    turnover.iloc[0, :] = predictions[0]
    turnover = turnover.abs().sum(axis=1)

    transaction_fees = turnover*fee_value  # Transaction fees as pct
    return transaction_fees


def daily_to_annual_returns(daily_returns):
    daily_returns.iloc[0] = 0
    tot_ret = (daily_returns + 1).prod() - 1

    init_date = daily_returns.index[0]
    end_date = daily_returns.index[-1]
    fyears = (end_date - init_date) / pd.Timedelta(days=365, hours=6)

    anual_ret = np.power(tot_ret + 1, 1/fyears) - 1
    return anual_ret


def calculate_metrics(df_returns, df_results, name, benchmark_returns=None):
    annual_returns = daily_to_annual_returns(df_returns)
    annual_volatility = df_returns.std()*np.sqrt(252)
    annual_sharpe = annual_returns/annual_volatility

    if len(df_results.columns) == 3:
        df_results.loc[name, :] = [annual_returns,
                                   annual_volatility,
                                   annual_sharpe]
        return

    annual_negative_volatility = df_returns[df_returns < 0].std()*np.sqrt(252)
    annual_sortino = annual_returns/annual_negative_volatility

    cum_total_returns = (1 + df_returns).cumprod()
    peak = cum_total_returns.expanding(min_periods=1).max()
    drawdowns = (cum_total_returns/peak)-1
    max_drawdown = drawdowns.min()

    time_under_water = calculate_time_under_water(cum_total_returns)
    max_time_under_water = time_under_water.max()

    annual_calmar_ratio = annual_returns/abs(max_drawdown)

    information_ratio = 0
    if benchmark_returns is not None:
        information_ratio = calculate_information_ratio(
            df_returns, benchmark_returns)

    df_results.loc[name, :] = [annual_returns, annual_volatility,
                               annual_sharpe, annual_sortino,
                               max_drawdown, max_time_under_water,
                               annual_calmar_ratio, information_ratio]


def calculate_time_under_water(cum_total_returns):
    under_water = (cum_total_returns <
                   cum_total_returns.cummax()).astype(float)

    cut_uw = under_water[under_water == 0]
    if cut_uw.index[-1] != under_water.index[-1]:
        cut_uw.loc[under_water.index[-1]] = 0

    tuw = pd.Series(np.zeros(under_water.shape), index=under_water.index)
    current = cut_uw.index[0]

    for idate in cut_uw.index[1:]:
        tuw.loc[current:idate] = under_water[current:idate].cumsum()
        current = idate

    return tuw


def calculate_information_ratio(df_returns, benchmark_returns):
    init_date = benchmark_returns.index[0]
    end_date = benchmark_returns.index[-1]
    years_in = (end_date - init_date) / pd.Timedelta(days=365, hours=6)
    bdays_year = int(benchmark_returns.shape[0]/years_in)

    active_dayret = df_returns - benchmark_returns
    active_dayret.dropna().head()
    tracking_error = np.sqrt(bdays_year) * active_dayret.std()
    inform_ratio = (bdays_year * active_dayret.mean()) / tracking_error
    return inform_ratio
