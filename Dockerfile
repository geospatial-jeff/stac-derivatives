FROM lambci/lambda:build-provided

ARG PYVERSION=3.6.0

# install Python
ENV \
    PYENV_ROOT=/root/.pyenv \
    PATH=/root/.pyenv/shims:/root/.pyenv/bin:$PATH

RUN \
    curl https://pyenv.run | bash; \
    pyenv install ${PYVERSION}; \
    pyenv global ${PYVERSION}; \
    pip install --upgrade pip


COPY requirements-sls.txt ./

RUN \
    pip install -r requirements-sls.txt

COPY bin/* /usr/local/bin/

RUN \
    chmod +x /usr/local/bin/package-service.sh

WORKDIR /home/stac_derivatives
