FROM ubuntu:22.04

# Set environment to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"] 
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y install python3 && \
    apt-get -y install python3-pip && \
    apt-get -y install python3-venv && \
    apt-get -y install unzip && \
    apt-get -y install curl && \
    apt-get -y install gnupg && \
    apt-get -y install wget && \ 
    apt-get -y install unixodbc && \
    apt-get -y install odbcinst && \
    dpkg --configure -a && \ 
    wget -qO /etc/apt/trusted.gpg.d/microsoft.asc https://packages.microsoft.com/keys/microsoft.asc && \
    curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN cat /etc/os-release
RUN curl -sSL -O https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb
RUN dpkg --force-confold -i packages-microsoft-prod.deb
RUN curl https://packages.microsoft.com/ubuntu/22.04/prod/pool/main/m/msodbcsql18/msodbcsql18_18.4.1.1-1_amd64.deb -o msodbcsql18.deb
RUN ACCEPT_EULA=Y dpkg --force-confold --install msodbcsql18.deb
RUN rm packages-microsoft-prod.deb
RUN apt-get -y update
#RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18
RUN wget -qO ./mssql-tools18.deb https://packages.microsoft.com/ubuntu/22.04/prod/pool/main/m/mssql-tools18/mssql-tools18_18.4.1.1-1_amd64.deb
RUN ACCEPT_EULA=Y dpkg --force-confold --install mssql-tools18.deb
#RUN ACCEPT_EULA=Y apt-get install -y mssql-tools18
RUN echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
RUN source ~/.bashrc 
RUN odbcinst -q -d
RUN cat /etc/odbcinst.ini
#RUN apt-get install -y unixodbc-dev

# ALSO install the ODBC driver manager
#RUN apt-get update && \
#    apt-get install -y --no-install-recommends \
#    unixodbc \
#    unixodbc-dev && \
#    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

# Verify ODBC installation and list available drivers
RUN echo "=== Available ODBC Drivers ===" && \
    odbcinst -q -d && \
    echo "=== ODBC configuration ===" && \
    odbcinst -j
    
# Create non-root user for security
RUN useradd -m -u 1000 flaskuser && chown -R flaskuser:flaskuser /app
USER flaskuser
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info"]