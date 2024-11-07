#
# Authors: Nuno Antunes <nmsa@dei.uc.pt>, João Antunes <jcfa@dei.uc.pt>
#

FROM maven:3-jdk-11-slim

COPY 	ddss-mvn /ddss-mvn
WORKDIR /ddss-mvn

# RUN sh build.sh
RUN mvn clean package

CMD ["sh", "/ddss-mvn/docker.sh"]


