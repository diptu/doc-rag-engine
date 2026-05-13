import fitz  # PyMuPDF
import os


def create_multipage_pdf(path: str):
    doc = fitz.open()

    # Page 1
    page1 = doc.new_page()
    page1.insert_text((72, 72), "This is page one")

    # Page 2
    page2 = doc.new_page()
    page2.insert_text((72, 72), "This is page two")

    doc.save(path)
    doc.close()


def create_single_page_pdf(path: str):
    doc = fitz.open()

    page = doc.new_page()
    page.insert_text((72, 72), "This is a single page document")

    doc.save(path)
    doc.close()


if __name__ == "__main__":
    os.makedirs("tests/files", exist_ok=True)

    create_multipage_pdf("tests/files/multipage.pdf")
    create_single_page_pdf("tests/files/single_page.pdf")

    print("✅ Sample PDFs created:")
    print("- tests/files/multipage.pdf")
    print("- tests/files/single_page.pdf")
