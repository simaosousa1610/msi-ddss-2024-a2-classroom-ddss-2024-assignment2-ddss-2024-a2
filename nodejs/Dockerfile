#
# Authors: Nuno Antunes <nmsa@dei.uc.pt>, João Antunes <jcfa@dei.uc.pt>
#


FROM node:12-alpine
# If necessary to use a distro different from alpine
# please replace by the line below.
# FROM node:12.8.0



# Create app directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Bundle app source
COPY . /usr/src/app

# Install app dependencies
RUN npm install

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Start server
CMD ["npm", "run", "start"]