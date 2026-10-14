FROM php:8.2-cli-bookworm

WORKDIR /app
COPY index.php help.html ui.html ./
RUN mkdir -p /app/state && chown www-data:www-data /app/state
USER www-data
EXPOSE 8080
CMD ["php", "-S", "0.0.0.0:8080", "index.php"]
