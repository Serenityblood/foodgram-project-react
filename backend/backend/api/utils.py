import io

from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


def get_shopping_list(self, shopping_list):
    font = 'DejaVuSerif'
    pdfmetrics.registerFont(
        TTFont('DejaVuSerif', 'DejaVuSerif.ttf', 'UTF-8'))
    buffer = io.BytesIO()
    pdf_file = canvas.Canvas(buffer)
    pdf_file.setFont(font, 24)
    pdf_file.drawString(
        150,
        800,
        'Список покупок.'
    )
    pdf_file.setFont(font, 14)
    from_bottom = 750
    for number, ingredient in enumerate(shopping_list, start=1):
        pdf_file.drawString(
            50,
            from_bottom,
            f'{number}.  {ingredient["name"]} - {ingredient["amount"]} '
            f'{ingredient["unit"]}'
        )
        from_bottom -= 20
        if from_bottom <= 50:
            from_bottom = 800
            pdf_file.showPage()
            pdf_file.setFont(font, 14)
    pdf_file.showPage()
    pdf_file.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True,
                        filename='shopping_list.pdf')
