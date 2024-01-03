# Base python package
FROM python:3.8-slim-buster

# Working directory
WORKDIR /app

# Copy the dependencies
ADD requirements.txt .

# Install the dependencies
#RUN pip3 install -r requirements.txt
RUN pip3 install -r requirements.txt

# Copy the files
ADD . /app

# Executable commands
#CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
CMD python app.py