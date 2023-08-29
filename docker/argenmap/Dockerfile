# Use an official Apache image as the base image
FROM httpd:latest

# Install Git to clone the repository
RUN apt-get update && apt-get install -y git

# Clone the GitHub repository
RUN rm -rf /usr/local/apache2/htdocs/*
RUN git clone --depth 1 --branch v1.5.1 https://github.com/ign-argentina/argenmap.git /usr/local/apache2/htdocs/
COPY ./docker/argenmap/data.json /usr/local/apache2/htdocs/src/config/data.json
RUN chmod 755 /usr/local/apache2/htdocs/src/config/data.json

# Expose port 80 for the Apache server
EXPOSE 80
EXPOSE 443

# Start Apache server in the foreground
CMD ["httpd", "-D", "FOREGROUND"]
