FROM quay.io/pypa/manylinux_2_28_x86_64

ENV PATH="/opt/python/cp313-cp313/bin:$PATH"
RUN /opt/python/cp313-cp313/bin/pip install --upgrade pip && pip install nuitka

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
RUN cd /opt/_internal && tar xf static-libs-for-embedding-only.tar.xz

COPY . /app

RUN nuitka --enable-plugin=pyside6 --output-file=rclone_explorer --windows-icon-from-ico=app/resources/favicon.ico --include-data-dir=app/resources=app/resources --include-data-dir=translations=translations --windows-console-mode=attach --product-name="Rclone Explorer" --product-version=1 --standalone main.py
