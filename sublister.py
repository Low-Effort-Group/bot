import sublist3r

sublist3r.main(
    "rvid.eu",  # Target domain
    threads=40,  # Number of threads
    savefile="save.txt",  # File to save the output
    ports=None,  # Ports to scan (optional)
    silent=False,  # Suppress console output
    verbose=True,  # Enable verbose output
    enable_bruteforce=False,  # Enable brute-force
    engines=None,  # List of engines to use (optional)
)
