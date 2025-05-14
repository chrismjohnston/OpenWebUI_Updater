import subprocess
import platform

# Configuration
IMAGE_NAME = "ghcr.io/open-webui/open-webui" # Base image name
IMAGE_TAG = "ollama"  # Specific tag for the Ollama bundled version
CONTAINER_NAME = "open-webui"
HOST_PORT = 3000
CONTAINER_PORT = 8080
# Docker volume for Open WebUI's own data (chats, settings)
OPEN_WEBUI_DATA_VOLUME = "open-webui-data"
# Docker volume for Ollama's data (models) if using the bundled ollama image
OLLAMA_DATA_VOLUME = "ollama-data"


def run_command(command, shell=False):
    """
    Executes a shell command and prints its output.
    Returns True if the command was successful, False otherwise.
    """
    # Ensure all parts of the command are strings
    command = [str(c) for c in command]
    print(f"\nExecuting: {' '.join(command)}")
    try:
        process = subprocess.run(command, shell=shell, check=True, capture_output=True, text=True)
        if process.stdout:
            print("Output:\n", process.stdout)
        if process.stderr:
            # Docker sometimes prints non-error info to stderr (like pull progress)
            print("Standard Error Output (if any):\n", process.stderr)
        print(f"Command '{' '.join(command)}' executed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(command)}")
        print("Return code:", e.returncode)
        if e.stdout:
            print("Stdout:", e.stdout)
        if e.stderr:
            print("Stderr:", e.stderr)
        return False
    except FileNotFoundError:
        print(f"Error: The command 'docker' was not found. Please ensure Docker is installed and in your system's PATH.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

def main():
    """
    Main function to stop, remove, pull, and run the Open WebUI Docker container.
    """
    # Construct the full image name with the tag
    full_image_name = f"{IMAGE_NAME}:{IMAGE_TAG}"

    print(f"--- Starting Open WebUI Docker Setup ---")
    print(f"Image: {full_image_name}")
    print(f"Container Name: {CONTAINER_NAME}")
    print(f"Host Port: {HOST_PORT}, Container Port: {CONTAINER_PORT}")
    print(f"Open WebUI Data Volume: {OPEN_WEBUI_DATA_VOLUME}")
    if "ollama" in IMAGE_TAG.lower(): # Check if it's an ollama bundled image
        print(f"Ollama Data Volume (for bundled Ollama): {OLLAMA_DATA_VOLUME}")


    # Step 1: Stop any existing container with the same name
    print(f"\n--- Step 1: Stopping existing container '{CONTAINER_NAME}' (if any) ---")
    stop_command = ["docker", "stop", CONTAINER_NAME]
    run_command(stop_command) # We don't need to halt if it fails (container might not exist)

    # Step 2: Remove any existing container with the same name
    print(f"\n--- Step 2: Removing existing container '{CONTAINER_NAME}' (if any) ---")
    remove_command = ["docker", "rm", CONTAINER_NAME]
    run_command(remove_command) # We don't need to halt if it fails

    # Step 3: Pull the latest image
    print(f"\n--- Step 3: Pulling image '{full_image_name}' ---")
    pull_command = ["docker", "pull", full_image_name]
    if not run_command(pull_command):
        print(f"\nFailed to pull the Docker image '{full_image_name}'. Please check the image name/tag, your internet connection, and Docker setup.")
        return

    # Step 4: Run the new container
    print(f"\n--- Step 4: Running new container '{CONTAINER_NAME}' ---")
    
    docker_run_command = [
        "docker", "run",
        "-d",  # Run in detached mode
        "-p", f"{HOST_PORT}:{CONTAINER_PORT}",  # Port mapping for Open WebUI
        # Volume for Open WebUI's persistent data (chats, user settings etc.)
        "-v", f"{OPEN_WEBUI_DATA_VOLUME}:/app/backend/data",
        "--name", CONTAINER_NAME,
        "--restart", "always"
    ]

    # Add GPU support and Ollama specific configurations if using an Ollama image
    if "ollama" in IMAGE_TAG.lower():
        # For Ollama bundled image, it often exposes Ollama on 11434 internally
        # and requires a volume for Ollama models.
        docker_run_command.extend([
            "-v", f"{OLLAMA_DATA_VOLUME}:/root/.ollama", # Persistent storage for Ollama models
            # The following port mapping is if you want to access Ollama API directly from host.
            # OpenWebUI container will access Ollama internally.
            # "-p", "11434:11434", 
        ])
        # Add GPU flag if you intend to use GPU with the bundled Ollama
        # Ensure your system and Docker are configured for NVIDIA GPU passthrough
        docker_run_command.extend(["--gpus", "all"]) # Corrected: --gpus and all are separate
    else:
        # For standalone Open WebUI, it needs to connect to an Ollama instance.
        # --add-host is useful if Ollama is running on the host machine outside Docker.
        docker_run_command.append("--add-host=host.docker.internal:host-gateway")


    docker_run_command.append(full_image_name) # The image to run

    if not run_command(docker_run_command):
        print(f"\nFailed to start the Open WebUI container. Please check Docker logs for '{CONTAINER_NAME}' for more details.")
        print(f"You can try: docker logs {CONTAINER_NAME}")
        return

    print(f"\n--- Open WebUI Setup Complete ---")
    print(f"Open WebUI ({IMAGE_TAG} version) should now be running.")
    print(f"Access it at: http://localhost:{HOST_PORT}")
    print(f"Open WebUI data is stored in Docker volume: '{OPEN_WEBUI_DATA_VOLUME}'")
    if "ollama" in IMAGE_TAG.lower():
         print(f"Ollama models (if using bundled version) are stored in Docker volume: '{OLLAMA_DATA_VOLUME}'")

if __name__ == "__main__":
    # Basic check if Docker command is available
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Docker command not found or Docker daemon is not responding.")
        print("Please ensure Docker is installed, running, and accessible in your system's PATH.")
        exit(1)
    
    main()
