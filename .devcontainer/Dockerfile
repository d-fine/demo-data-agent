FROM mcr.microsoft.com/vscode/devcontainers/base:bookworm

WORKDIR /opt

# for vscode extensions and Zscaler MITM
ENV NODE_EXTRA_CA_CERTS="/etc/ssl/certs/ca-certificates.crt"

# install enterprise certificates (for Zscaler MITM)
COPY .devcontainer/certificates/ /usr/local/share/ca-certificates/
RUN update-ca-certificates

# install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.8 /uv /uvx /bin/

ENV PYTHONUNBUFFERED=True
ENV UV_LINK_MODE=copy
