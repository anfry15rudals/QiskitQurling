from scipy.optimize import curve_fit
import matplotlib.pyplot as plt 
import pickle as pkl

def linear(x, y_intercept, slope):
    return y_intercept + (x * slope)

def third_poly(x, a, b, c, d):
    return a + b * x + c * x**2 + d * x**3

x = np.arange(data_len)
popt, pcov = curve_fit(linear, x, monitor_reward_history)
plt.plot(linear(x, popt[0], popt[1]))
plt.plot(monitor_reward_history)

x = np.arange(data_len)
popt, pcov = curve_fit(third_poly, x, monitor_reward_history)
plt.plot(third_poly(x, *popt), 'b-', linewidth=3)
plt.plot(monitor_reward_history, 'go', alpha=0.5)
plt.axhline(50, c='r', label='random_agent')
plt.legend()

with open("goodresult.pkl", "wb") as f:
    pkl.dump(monitor_reward_history, f)