# Untested draft. onnxruntime_go needs cgo + libonnxruntime.so at runtime;
# keep ORT_VERSION in line with the onnxruntime_go version in go.mod.
FROM golang:1.26-bookworm AS build
ARG ORT_VERSION=1.22.0
WORKDIR /src
RUN curl -fsSL https://github.com/microsoft/onnxruntime/releases/download/v${ORT_VERSION}/onnxruntime-linux-x64-${ORT_VERSION}.tgz \
    | tar -xz -C /opt && mv /opt/onnxruntime-linux-x64-${ORT_VERSION} /opt/onnxruntime
COPY go.mod go.sum* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=1 go build -o /out/engine ./cmd/engine

FROM debian:bookworm-slim
COPY --from=build /opt/onnxruntime/lib/ /usr/local/lib/
RUN ldconfig
COPY --from=build /out/engine /usr/local/bin/engine
COPY models/ /app/models/
COPY content/ /app/content/
ENV MODEL_PATH=/app/models/model.onnx \
    CONTENT_PATH=/app/content/words.json \
    ENGINE_ADDR=:8080
EXPOSE 8080
ENTRYPOINT ["engine"]
