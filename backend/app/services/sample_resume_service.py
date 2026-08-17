from io import BytesIO

from reportlab.pdfgen import (
    canvas,
)


def generate_sample_resume_pdf(
    name: str,
    email: str,
    headline: str,
    summary: str,
) -> bytes:

    buffer = BytesIO()

    pdf = canvas.Canvas(
        buffer
    )

    pdf.setTitle(
        f"{name} Resume"
    )

    pdf.setFont(
        "Helvetica-Bold",
        18,
    )

    pdf.drawString(
        72,
        750,
        name,
    )

    pdf.setFont(
        "Helvetica",
        11,
    )

    pdf.drawString(
        72,
        725,
        email,
    )

    pdf.setFont(
        "Helvetica-Bold",
        12,
    )

    pdf.drawString(
        72,
        690,
        headline
        or
        "Sample Candidate",
    )

    pdf.setFont(
        "Helvetica",
        10,
    )

    text = pdf.beginText(
        72,
        660,
    )

    text.textLine(
        "SkillBeacon Sample Resume"
    )

    text.textLine(
        summary
        or
        (
            "Generated automatically "
            "for sample-data testing."
        )
    )

    pdf.drawText(text)

    pdf.save()

    buffer.seek(0)

    return buffer.read()