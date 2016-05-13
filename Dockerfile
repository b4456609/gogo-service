# Set the base image to Ubuntu
FROM ubuntu:14.04

# Add the application resources URL
RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list

# Update the sources list
RUN apt-get update

# Install basic applications
RUN apt-get install -y tar git curl wget build-essential gcc

# Install Python and Basic Python Tools
RUN apt-get install -y python python-dev python-distribute python-pip

# libev support
RUN apt-get install -y libev4 libev-dev

# Set the default directory where CMD will execute
WORKDIR /opt/app

# Copy the application folder inside the container
ADD api.py /opt/app
ADD model.py /opt/app
ADD requirements.txt /opt/app

# Get pip to download and install requirements:
RUN pip install -r requirements.txt

# Expose ports
EXPOSE 5000

# Set the default command to execute
# when creating a new container
# i.e. using CherryPy to serve the application
ENTRYPOINT ["python"]
CMD ["api.py"]