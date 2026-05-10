## Model downloads

The first run of `TranslateGemmaEngine` downloads the model weights and can pull several gigabytes
of data. Make sure the runtime environment has enough disk space and network access for that
initial bootstrap.

## Engine registration

`packages/stt/src/poly_stt/bootstrap.py` registers `whisper-local-base` by default when the worker
starts. If you change the default Whisper size, update the bootstrap settings and the worker
startup docs together.
