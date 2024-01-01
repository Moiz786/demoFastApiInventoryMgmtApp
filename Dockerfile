# base image for python 3.8.10 selected
FROM python:3.8.10

# creates SIMS directory in docker
WORKDIR /SIMS

# copies requirements file in docker
COPY requirements.txt .

# install requirements from the file
RUN pip install -r requirements.txt

# copy the project files
COPY . .

# SIMS app inside docker will be on port 8000
EXPOSE 8000
EXPOSE 5432

# command to start project inside docker
CMD ["uvicorn", "sims:sims_app", "--host", "0.0.0.0"]