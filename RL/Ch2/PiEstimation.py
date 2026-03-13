import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List

def monte_carlo_pi(num_points: int) -> Tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    '''
    Estimate π using Monte Carlo method

    Args:
        num_points: Number of random points to generate

    Returns:
        Tuple of (pi_estimate, x_coords, y_coords, distances)
    '''

    # Randomly generate points (x, y) at the range of [-1, 1] x [-1, 1]
    x = np.random.uniform(-1, 1, num_points)
    y = np.random.uniform(-1, 1, num_points)

    # Calculate the distance from the origin to each point
    distances = np.sqrt(x**2 + y**2)

    # Count the number of points inside the unit circle (distance <= 1)
    points_inside_circle = np.sum(distances <= 1)

    # Estimate π: π ≈ 4 * (points inside circle / total points)
    pi_estimate = 4 * points_inside_circle / num_points

    return pi_estimate, x, y, distances


def plot_sampling_and_convergence(num_scatter: int, num_convergence: int):
    """
    Plot scatter sampling and pi estimation convergence side by side.

    Args:
        num_scatter: Number of points for the scatter plot
        num_convergence: Maximum sample size for convergence plot
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 1. Scatter plot - points inside/outside unit circle
    pi_est, x, y, distances = monte_carlo_pi(num_scatter)
    inside = distances <= 1

    ax = axes[0]
    ax.scatter(x[inside], y[inside], s=0.5, color='red', label='Inside circle')
    ax.scatter(x[~inside], y[~inside], s=0.5, color='blue', label='Outside circle')
    theta = np.linspace(0, 2 * np.pi, 200)
    ax.plot(np.cos(theta), np.sin(theta), 'k-', linewidth=1)
    ax.set_aspect('equal')
    ax.set_title(f'Monte Carlo Sampling (n={num_scatter})\n'
                 f'Estimated π = {pi_est:.4f}')
    ax.legend(loc='lower left', markerscale=5)

    # 2. Convergence plot - pi estimate vs sample size
    ax = axes[1]
    sample_sizes = np.unique(np.logspace(
        1, np.log10(num_convergence), 200).astype(int))
    estimates: List[float] = []
    for n in sample_sizes:
        est, _, _, _ = monte_carlo_pi(n)
        estimates.append(est)

    ax.plot(sample_sizes, estimates, 'b-', linewidth=0.8)
    ax.axhline(y=np.pi, color='red', linestyle='--', label='True π value')
    ax.set_xscale('log')
    ax.set_xlabel('Number of samples')
    ax.set_ylabel('π estimate')
    ax.set_title('π Estimation Convergence')
    ax.legend()

    plt.tight_layout()
    plt.savefig('RL/Ch2/results/pi_estimation.png', dpi=150)
    plt.show()


if __name__ == "__main__":
    # Set random seed for reproducibility
    np.random.seed(42)

    # Quick Example
    print("\n1. Quick Example: (100,000 points):")
    pi_estimate, _, _, _ = monte_carlo_pi(100000)
    print(f"Estimated π: {pi_estimate:.6f}")
    print(f"True π value: {np.pi:.6f}")
    print(f"Error: {abs(pi_estimate - np.pi):.6f}")

    # Visualization
    plot_sampling_and_convergence(num_scatter=10000,
                                 num_convergence=10000)