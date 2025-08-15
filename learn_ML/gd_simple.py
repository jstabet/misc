import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# data
n = 100
x = np.linspace(0, 10, n)
noise = np.random.normal(0, 1.0, size=n)
y = 3.5 + 2.0 * x + noise

# gradient descent
learning_rate = 0.01
m, b = 0, 0
n = len(x)
for i in range(1000):

    if i % 10 == 0:
        plt.scatter(x, y)
        plt.plot(x, m*x + b, color='green')
        plt.xlim(x[0], x[-1])
        plt.ylim(y[0], y[-1])
        plt.title(f'Iteration {i}\nm: {m:.2f}, b: {b:.2f}')
        plt.pause(0.05)
        plt.clf()

    y_pred = m*x + b

    Dm = (-2/n) * (x * (y-y_pred)).sum()
    Db = (-2/n) * (y-y_pred).sum()

    m -= learning_rate * Dm
    b -= learning_rate * Db

plt.show()

print('GD:', m, b)

# compare with OLS (beta = (X^T X)^{-1} X^T y)
X = np.column_stack([np.ones_like(x), x])
XtX = X.T @ X
XtX_inv = np.linalg.inv(XtX)
XtY = X.T @ y
beta_ols = XtX_inv @ XtY
b_OLS, m_OLS = beta_ols
print('OLS:', m_OLS, b_OLS)

# compare with sklearn
model = LinearRegression()
model.fit(x.reshape(-1, 1), y)
m_sklearn, b_sklearn = model.coef_[0], model.intercept_
print('sklearn:', m_sklearn, b_sklearn)