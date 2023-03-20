import base64
import io

from django.db.models import F, Sum
from django.core.files.base import ContentFile
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from rest_framework import serializers

from api.models import IngForRec


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


def get_shopping_list(self, request):
    user = request.user
    shopping_list = IngForRec.objects.filter(
        recipe__shopping_card__user=user).values(
        name=F('ingredient__name'),
        unit=F('ingredient__measurement_unit')
    ).annotate(amount=Sum('amount')).order_by()
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
