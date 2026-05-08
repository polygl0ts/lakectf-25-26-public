FROM ubuntu:24.04

# Based on https://github.com/laravel/sail/tree/1.x/runtimes/8.5
ARG WWWGROUP=1000
ARG NODE_VERSION=24
ARG MYSQL_CLIENT="mysql-client"
ARG POSTGRES_VERSION=18

WORKDIR /var/www/html

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
ENV LANG=C.UTF-8
ENV SUPERVISOR_PHP_COMMAND="/usr/bin/php -d variables_order=EGPCS /var/www/html/artisan serve --host=0.0.0.0 --port=80"
ENV SUPERVISOR_PHP_USER="sail"
ENV PLAYWRIGHT_BROWSERS_PATH=0

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN echo "Acquire::http::Pipeline-Depth 0;" > /etc/apt/apt.conf.d/99custom && \
    echo "Acquire::http::No-Cache true;" >> /etc/apt/apt.conf.d/99custom && \
    echo "Acquire::BrokenProxy    true;" >> /etc/apt/apt.conf.d/99custom

RUN apt-get update && apt-get upgrade -y \
    && mkdir -p /etc/apt/keyrings \
    && apt-get install -y gnupg gosu curl ca-certificates zip unzip git supervisor sqlite3 libcap2-bin libpng-dev python3 dnsutils librsvg2-bin fswatch ffmpeg nano  \
    && curl -sS 'https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xb8dc7e53946656efbce4c1dd71daeaab4ad4cab6' | gpg --dearmor | tee /etc/apt/keyrings/ppa_ondrej_php.gpg > /dev/null \
    && echo "deb [signed-by=/etc/apt/keyrings/ppa_ondrej_php.gpg] https://ppa.launchpadcontent.net/ondrej/php/ubuntu noble main" > /etc/apt/sources.list.d/ppa_ondrej_php.list \
    && apt-get update \
    && apt-get install -y \
        libgd3 \
        php8.5-cli \
        php8.5-dev \
        php8.5-pgsql \
        php8.5-sqlite3 \
        php8.5-gd \
        php8.5-curl \
        php8.5-mongodb \
        php8.5-imap \
        php8.5-mysql \
        php8.5-mbstring \
        php8.5-xml \
        php8.5-zip \
        php8.5-bcmath \
        php8.5-soap \
        php8.5-intl \
        php8.5-readline \
        php8.5-ldap \
        php8.5-msgpack \
        php8.5-igbinary \
        php8.5-redis \
        php8.5-swoole \
        php8.5-memcached \
        php8.5-pcov \
        php8.5-imagick \
        php8.5-xdebug \
    && curl -sLS https://getcomposer.org/installer | php -- --install-dir=/usr/bin/ --filename=composer \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_VERSION.x nodistro main" > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y nodejs \
    && npm install -g npm \
    && npm install -g pnpm \
    && npm install -g bun \
    && npx playwright install-deps \
    && corepack enable \
    && corepack prepare yarn@stable --activate \
    && curl -sS https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor | tee /etc/apt/keyrings/pgdg.gpg >/dev/null \
    && echo "deb [signed-by=/etc/apt/keyrings/pgdg.gpg] http://apt.postgresql.org/pub/repos/apt noble-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update \
    && apt-get install -y $MYSQL_CLIENT \
    && apt-get install -y postgresql-client-$POSTGRES_VERSION \
    && apt-get -y autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN setcap "cap_net_bind_service=+ep" /usr/bin/php8.5

RUN userdel -r ubuntu
RUN groupadd --force -g $WWWGROUP sail
RUN useradd -ms /bin/bash --no-user-group -g $WWWGROUP -u 1000 sail
RUN git config --global --add safe.directory /var/www/html

COPY sail/start-container /usr/local/bin/start-container
COPY sail/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY sail/php.ini /etc/php/8.5/cli/conf.d/99-sail.ini
RUN chmod +x /usr/local/bin/start-container

# UNIT3D installation

RUN curl -L https://codeload.github.com/HDInnovations/UNIT3D/zip/refs/tags/v9.2.0 -o /tmp/unit3d.zip \
    && unzip /tmp/unit3d.zip -d /tmp/ \
    && rm -rf /var/www/html \
    && mv /tmp/UNIT3D-9.2.0 /var/www/html \
    && rm -rf /tmp/unit3d.zip /tmp/UNIT3D-9.2.0

RUN chown -R sail:sail /var/www/html
RUN cp /var/www/html/.env.example /var/www/html/.env
RUN composer install --no-dev --optimize-autoloader --working-dir=/var/www/html
RUN rm /var/www/html/.env

RUN bun install
RUN bun run build

RUN chmod +x /var/www/html/artisan
COPY config/* /var/www/html/config/
COPY app/Actions/Fortify/CreateNewUser.php /var/www/html/app/Actions/Fortify/CreateNewUser.php
COPY app/Http/Controllers/TorrentDownloadController.php /var/www/html/app/Http/Controllers/TorrentDownloadController.php
COPY app/Http/Controllers/AnnounceController.php /var/www/html/app/Http/Controllers/AnnounceController.php
COPY app/Http/Kernel.php /var/www/html/app/Http/Kernel.php
COPY database/seeders/GroupSeeder.php /var/www/html/database/seeders/GroupSeeder.php
COPY database/seeders/UserSeeder.php /var/www/html/database/seeders/UserSeeder.php
COPY app/Providers/RouteServiceProvider.php /var/www/html/app/Providers/RouteServiceProvider.php
COPY app/Providers/FortifyServiceProvider.php /var/www/html/app/Providers/FortifyServiceProvider.php

EXPOSE 80/tcp

ENTRYPOINT ["start-container"]
