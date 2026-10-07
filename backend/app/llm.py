import time

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"

print("Loading LLM...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32
)

model.eval()

print("LLM loaded successfully.")


def generate_answer(question: str, context: str) -> str:
    """
    Generate a grounded answer using only the retrieved document context.
    """

    start_time = time.time()

    prompt = f"""
You are DealLens, a document analysis assistant.

Answer the user's question using ONLY the DOCUMENT CONTEXT.

STRICT RULES:

1. Use only information explicitly stated in the document.

2. Answer ONLY what the question asks.

3. Do not add related information just because it appears elsewhere
   in the retrieved context.

4. If the question asks "what workshops", "what technologies",
   "what skills", "what courses", "what features", etc., extract
   ONLY the items that directly answer that question.

5. Do not expand a list using other information from the document.

6. Do not infer relationships between sentences.

7. Do not combine separate activities into the answer unless the
   document explicitly connects them to the question.

8. Preserve the wording used in the document whenever possible.

9. When listing items, do not use vague phrases such as
    "and more", "etc.", or "and so on" if the retrieved context
    contains the specific items. List the explicitly supported items.

10. If the document does not contain enough information to answer
    the question, say exactly:

    "I could not find enough information in the document to answer this."
11. When the question asks specifically about workshops or seminars,
    prioritize sentences that explicitly contain the words
    "workshops" or "seminars".

12. If the document says "workshops and seminars ... including",
    extract the items that directly follow "including" from that
    statement. Do not add activities mentioned in earlier or later
    sentences.

13. Do not include choreography, direction, music composition,
    scriptwriting, or other activities merely because they appear
    near the workshop description unless the document explicitly
    identifies them as workshops or seminars.
14. Do not replace "etc." with phrases such as "and more".
    If the source uses "etc.", stop the list at the explicitly
    stated items.
IMPORTANT FOR EXTRACTION QUESTIONS:

If the document says something like:

"The club offers workshops and seminars ... including training
in voice modulation, acting, movement and use of space, stage design..."

and the user asks:

"What workshops does the club offer?"

answer only:

"Voice modulation, acting, movement and use of space, and stage design."

Do NOT add other activities mentioned elsewhere in the document.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""

    messages = [
        {
            "role": "user",
            "content": prompt
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

    with torch.inference_mode():
        outputs = model.generate(
    **inputs,
    max_new_tokens=100,
    do_sample=False,
    repetition_penalty=1.1
)

    generated_tokens = outputs[0][
        inputs["input_ids"].shape[-1]:
    ]

    answer = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True
    )

    elapsed = time.time() - start_time

    print(f"LLM generation completed in {elapsed:.2f} seconds.")

    return answer.strip()