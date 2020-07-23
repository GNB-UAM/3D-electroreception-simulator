FROM ubuntu:14.04

WORKDIR /home

RUN apt-get update && apt-get install -y git cmake build-essential gfortran libopenmpi-dev libblas-dev liblapack-dev alien checkinstall build-essential automake autoconf libtool pkg-config

RUN git clone https://github.com/ElmerCSC/elmerfem.git

WORKDIR elmerfem/build

RUN cmake .. -DWITH_OpenMP:BOOLEAN=FALSE -DWITH_MPI:BOOLEAN=FALSE

RUN make -j8

ENV DEBIAN_FRONTEND=noninteractive

RUN checkinstall
