# Context is the accepted runtime tree, not repository source or a host build.
ARG BASE_IMAGE=debian:bookworm-20251020-slim@sha256:3fc563f538cf97e350bb04f43ad234c5b100aa602cced60cd36d482336d45fd5
FROM ${BASE_IMAGE}
ARG CNAF_COMMIT
ARG RUNTIME_TREE_DIGEST
LABEL org.opencontainers.image.title="Arxo CNAF MCP technical preview" \
      org.opencontainers.image.source="https://github.com/arxohq/arxo-cnaf" \
      org.opencontainers.image.revision="${CNAF_COMMIT}" \
      org.arxo.runtime.tree.digest="${RUNTIME_TREE_DIGEST}"
COPY --chown=65532:65532 runtime/ /opt/cnaf/runtime/
COPY --chmod=0555 mcp_entrypoint.sh /opt/cnaf/mcp_entrypoint.sh
COPY NOTICE /opt/cnaf/NOTICE
USER 65532:65532
WORKDIR /opt/cnaf/runtime
EXPOSE 8722
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD ["/opt/cnaf/mcp_entrypoint.sh", "healthcheck"]
ENTRYPOINT ["/opt/cnaf/mcp_entrypoint.sh"]
CMD ["http"]
