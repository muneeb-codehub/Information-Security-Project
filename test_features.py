from src.features import extract_lexical_features, build_char_tokenizer, url_to_seq

urls = [
    "https://example.com/login",
    "http://192.168.0.1/admin",
    "http://very.suspicious-login.account-verify.example.co.uk/path?user=test"
]

for u in urls:
    print(u, "->", extract_lexical_features(u))

tok = build_char_tokenizer(urls)
print("Tokenizer vocab size:", len(tok.word_index))
print("Sequence shape:", url_to_seq(tok, urls[0], maxlen=64).shape)
