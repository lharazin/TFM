import numpy as np
import pandas as pd
import cvxpy as cp


class PortfolioOptimizer:

    def get_optimal_portfolio(self, data_period, w, constraints):
        returns = np.log(data_period).diff().dropna()
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

    def get_normal_constraints(self, acwi_weights):
        w = cp.Variable(acwi_weights.shape[1])

        constraints = [cp.sum(w) == 1]
        i = 0

        for country in acwi_weights.columns:
            weights = acwi_weights.loc[:, country].values[0]

            # Min weight between 0.1% and 25%
            min_weight = round(weights*0.5/100, 3)
            if min_weight < 0.001:
                min_weight = 0.001

            # Max weight between 3% to 75%
            max_weight = round(weights*2/100, 3)
            if max_weight < 0.03:
                max_weight = 0.03
            elif max_weight > 0.75:
                max_weight = 0.75

            constraints += [
                w[i] >= min_weight,
                w[i] <= max_weight
            ]
            i += 1
        return w, constraints

    def get_tight_constraints(self, acwi_weights):
        w = cp.Variable(acwi_weights.shape[1])

        constraints = [cp.sum(w) == 1]
        i = 0

        for country in acwi_weights.columns:
            weights = acwi_weights.loc[:, country].values[0]

            # Min weight between 0.1% and 35%
            min_weight = round(weights*0.7/100, 3)
            if min_weight < 0.001:
                min_weight = 0.001

            # Max weight between 2% to 70%
            max_weight = round(weights*1.5/100, 3)
            if max_weight < 0.02:
                max_weight = 0.02
            elif max_weight > 0.7:
                max_weight = 0.7

            constraints += [
                w[i] >= min_weight,
                w[i] <= max_weight
            ]
            i += 1
        return w, constraints

    def get_loose_constraints(self, acwi_weights):
        w = cp.Variable(acwi_weights.shape[1])

        constraints = [cp.sum(w) == 1]
        i = 0

        for country in acwi_weights.columns:
            weights = acwi_weights.loc[:, country].values[0]

            # Min weight between 0% and 15%
            min_weight = round(weights*0.3/100, 4)
            if min_weight <= 0.001:
                min_weight = 0

            # Max weight between 4% to 80%
            max_weight = round(weights*3/100, 3)
            if max_weight < 0.04:
                max_weight = 0.04
            elif max_weight > 0.8:
                max_weight = 0.8

            constraints += [
                w[i] >= min_weight,
                w[i] <= max_weight
            ]
            i += 1
        return w, constraints

    def get_constraints_for_ranking(self, acwi_weights, ranked_countries):
        w = cp.Variable(acwi_weights.shape[1])
        constraints = [cp.sum(w) == 1]
        i = 0

        for country in acwi_weights.columns:
            benchmark_weight = acwi_weights.loc[:, country].values[0]
            benchmark_weight = round(benchmark_weight/100, 3)
            rank = ranked_countries[country]

            if i < 3:  # Special constraints for US, Japan and UK
                if rank < 10:
                    min_weight = benchmark_weight
                    max_weight = benchmark_weight*2
                    if max_weight > 0.7:
                        max_weight = 0.7
                else:
                    min_weight = benchmark_weight*0.5
                    max_weight = benchmark_weight
            else:
                min_weight = 0.001
                max_weight = 0.03

            constraints += [
                w[i] >= min_weight,
                w[i] <= max_weight
            ]

            if i >= 3 and rank > 0:
                higher_ranked_country = ranked_countries[
                    ranked_countries == rank-1].index[0]
                higher_ranked_country_idx = acwi_weights.columns.get_loc(
                    higher_ranked_country)
                if higher_ranked_country_idx >= 3:
                    constraints.append(w[i] <= w[higher_ranked_country_idx])
                elif rank > 1:
                    higher_ranked_country = ranked_countries[
                        ranked_countries == rank-2].index[0]
                    higher_ranked_country_idx = acwi_weights.columns.get_loc(
                        higher_ranked_country)
                    if higher_ranked_country_idx >= 3:
                        constraints.append(
                            w[i] <= w[higher_ranked_country_idx])
            i += 1

        return w, constraints
