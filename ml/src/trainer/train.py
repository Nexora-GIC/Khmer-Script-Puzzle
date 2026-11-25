"""Only if evaluate.py says the models aren't good enough as they are.

Take a Hugging Face model's CNN encoder (it already knows Khmer strokes), drop its
line-reading head, add a small classifier (~64×64 image → ~80 piece scores), and train
briefly on piece images. Which model to start from is decided AFTER evaluation. Fine-tuning needs PyTorch weights:
  - mengheang/khmer-handwritten-ocr has them (safetensors; CC-BY-NC).
  - Chakkhu-OCR-Khmer-ONNX is ONNX only; the original muyleanging/Chakkhu-OCR-Khmer
    it was exported from may have them (not checked yet).
Images go through preprocess.load_image, the same as evaluate.py."""


def main():
    raise NotImplementedError


if __name__ == "__main__":
    main()
