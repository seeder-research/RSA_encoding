import numpy as np
import re

for i in range(100):
    datafile = 'data/50points_range50_'+ str(i) +'.txt'
    with open(datafile, 'r') as f:
        lines = f.readlines()

    reading_coordinates = False
    points = []

    for line in lines:
        line = line.strip()
        if line == "SECTION Coordinates":
            reading_coordinates = True
            continue

        if reading_coordinates:
            parts = line.split()
            if len(parts) == 2 and all(part.lstrip('-').isdigit() for part in parts):
                points.append(tuple(map(int, parts)))
            else:
                break

    # Parse the coordinates
    destination = points[0]
    sources = points[1:]

    def generate_hanan_grid(points):
        x_coords = sorted(set(point[0] for point in points))
        y_coords = sorted(set(point[1] for point in points))

        hanan_points = [(x, y) for x in x_coords for y in y_coords]

        edge_list = []
        edge_dict = {}
        edge_count = 1

        # Row edges (x direction)
        for i in range(len(x_coords) - 1):
            for y in y_coords:
                x1, x2 = x_coords[i], x_coords[i + 1]
                length = abs(x2 - x1)
                edge_name = f"x{edge_count}"
                direction = "left" if x1 >=0 and x2 >= 0 else "right"
                if x1>=0 and x2>=0:
                    edge_list.append(((x2, y), (x1, y), edge_name, direction, length))
                else:
                    edge_list.append(((x1, y), (x2, y), edge_name, direction, length))
                edge_dict[edge_name] = (direction, length)
                edge_count += 1

        # Column edges (y direction)
        for i in range(len(y_coords) - 1):
            for x in x_coords:
                y1, y2 = y_coords[i], y_coords[i + 1]
                length = abs(y2 - y1)
                edge_name = f"x{edge_count}"
                direction = "down" if y1 >=0 and y2 >= 0 else "up"
                if y1>=0 and y2>=0:
                    edge_list.append(((x, y2), (x, y1), edge_name, direction, length))
                else:
                    edge_list.append(((x, y1), (x, y2), edge_name, direction, length))
                edge_dict[edge_name] = (direction, length)
                edge_count += 1

        return edge_list, edge_dict, hanan_points


    # Generate edge list
    edge_list, edge_dict, hanan_points = generate_hanan_grid(points)

    def generate_pb_constraints(destination, sources, edge_list, hanan_points):
        pb_constraints = []


        for source in sources:
            x,y = source
            # Constraint 1: For each source on the axis, the output edge must be selected as 1
            if x == 0 or y == 0:
                for (start, _, edge_name, _, _) in edge_list:
                    if source == start:
                        pb_constraints.append(f"+1 {edge_name} = 1")

            # Constraint 2: For each source not on the axis, one of the output edge must be selected as 1
            else:
                edge_names = []
                for (start, _, edge_name, _, _) in edge_list:
                    if source == start:
                        edge_names.append(edge_name)
                pb_constraints.append(f"+1 {' +1 '.join(edge_names)} = 1")
        
        # Identify non-source points
        non_source_points = set(hanan_points) - set(sources) - {destination}

        for point in non_source_points:
            x,y = point
            if x==0 or y==0:
                start_edge_names = []
                end_edge_names = []
                for (start, end, edge_name, _, _) in edge_list:
                    if point == end:
                        end_edge_names.append(edge_name)
                    
                    if point == start:
                        start_edge_names.append(edge_name)
                
                    
                if end_edge_names != [] and start_edge_names != []:  
                    # pb_constraints.append(f"+1 {' +1 '.join(end_edge_names)} -2 {' -2 '.join(start_edge_names)} <= 0")
                    # pb_constraints.append(f"+1 {' +1 '.join(start_edge_names)} -2 {' -2 '.join(end_edge_names)} <= 0")

                    # need to reverse to >=
                    pb_constraints.append(f"-1 {' -1 '.join(end_edge_names)} +3 {' +3 '.join(start_edge_names)} >= 0")
                    pb_constraints.append(f"-1 {' -1 '.join(start_edge_names)} +1 {' +1 '.join(end_edge_names)} >= 0")

                # Additional constraint: Both start edges cannot be 1 at the same time if there are more than one
                if len(start_edge_names) > 1:
                    pb_constraints.append(f"-1 {' -1 '.join(start_edge_names)} >= -1")   

            else:
                # Constraint 3: For each non-source point, if one of the input edge is selected as 1, then one of the output edge must be selected as 1
                start_edge_names = []
                end_edge_names = []
                for (start, end, edge_name, _, _) in edge_list:
                    if point == end:
                        end_edge_names.append(edge_name)
                    
                    if point == start:
                        start_edge_names.append(edge_name)
                
                    
                if end_edge_names != [] and start_edge_names != []:  
                    # pb_constraints.append(f"+1 {' +1 '.join(end_edge_names)} -2 {' -2 '.join(start_edge_names)} <= 0")
                    # pb_constraints.append(f"+1 {' +1 '.join(start_edge_names)} -2 {' -2 '.join(end_edge_names)} <= 0")

                    # need to reverse to >=
                    pb_constraints.append(f"-1 {' -1 '.join(end_edge_names)} +2 {' +2 '.join(start_edge_names)} >= 0")
                    pb_constraints.append(f"-1 {' -1 '.join(start_edge_names)} +1 {' +1 '.join(end_edge_names)} >= 0")

                # Additional constraint: Both start edges cannot be 1 at the same time if there are more than one
                if len(start_edge_names) > 1:
                    pb_constraints.append(f"-1 {' -1 '.join(start_edge_names)} >= -1")    


        return pb_constraints


    pb_constraints = generate_pb_constraints(destination, sources, edge_list,  hanan_points)

    def generate_objective_function(edge_list):
        objective_terms = [f"+{length} {edge_name}" for _, _, edge_name, _, length in edge_list]
        objective_function = " ".join(objective_terms)
        return objective_function

    objective_function = generate_objective_function(edge_list)

    def save_pb_to_file(pb_constraints, objective_function, filename):
        variables = re.findall(r'x\d+', objective_function)

        # Get the count of unique variables
        num_variables = len(set(variables))
        num_constraints = len(pb_constraints)
        
        with open(filename, "w") as f:
            # Write the header with the number of variables and constraints
            f.write(f"* #variable= {num_variables} #constraint= {num_constraints}\n")
            
            # Write the objective function
            f.write("min: ")
            f.write(objective_function)
            f.write(" ;\n")
            
            # Write the constraints
            for constraint in pb_constraints:
                f.write(constraint)
                f.write(" ;\n")

    # Save to file
    output_file_path = 'no_reduction_PB/pb_constraints_' + str(i) + '.txt'
    save_pb_to_file(pb_constraints, objective_function, output_file_path)
