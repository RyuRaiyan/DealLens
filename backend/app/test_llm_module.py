from .llm import generate_answer


question = "What programming languages does the candidate know?"

context = """
The candidate is pursuing a B.Tech in Artificial Intelligence and Machine Learning.
Relevant coursework includes Machine Learning, Computer Vision, Graph Theory and
Optimisation, and Python.

The candidate also developed an E-Commerce website using Python and supporting APIs
for the backend.
"""


answer = generate_answer(
    question=question,
    context=context
)

print("\n--- Question ---")
print(question)

print("\n--- Generated Answer ---")
print(answer)