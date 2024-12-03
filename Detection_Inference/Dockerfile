# Use the existing CUDA image as the base image
FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04

# Install Python and other dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip \
                       libglib2.0-0 cmake gcc g++ \
                       libavcodec-dev libavformat-dev libswscale-dev \
                       libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev \
                       libgtk-3-dev git && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Set python3 as the default python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set the working directory in the container
WORKDIR /app

# Clone OpenCV repositories
RUN git clone https://github.com/opencv/opencv.git
RUN git clone https://github.com/opencv/opencv_contrib.git

# Create build directory and run CMake
WORKDIR /app/opencv
RUN mkdir -p build && cd build && \
    cmake -D CMAKE_BUILD_TYPE=Release \
          -D CMAKE_INSTALL_PREFIX=$(python3 -c "import sys; print(sys.prefix)") \
          -D OPENCV_EXTRA_MODULES_PATH=/app/opencv_contrib/modules \
          -D PYTHON3_EXECUTABLE=$(which python3) \
          -D PYTHON3_INCLUDE_DIR=$(python3 -c "import sysconfig; print(sysconfig.get_path('include'))") \
          -D PYTHON3_LIBRARY=$(python3 -c "import sysconfig; print(sysconfig.get_config_var('LIBDIR'))") \
          -D WITH_GSTREAMER=ON ..

# Build and install OpenCV
RUN cd build && make -j$(nproc) && make install

# Copy the current directory contents into the container at /usr/src/app
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache

# Install system dependencies
RUN apt update && apt install -y libgl1-mesa-glx

# Upgrade pip again (to ensure it's the latest version)
RUN pip3 install --upgrade pip


# Install any needed packages specified in requirements.txt
# RUN --mount=type=cache,target=/root/.cache pip install -r ./requirements.txt
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Update package lists and install vim in a non-interactive way
RUN apt-get update && apt-get install -y vim

# MQTT settings
RUN apt-get update
RUN apt-get install -y mosquitto mosquitto-clients 

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED=1

COPY . /app

RUN chmod +x infer.sh
RUN chmod +x script.sh


# RUN chmod 777 /app/infer.sh
# RUN ls -al /app
# ENTRYPOINT ["./infer.sh"]
ENTRYPOINT [ "/app/script.sh" ]
# CMD ["bash","/app/infer.sh"]

# CMD ["mosquitto","-d"]

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# 기본 명령어 설정
# CMD ["bash", "-c", "cd /app && source infer.sh"]


