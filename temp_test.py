from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

print("Loading NLLB model explicitly...")
tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M", src_lang="rus_Cyrl")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")

print("Processing text...")
text = "Привет, как дела?"
inputs = tokenizer(text, return_tensors="pt")
# kat_Geor is the language code for Georgian in NLLB
forced_bos_token_id = tokenizer.lang_code_to_id["kat_Geor"]

translated_tokens = model.generate(
    **inputs, 
    forced_bos_token_id=forced_bos_token_id, 
    max_length=100
)
translated_text = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
print(f"Translated: {translated_text}")
