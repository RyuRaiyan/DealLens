from transformers import AutoTokenizer, AutoModelForCausalLM


MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"


print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

print("Loading model...")
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

messages = [
    {
        "role": "user",
        "content": "Explain what a vector database is in two sentences."
    }
]

text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)

inputs = tokenizer(
    text,
    return_tensors="pt"
)

print("Generating answer...")

outputs = model.generate(
    **inputs,
    max_new_tokens=100
)

generated_tokens = outputs[0][inputs["input_ids"].shape[-1]:]

answer = tokenizer.decode(
    generated_tokens,
    skip_special_tokens=True
)

print("\n--- LLM Answer ---")
print(answer)