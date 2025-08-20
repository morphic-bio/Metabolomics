# Base image: Ubuntu with Python3 and required tools
FROM ubuntu:22.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system packages: Python 3.11, pip, git, wget, unzip, build tools, and Mono for RawFile conversion
RUN apt-get update && apt-get install -y \
    python3.11 python3.11-dev python3.11-distutils \
    git nano wget unzip build-essential mono-devel \
 && rm -rf /var/lib/apt/lists/*

# Install pip for Python 3.11
RUN wget -q https://bootstrap.pypa.io/get-pip.py && python3.11 get-pip.py && rm get-pip.py

# Install Asari and PCPFM Python packages
RUN python3.11 -m pip install --no-cache-dir asari-metabolomics pcpfm pandas

# Install Thermo RawFileParser for .RAW to .mzML conversion
RUN mkdir -p /usr/local/thermo && \
    wget -q -O /tmp/ThermoRawFileParser.zip https://github.com/compomics/ThermoRawFileParser/releases/download/v1.4.0/ThermoRawFileParser.zip && \
    unzip /tmp/ThermoRawFileParser.zip -d /usr/local/thermo && \
    rm /tmp/ThermoRawFileParser.zip

# Set working directory and copy pipeline scripts
WORKDIR /pipeline
COPY step0_mzML_convert.sh step1_combine_sequences.py step2_add_pcpfm_metadata.py step3_map_mzML.py step4_pcpfm_process.sh  step5_steroid_annotate.py ./
RUN chmod +x step0_mzML_convert.sh step4_pcpfm_process.sh

# Default command: start an interactive shell (can be overridden)
CMD ["bash"]