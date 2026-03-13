import numpy as np
from typing import Tuple

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


if __name__ == "__main__":
    # Set random seed for reproducibility
    np.random.seed(42)

    # Quick Example
    print("\n1. Quick Example: (100,000 points):")
    pi_estimate, _, _, _ = monte_carlo_pi(100000)
    print(f"Estimated π: {pi_estimate:.6f}")
    print(f"True π value: {np.pi:.6f}")
    print(f"Error: {abs(pi_estimate - np.pi):.6f}")