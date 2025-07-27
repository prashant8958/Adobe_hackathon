# Adobe Hackathon Solution

This repository contains the solution for the Adobe Hackathon challenge.

## Docker Instructions

### Build the image

```bash
docker build -t gauravni/my-python-app .
```

### Run the container

```bash
docker run --rm -v "$PWD":/app gauravni/my-python-app
```

