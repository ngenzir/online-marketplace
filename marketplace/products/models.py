from django.db import models

class Product():
	name = models.CharField(max_length=30)
	description = models.TextField()
	price = models.DecimalField(max_digits=100, decimal_places=2, default=19.99, null=True,)
	sale_active = models.BooleanField(default=False)
	sale_price = models.DecimalField(max_digits=100, decimal_places=2, default=12.99, null=True, blank=True)
	slug = models.SlugField(blank=True, unique=True)

	def __unicode__(self):
		return self.name

	def get_absolute_url(self):
		view_name = "product:detail_slug"
		return reverse(view_name, kwargs={"slug":self.slug})

