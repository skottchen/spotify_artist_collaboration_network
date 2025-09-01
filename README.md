# Table of Contents

- [Spotify Artist Collaboration Network](#spotify-artist-collaboration-network)
- [File Overview](#file-overview)
- [Design Decisions](#design-decisions)
- [Final Outputs](#final-outputs)
- [How to Run](#how-to-run)
- [Running This Program with Docker](#running-this-program-with-docker)
- [Video Demo](#video-demo)

# Spotify Artist Collaboration Network

This project visualizes and analyzes musical artist collaborations using data from the Spotify Web API. Given a user-defined playlist, the program extracts the top artists, gathers metadata about their albums and featured tracks, and constructs a network graph where each node represents an artist and each edge represents a collaboration. It outputs a visual graph of the collaboration network and a CSV file displaying each artist’s
[degree centrality](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.degree_centrality.html) and total number of collaborations with other artists in the playlist. 

The goal of this project is to explore patterns in collaboration behavior between mainstream artists, identify central figures in the network, and practice skills in API usage, data cleaning, network analysis, and visualization. This project was also a way to gain hands-on experience integrating multiple Python modules and structuring a scalable data analysis pipeline.

## File Overview

### `auth.py`

Handles authentication with the Spotify API using the Client Credentials Flow.

- Loads client credentials (`CLIENT_ID` and `CLIENT_SECRET`) from a `.env` file.
- `get_token()` encodes credentials and requests an access token.
- `get_auth_header(token)` generates the proper authorization headers needed for authenticated API calls.

### `fetch_api_data.py`

This script executes the initial data retrieval process:

- Authenticates with the Spotify API.
- Extracts top artists from a given playlist using `get_top_artists`.
- Fetches all albums by each artist (`get_artist_albums`), and filters out redundant/duplicate albums using `clean_album_names`.
- Retrieves all collaborations (i.e., artists featured on each track) via `get_artist_collaborations`.
- Outputs raw data into `Spotify_API_data/raw_artists_colab_data.json`.

### `clean_json_files.py`

This module processes and filters the raw JSON data for meaningful content:

- Removes the first listed collaboration for Beyoncé, which often contained a self-reference or duplicate.
- Filters out artists who had no recorded collaborations (to reduce graph clutter).
- Saves cleaned data to `Spotify_API_data/cleaned_artists_colab_data.json`.

### `perform_network_analysis.py`

This is the central analysis and visualization script. It:

- Loads the cleaned collaboration data.
- Builds a graph using NetworkX, where artists are nodes and collaborations are edges.
- Assigns a unique color and size to each node based on their collaboration count.
- Generates a PNG image of the graph (`Outputs/artists_collaboration_graph.png`).
- Calculates degree centrality for each artist and writes a CSV file with metrics (`Outputs/network_analysis_results.csv`).

## Design Decisions

Several design choices were debated during this project. One was how to handle duplicate albums—Spotify often lists the same album with various editions (e.g., deluxe, remastered). Instead of keeping all versions, I implemented a `clean_album_names` function that retains only the latest version based on release date, simplifying the data without losing relevance.

Another key choice was to use JSON as an intermediate data format between stages. This modular approach separated raw collection, cleaning, and analysis into independent steps, making the project more maintainable and debuggable.

Finally, the use of `randomcolor` for graph node colors was chosen to make the visual output aesthetically distinct and avoid confusion between similarly named artists.

## Final Outputs

- `Spotify_API_data/top_artists.json`: Top artists extracted from playlist.
- `Spotify_API_data/raw_artists_colab_data.json`: Raw collaboration data.
- `Spotify_API_data/cleaned_artists_colab_data.json`: Cleaned version of above.
- `Outputs/artists_collaboration_graph.png`: Network visualization of collaborations.
- `Outputs/network_analysis_results.csv`: Degree centrality and collaboration counts.

## How to Run

Ensure you have a `.env` file with your Spotify API credentials and a playlist ID (you can obtain credentials by creating a [Spotify Developer account](https://developer.spotify.com/documentation/web-api)):

```
SPOTIFY_CLIENT_ID=your_id
SPOTIFY_CLIENT_SECRET=your_secret
PLAYLIST_ID=your_playlist_id
```


Then simply run:

```
python project.py
```

## Running This Program with Docker

> **Note:**
> You do not strictly need Docker Desktop to run Docker, but you do need Docker Engine installed on your system.
> - On Windows and macOS, Docker Desktop is the easiest way to install and manage Docker.
> - On Linux, you can install Docker Engine directly without Docker Desktop.
> Some form of Docker Engine is required to build and run Docker containers.

### Build the Docker Image

From your project root, build the Docker image with:

```powershell
docker build -t <your_image_name> .
```

### Run the Program with Docker (with Output Persistence)

To run the program in a Docker container and save the output files (such as the graph image, CSV, and API data) to your local machine, use the following command from your project root (replace the placeholders with your actual values):

```powershell
docker run `
	--env CLIENT_ID="<your_client_id>" `
	--env CLIENT_SECRET="<your_client_secret>" `
	--env PLAYLIST_ID="<your_playlist_id>" `
	-v ${PWD}\Outputs:/spotify_proj/Outputs `
	-v ${PWD}\Spotify_API_data:/spotify_proj/Spotify_API_data `
	<your_image_name>
```

This will map the container's `Outputs` and `Spotify_API_data` directories to the corresponding folders in the project directory, so all generated files will be available on your machine after the container finishes running.

## Video Demo
For the demo, I will be using Spotify's [Top Artists of 2024 Global](https://open.spotify.com/playlist/37i9dQZF1DX9lzz0FRAxgl) playlist.  
[![Watch the Demo](https://img.shields.io/badge/Watch%20the%20Demo-red?logo=youtube)](https://www.youtube.com/watch?v=IHHLYT7mpLY)

