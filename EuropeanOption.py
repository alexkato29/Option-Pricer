import math


class Option:
    # Options REQUIRE: a type (call or put), a ticker, strike price, and expiration (in days to exp)
    def __init__(self, type, underlying, strike, time, rate, vol, div, debug=False):
        self.type = type
        self.underlying = underlying
        self.strike = strike
        self.time = time / 365
        self.rate = rate / 100
        self.vol = vol / 100
        self.div = div / 100
        self.price = self.get_price(debug)
        self.greeks = self.compute_greeks(debug)  # Delta, Gamma, Vega, Theta, Rho

    def __str__(self):
        return str.format("Price: %f\nDelta: %f\nGamma: %f\nVega: %f\nTheta: %f\nRho: %f\n"
                          % (self.price, self.greeks[0], self.greeks[1], self.greeks[2], self.greeks[3], self.greeks[4]))

    def is_call(self):
        return self.type == "call"

    # Returns the value of the option depending on if it is a call or put
    def get_price(self, debug=False):
        if self.is_call():
            return self.get_call(debug)
        return self.get_put(debug)

    # Computes the standard formula: C = S*exp(-qt)*N(d1) - Ke^(-rt)*N(d2)
    # N(d1) is the future value of the stock iff it expires at or above strike
    # N(d2) is the probability it expires at or above the strike
    def get_call(self, debug):
        d1 = self.get_d1()
        d2 = self.get_d2()
        n1 = self.n(d1)
        n2 = self.n(d2)
        spot = self.underlying
        rf_rate = self.rate
        strike = self.strike
        time = self.time

        present_value = spot * n1 * math.exp(-self.div*time)
        discounted_value = strike * math.exp(-1 * rf_rate * time) * n2

        if debug:
            print("d1: %f\nN(d1): %f\nd2: %f\nN(d2): %f\n" % (d1, n1, d2, n2))

        return present_value - discounted_value

    def get_put(self, debug):
        d1 = self.get_d1()
        d2 = self.get_d2()
        n1 = self.n(-d1)
        n2 = self.n(-d2)
        spot = self.underlying
        rf_rate = self.rate
        strike = self.strike
        time = self.time

        present_value = spot * n1 * math.exp(-self.div * time)
        discounted_value = strike * math.exp(-1 * rf_rate * time) * n2

        if debug:
            print("d1: %f\nN(d1): %f\nd2: %f\nN(d2): %f\n" % (d1, n1, d2, n2))

        return discounted_value - present_value

    # Computes d1 using the formula: d1 = [ln(S/K) + t(r-q-(sigma^2/2))]/sigma * sqrt(t)
    def get_d1(self):
        rate_of_growth = math.log(self.underlying / self.strike)
        mean = (self.rate - self.div + (math.pow(self.vol, 2) / 2)) * self.time
        denominator = 1 / (self.vol * math.sqrt(self.time))

        return denominator * (rate_of_growth + mean)

    # N(d2) is the probability that at expiration, the spot is at or above strike
    # d2 is the -Z score
    def get_d2(self):
        d1 = self.get_d1()
        to_sub = self.vol * math.sqrt(self.time)

        return d1 - to_sub

    # Cumulative distribution function for the standard normal distribution
    @staticmethod
    def n(z):
        return (1.0 + math.erf(z / math.sqrt(2.0))) / 2.0

    @staticmethod
    def n_prime(z):
        # N'(d1) = (1/sqrt(2pi))*exp(-d1^2/2)
        # Integral is just undone. N' is quite trivial
        return (1 / math.sqrt(2 * math.pi)) * math.exp(-math.pow(z, 2) / 2)

    """
    Computation is quite long for some but relatively simple.
    
    (All of the following are partials)
    delta = dC/dS
    gamma = d^2C/dS^2
    theta = dC/dT
    vega = dC/dSigma
    rho = dC/dR
    """
    def compute_greeks(self, debug):
        d1 = self.get_d1()
        d2 = self.get_d2()

        gamma = math.exp(-self.div * self.time) * self.n_prime(d1) / (
                    self.underlying * self.vol * math.sqrt(self.time))
        vega = (1 / 100) * self.underlying * math.exp(-self.div * self.time) * math.sqrt(
            self.time) * self.n_prime(d1)

        if self.is_call():
            delta = math.exp(-self.div * self.time) * self.n(d1)
            theta_1 = self.underlying * self.vol * math.exp(-self.div * self.time) * self.n_prime(d1) / (
                        2 * math.sqrt(self.time))
            theta_2 = self.rate * self.strike * math.exp(-self.rate * self.time) * self.n(d2)
            theta_3 = self.div * self.underlying * math.exp(-self.div * self.time) * self.n(d1)
            theta = (1 / 365) * (theta_3 - theta_1 - theta_2)
            rho = (1 / 100) * self.strike * self.time * math.exp(-self.rate * self.time) * self.n(d2)

        else:
            delta = math.exp(-self.div * self.time) * (self.n(d1) - 1)
            theta_1 = self.underlying * self.vol * math.exp(-self.div * self.time) * self.n_prime(d1) / (
                    2 * math.sqrt(self.time))
            theta_2 = self.rate * self.strike * math.exp(-self.rate * self.time) * self.n(-d2)
            theta_3 = self.div * self.underlying * math.exp(-self.div * self.time) * self.n(-d1)
            theta = (1 / 365) * (theta_2 - theta_1 - theta_3)
            rho = (-1 / 100) * self.strike * self.time * math.exp(-self.rate * self.time) * self.n(-d2)

        return [delta, gamma, vega, theta, rho]
