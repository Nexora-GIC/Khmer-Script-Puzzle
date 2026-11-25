// Package recognize turns strokes into a 64×64 image (must match the ml repo's preprocess.py exactly — see testdata/preprocess_cases.json) and runs model.onnx via onnxruntime_go, limited to the pieces allowed in the slot.
package recognize
