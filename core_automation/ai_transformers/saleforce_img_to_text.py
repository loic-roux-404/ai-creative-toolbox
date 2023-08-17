from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor


def image_to_text(img):
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained(
        "Salesforce/blip-image-captioning-base"
    )

    raw_image = Image.open(img).convert("RGB")

    # unconditional image captioning
    inputs = processor(raw_image, return_tensors="pt").input_ids

    out = model.generate(inputs, do_sample=True, top_p=0.84, top_k=100, max_length=20)

    return processor.decode(out[0])
