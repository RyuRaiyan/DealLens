import fitz

pdf_path = r"C:\Users\ryura\OneDrive\Desktop\ryuraiyan@gmail.com (1).pdf"

doc = fitz.open(pdf_path)

print("NUMBER OF PAGES:", len(doc))
print("=" * 80)

for page_number, page in enumerate(doc):
    print(f"\n========== PAGE {page_number + 1} ==========\n")

    normal = page.get_text("text")
    sorted_text = page.get_text("text", sort=True)

    print("----- NORMAL EXTRACTION -----")
    print(normal)

    print("\n----- SORTED EXTRACTION -----")
    print(sorted_text)

print("\n" + "=" * 80)