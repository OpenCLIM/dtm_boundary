FROM python:3.8
RUN apt-get -y update
RUN apt-get -y install libgdal-dev gdal-bin
RUN pip install rasterio geopandas

RUN mkdir src

WORKDIR src

COPY run.py .

#COPY data /data

CMD [ "python", "run.py"]

