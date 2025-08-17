import random



def generate_points(file_name, num_points, x_range, y_range):
    """
    Generates a file with random points within the specified range, avoiding obstacles.

    Parameters:
    - file_name (str): The name of the file to write the points to.
    - num_points (int): The number of points to generate.
    - x_range (tuple): A tuple specifying the range for x coordinates (min_x, max_x).
    - y_range (tuple): A tuple specifying the range for y coordinates (min_y, max_y).
    """
    with open(file_name, 'a') as f:  # Append to the existing file
        f.write("SECTION Coordinates\n")
        f.write(f"0 0\n")
        for _ in range(num_points):
            x = random.randint(x_range[0], x_range[1])
            y = random.randint(y_range[0], y_range[1])
            f.write(f"{x} {y}\n")                
        f.write("\n")


for i in range(100):
    random.seed(i)
    filename = 'data/50points_range50_'+ str(i) + '.txt'
    generate_points(filename, 50, (-50, 50), (-50, 50))
