import numpy as np 
import numpy.typing as npt

class Similarity:
    def dot_product(self, vec1: npt.NDArray, vec2: npt.NDArray) -> np.float64:
        if vec1 is None or vec2 is None or vec1.size == 0 or vec2.size == 0:
            raise ValueError("Input vectors cannot be None or empty")
        shape1 = vec1.shape
        shape2 = vec2.shape
        if shape1 != shape2:
            raise ValueError("Vectors must be of the same shape")
        result = np.float64(0)
        flat1 = vec1.flatten()
        flat2 = vec2.flatten()
        for i in range(flat1.size):
            result += flat1[i] * flat2[i]
        return result
    
    def norm(self, vec: npt.NDArray) -> np.float64:
        if vec is None or vec.size == 0:
            raise ValueError("Input vectors cannot be None or empty")
        sum = np.float64(0)
        flat = vec.flatten()
        for i in range(flat.size):
            sum += flat[i]**2
        return np.sqrt(sum)
    
    def vector_normalization(self, vec: npt.NDArray) -> npt.NDArray:
        if vec is None or vec.size == 0:
            raise ValueError("Input vectors cannot be None or empty")
        norm = self.norm(vec)
        if norm == 0:
            raise ValueError("Cannot normalize a zero vector")
        return vec / norm
    
    def cosine_similarity(self, vec1: npt.NDArray, vec2: npt.NDArray) -> np.float64:
        if vec1 is None or vec2 is None or vec1.size == 0 or vec2.size == 0:
            raise ValueError("Input vectors cannot be None or empty")
        shape1 = vec1.shape
        shape2 = vec2.shape
        if shape1 != shape2:
            raise ValueError("Vectors must be of the same shape")
        norm_vec1 = self.norm(vec1)
        norm_vec2 = self.norm(vec2)
        return self.dot_product(vec1, vec2) / (norm_vec1 * norm_vec2)

    


if __name__ == "__main__":
    sim = Similarity()
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])
    result = sim.dot_product(a, b)
    print(f"Dot product of {a} and {b} is: {result}")

    a = np.array([1, 1])
    b = np.array([2, 2])

    result = sim.cosine_similarity(a, b)
    print(f"cosine similarity of {a} and {b} is: {result}")  # Output: 4.0

    a = np.array([1, 1])
    b = np.array([10, 10])

    print("Cosine:", sim.cosine_similarity(a, b))
    print("L2:", sim.norm(a - b))