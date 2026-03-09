from django.db import models


class DiseaseInfo(models.Model):
    """Database of diseases with information"""
    name = models.CharField(max_length=200, unique=True)
    short_description = models.TextField(blank=True, null=True)
    symptoms = models.TextField(blank=True, null=True, help_text='Comma-separated symptoms')
    treatment = models.TextField(blank=True, null=True)
    prevention = models.TextField(blank=True, null=True)
    severity = models.CharField(
        max_length=20,
        choices=[('mild', 'Mild'), ('moderate', 'Moderate'), ('severe', 'Severe')],
        default='mild'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Disease Info'
        verbose_name_plural = 'Disease Infos'
        ordering = ['name']

    def __str__(self):
        return self.name
