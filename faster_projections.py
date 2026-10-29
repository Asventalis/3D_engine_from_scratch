import numpy as np

def normalize(vector):
    """Normalize a vector."""
    vector = np.array(vector, dtype=float)
    norm = np.linalg.norm(vector)
    if norm == 0:
        raise ValueError("Zero vector cannot be normalized.")
    return vector / norm

def is_orthonormal(x, y, z):
    """Check if the vectors form an orthonormal basis."""
    # Check orthogonality
    orthogonal = (
        np.isclose(np.dot(x, y), 0) and
        np.isclose(np.dot(x, z), 0) and
        np.isclose(np.dot(y, z), 0)
    )
    # Check normalization
    normalized = (
        np.isclose(np.linalg.norm(x), 1) and
        np.isclose(np.linalg.norm(y), 1) and
        np.isclose(np.linalg.norm(z), 1)
    )
    return orthogonal and normalized

def rotate_points(points, axis, angle):
    """
    Rotate an array of points around a given axis by a specified angle.

    Parameters:
    - points: np.ndarray of shape (n, 3), the points to rotate.
    - axis: array-like of shape (3,), the axis of rotation.
    - angle: float, the angle of rotation in radians.

    Returns:
    - np.ndarray of shape (n, 3), the rotated points.
    """
    # Normalize the axis of rotation
    axis = normalize(axis)

    # Compute the rotation matrix using Rodrigues' rotation formula
    cos_theta = np.cos(angle)
    sin_theta = np.sin(angle)
    one_minus_cos = 1 - cos_theta

    x, y, z = axis
    rotation_matrix = np.array([
        [cos_theta + x * x * one_minus_cos, x * y * one_minus_cos - z * sin_theta, x * z * one_minus_cos + y * sin_theta],
        [y * x * one_minus_cos + z * sin_theta, cos_theta + y * y * one_minus_cos, y * z * one_minus_cos - x * sin_theta],
        [z * x * one_minus_cos - y * sin_theta, z * y * one_minus_cos + x * sin_theta, cos_theta + z * z * one_minus_cos]
    ])

    # Rotate the points
    return points @ rotation_matrix.T

class ReferenceFrame:
    def __init__(self, x, y, z, position, global_frame=None):
        # Normalize the input vectors
        x = normalize(x)
        y = normalize(y)
        z = normalize(z)
        position = np.array(position, dtype=float)

        # Ensure the vectors form an orthonormal basis
        if not is_orthonormal(x, y, z):
            raise ValueError("The provided vectors must form an orthonormal basis.")

        # Create the 4x4 transformation matrix
        self.matrix = np.eye(4)
        self.matrix[:3, 0] = x
        self.matrix[:3, 1] = y
        self.matrix[:3, 2] = z
        self.matrix[:3, 3] = position

        # Precompute the inverse matrix for efficiency
        self.inverse_matrix = np.linalg.inv(self.matrix)

        self.global_reference_frame = global_frame
        self.local_reference_frames = []
        self.local_objects = []

    def transform_points(self, points):
        """Transform points from the reference frame to the global frame."""
        points_h = np.hstack((points, np.ones((points.shape[0], 1))))  # Convert to homogeneous coordinates
        transformed_h = points_h @ self.matrix.T
        return transformed_h[:, :3]  # Convert back to Cartesian coordinates

    def inverse_transform_points(self, points):
        """Transform points from the global frame to the reference frame."""
        points_h = np.hstack((points, np.ones((points.shape[0], 1))))  # Convert to homogeneous coordinates
        transformed_h = points_h @ self.inverse_matrix.T
        return transformed_h[:, :3]  # Convert back to Cartesian coordinates
    

class Object3D:
    def __init__(self, vertexes, faces, local_frame=ReferenceFrame([1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, 0])):
        self.vertexes = np.array(vertexes, dtype=float)
        self.faces = np.array(faces, dtype=int)
        self.local_frame = local_frame
        self.local_frame.local_objects.append(self)