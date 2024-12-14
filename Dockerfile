FROM certbot/certbot

# Install python-dotenv without cache
RUN pip install --no-cache-dir python-dotenv tencentcloud-sdk-python-dnspod

# Set the working directory to /codes
WORKDIR /codes

# Copy the current directory's files to /codes in the container
COPY . /codes

# Set the default command to run the Python script aaa.py
CMD ["python3", "/codes/cert.py"]
