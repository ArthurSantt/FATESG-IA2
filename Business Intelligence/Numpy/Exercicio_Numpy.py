import numpy as np

arr1 = np.arange(10)
arr1[5:9] = 0
print("Exercício 1:", arr1)

arr2 = np.array([[1, 2], [3, 4], [5, 6]])
print("\nExercício 2:")
print("Shape:", arr2.shape)
print("2ª linha:", arr2[1])

arr3 = np.array([[10, 20], [30, 40], [50, 60]])
print("\nExercício 3:")
print("2ª coluna:", arr3[:, 1])

arr4 = np.arange(20).reshape(4, 5)
print("\nExercício 4:")
print("Matriz:\n", arr4)
print("3ª linha:", arr4[2])

arr5 = np.arange(1, 21).reshape(4, 5)
print("\nExercício 5:")
print(arr5[0:2, 1:3]) 

arr6 = np.arange(100, 120).reshape(4, 5)
print("\nExercício 6:")
print(arr6[1:3, 0:3])