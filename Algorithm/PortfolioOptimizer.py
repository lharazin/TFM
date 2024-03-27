import numpy as np
import pandas as pd
import cvxpy as cp


class PortfolioOptimizer:

    def get_optimal_portfolio(self, data_period, acwi_weights):
        returns = np.log(data_period).diff().dropna()

        w = cp.Variable(acwi_weights.shape[1])
        constraints = self.get_constraints(w, acwi_weights)

        ret_data, risk_data, portfolio_weights = self.efficient_frontier(
            returns, w, constraints)

        sharpes = ret_data/risk_data
        idx = np.argmax(sharpes)
        optimal_portfolio = pd.Series(portfolio_weights[idx],
                                      index=returns.columns).round(3)

        return optimal_portfolio

    def efficient_frontier(self, returns, w, constraints, n_samples=20):
        sigma = returns.cov().values
        mu = np.mean(returns, axis=0).values
        gamma = cp.Parameter(nonneg=True)
        ret = mu.T @ w
        risk = cp.quad_form(w, sigma)

        prob = cp.Problem(cp.Maximize(ret - gamma*risk), constraints)
        risk_data = np.zeros(n_samples)
        ret_data = np.zeros(n_samples)
        gamma_vals = np.logspace(-1, 10, num=n_samples)

        portfolio_weights = []
        for i in range(n_samples):
            gamma.value = gamma_vals[i]
            prob.solve()
            risk_data[i] = np.sqrt(risk.value)
            ret_data[i] = ret.value
            portfolio_weights.append(w.value)
        return ret_data, risk_data, portfolio_weights

    def get_constraints(self, w, acwi_weights):
        constraints = [cp.sum(w) == 1]
        i = 0

        for country in acwi_weights.columns:
            weights = acwi_weights.loc[:, country].values[0]

            # Min weight between 0.1% and 30%
            min_weight = round(weights*0.5/100, 3)
            if min_weight < 0.001:
                min_weight = 0.001

            # Max weight between 3% to 70%
            max_weight = round(weights*2/100, 3)
            if max_weight < 0.03:
                max_weight = 0.03
            elif max_weight > 0.7:
                max_weight = 0.7

            constraints += [
                w[i] >= min_weight,
                w[i] <= max_weight
            ]
            i += 1

        return constraints
