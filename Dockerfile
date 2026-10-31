FROM ubuntu:22.04

ENV HUGO_VERSION=0.147.9
ENV DART_SASS_VERSION=1.89.2
ENV NODE_VERSION=20

# Basis-Tools + Python
RUN apt-get update && apt-get install -y \
    wget git dpkg tar curl python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Node.js installieren (offizielles Repo)
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest

# Hugo installieren
RUN wget -O /tmp/hugo.deb https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.deb \
    && dpkg -i /tmp/hugo.deb \
    && rm /tmp/hugo.deb

# Dart Sass installieren
RUN wget -O /tmp/dart-sass.tar.gz https://github.com/sass/dart-sass/releases/download/${DART_SASS_VERSION}/dart-sass-${DART_SASS_VERSION}-linux-x64.tar.gz \
    && tar -xf /tmp/dart-sass.tar.gz -C /opt \
    && ln -s /opt/dart-sass/dart-sass /usr/local/bin/dart-sass \
    && rm /tmp/dart-sass.tar.gz

WORKDIR /site


# requirements.txt installieren, wenn vorhanden
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || true

CMD ["hugo", "server", "--bind", "0.0.0.0", "--baseURL", "http://localhost/", "--appendPort=false", "--disableFastRender"]
