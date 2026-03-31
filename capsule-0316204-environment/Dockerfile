# hash:sha256:90cb78911ea17adccf05c60f70763983a3b5112d6bf7c0d37f06fc551724a64a
FROM registry.codeocean.com/codeocean/miniconda3:4.9.2-cuda11.7.0-cudnn8-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        cmake=3.16.3-1ubuntu1.20.04.1 \
        cuda-toolkit-11-0=11.0.3-1 \
        g++-9=9.4.0-1ubuntu1~20.04.1 \
        gcc-9-base=9.4.0-1ubuntu1~20.04.1 \
        graphviz=2.42.2-3build2 \
        make=4.2.1-1.2 \
    && rm -rf /var/lib/apt/lists/*

RUN conda install -y \
        numpy==1.21.5 \
        python==3.7.0 \
        scikit-learn==1.0.2 \
    && conda clean -ya

COPY postInstall /
RUN /postInstall
