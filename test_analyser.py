#!/usr/bin/python3.6

import re

def process_test(test_lines, threads, schedule):
    # Extract information from the lines of a test
    test_info = {"Threads": threads, "Schedule": schedule}
    for line in test_lines:
        # Defines running a new file
        if line.startswith("Running Test:"):
            test_info["Test Name"] = line.split(":")[1].strip()

        elif line.startswith("user"):
            user = re.search(r'user (\d+\.\d+)', line).groups()[0]
            test_info["Timing-User"] = float(user)
            # event, duration = re.search(r'Event (\d+): (.+), Duration: (\d+)', line).groups()
            # test_info.setdefault("Events", []).append({"Event": event, "Description": duration})

        elif line.startswith("sys"):
            user = re.search(r'sys (\d+\.\d+)', line).groups()[0]
            test_info["Timing-System"] = float(user)

        elif line.startswith("real"):
            user = re.search(r'real (\d+\.\d+)', line).groups()[0]
            test_info["Timing-Elapsed"] = user

        elif line.startswith("diffuse"):
            timing = re.search(r'diffuse\t(\d+)', line).groups()[0]
            test_info["diffuse"] = test_info.get("diffuse", 0) + int(timing)
            test_info["diffuse_count"] = test_info.get("diffuse_count", 0) + 1

        elif line.startswith("reset"):
            timing = re.search(r'reset\t(\d+)', line).groups()[0]
            test_info["reset"] = test_info.get("reset", 0) + int(timing)
            test_info["reset_count"] = test_info.get("reset_count", 0) + 1

        elif line.startswith("upbounds"):
            timing = re.search(r'upbounds\t(\d+)', line).groups()[0]
            test_info["upbounds"] = test_info.get("upbounds", 0) + int(timing)
            test_info["upbounds_count"] = test_info.get("upbounds_count", 0) + 1
        
    return test_info

def read_file(file_path):
    threads = 0
    schedule = ""
    with open(file_path, 'r') as file:
        current_test_lines = []
        for line in file:
            # meta  config  parallel  threads 1
# meta  config  parallel  schedule guided
            if line.startswith("meta  config  parallel  threads"):
                if len(current_test_lines) > 1:
                    yield process_test(current_test_lines, threads, schedule)
                    current_test_lines = []

                threads = re.search(r"meta  config  parallel  threads (\d+)", line).groups()[0]
            elif line.startswith("meta  config  parallel  schedule"):
                schedule = re.search(r"meta  config  parallel  schedule ([A-Za-z0-9]+)", line).groups()[0]
            elif line.strip().startswith("Running Test:"):
                # Process the previous test if any
                if len(current_test_lines) > 1:
                    yield process_test(current_test_lines, threads, schedule)
                    current_test_lines = []
                # Start collecting lines for the new test
                current_test_lines.append(line.strip())
            else:
                current_test_lines.append(line.strip())

        # Process the last test in the file
        if current_test_lines:
            yield process_test(current_test_lines, threads, schedule)

if __name__ == "__main__":
    file_path = "kudu/err.deqn_762464.err"  # Replace with the actual file path
    tests = []
    for test_number, test_data in enumerate(read_file(file_path), start=1):
        print(f"Test {test_number}:")
        print(test_data)
        tests.append(test_data)
        print("\n")

    stats = {}
    for test in tests:
        avg_diffuse = test["diffuse"] / test["diffuse_count"]
        avg_reset = test["reset"] / test["reset_count"]
        avg_upbounds = test["upbounds"] / test["upbounds_count"]

        print(test["Threads"], "\t", test["Test Name"], "\t", avg_diffuse, " ", avg_reset, " ", avg_upbounds, "\t", test["Timing-Elapsed"])