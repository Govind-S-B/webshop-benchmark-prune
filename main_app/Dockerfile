# main_app/Dockerfile

# Use miniconda base image
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /app

# Copy the app content into the image
COPY . .

# Create and activate the conda environment, and run the setup script
RUN conda create -n webshop python=3.8.13 && \
    /bin/bash -c "source activate webshop && chmod +x setup.sh && ./setup.sh"
# Open port 3000 for the flask app
EXPOSE 3000

# Set the default command to run the app
CMD ["/bin/bash", "-c", "source activate webshop && chmod +x entrypoint.sh && ./entrypoint.sh"]
