import time

# Get the current time
current_time = time.time()

# Subtract 30 minutes (1800 seconds) from the current time
half_hour_ago = current_time - 1800

# Print the Unix timestamp of half an hour ago
print(int(half_hour_ago))
