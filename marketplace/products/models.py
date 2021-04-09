
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.urls import reverse
from django.utils.text import slugify




from sellers.models import SellerAccount



def download_image_location(instance, filename):
	return "%s/%s" %(instance.slug, filename)


class Product(models.Model):
	seller = models.ForeignKey(SellerAccount, on_delete=models.CASCADE)
	images = models.ImageField(blank=True, null=True, upload_to=download_image_location, storage=FileSystemStorage())
	name = models.CharField(max_length=30)
	description = models.TextField()
	price = models.DecimalField(max_digits=100, decimal_places=2, default=19.99, null=True,)
	sale_active = models.BooleanField(default=False)
	sale_price = models.DecimalField(max_digits=100, decimal_places=2, default=12.99, null=True, blank=True)
	slug = models.SlugField(blank=True, unique=True)
	
	def __unicode__(self):
		return self.name

	def get_absolute_url(self):
		view_name = "products:detail_slug"
		return reverse(view_name, kwargs={"slug":self.slug})

	def get_edit_url(self):
		view_name = "sellers:product_edit"
		return reverse(view_name, kwargs={"pk":self.id})

	def get_download(self):
		view_name = "products:download_slug"
		url = reverse(view_name, kwargs={"slug": self.slug})
		return url


	@property
	def get_price(self):
		if self.sale_price and self.sale_active:
			return self.price

	def get_html_price(self):
		price = self.get_price
		if price ==self.sale_price:
			return "<p><span>%s</span> <span style='color:red;text-decoration:line-through;'>%s</span></p>" %(self.sale_price, self.price)

		else:
			return "<p>%<p>" %(self.price)

	

def create_slug(instance, new_slug=None):
	slug = slugify(instance.title)
	if new_slug is not None:
		slug = new_slug
	qs = Product.objects.filter(slug=slug)
	exits = qs.exits()
	if exists:
		new_slug = "%s-%s" %(slug, qs.first().id)
		return create_slug(instance, new_slug=new_slug)
	return slug

def product_pre_save_receiver(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = create_slug(instance)

pre_save.connect(product_pre_save_receiver, sender=Product)


