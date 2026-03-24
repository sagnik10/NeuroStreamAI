from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL = "facebook/nllb-200-distilled-600M"

tokenizer = AutoTokenizer.from_pretrained(MODEL)

model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL,
    tie_word_embeddings=False
)

LANGS = {
    "en": "eng_Latn",
    "he": "heb_Hebr",
    "fr": "fra_Latn",
    "es": "spa_Latn",
    "de": "deu_Latn",
    "it": "ita_Latn",
    "ru": "rus_Cyrl"
}


def detect_lang(text):
    if any("\u0590" <= c <= "\u05FF" for c in text):
        return "he"
    return "en"


def translate(text, src="auto", tgt="en"):
    if src == "auto":
        src = detect_lang(text)
    if src == tgt:
        return text

    src_code = LANGS.get(src, "eng_Latn")
    tgt_code = LANGS.get(tgt, "eng_Latn")

    tokenizer.src_lang = src_code
    tokens = tokenizer(text, return_tensors="pt")
    tgt_id = tokenizer.convert_tokens_to_ids(tgt_code)

    out = model.generate(
        **tokens,
        forced_bos_token_id=tgt_id,
        max_length=512
    )

    return tokenizer.decode(out[0], skip_special_tokens=True)