from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=150)
    is_primary = models.BooleanField(default=False, verbose_name="Principal")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name
